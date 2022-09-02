# Imports
import discord
from discord.ext import commands
import asyncio
# from discord.ext import menus
import wavelink
from wavelink.ext import spotify
import sys
sys.path.append('../arpeggio/')
import builds
import utils
import json

class Player(wavelink.Player):
    def __init__(self):
        super().__init__()
        self.queue = builds.Queue(vc=self)
        self.request_channel = None

with open('../tokens.json', 'r') as f:
    tokens = json.load(f)
SPOTIFY_SECRET = tokens['spotify']

# Cog
class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.start_nodes())
    
    async def start_nodes(self):
        await self.bot.wait_until_ready()
        await wavelink.NodePool.create_node(bot=self.bot,
                                            host='0.0.0.0',
                                            port=2333,
                                            password='youshallnotpass',
                                            spotify_client=spotify.SpotifyClient(client_id="b4729e0a7b144f44bfda14a3111cf016", client_secret=SPOTIFY_SECRET))
    
    async def player_timeout(self, player):
        await asyncio.sleep(10)
        if not player.queue.is_empty():
            return
        if len(player.channel.members) > 1: # channel has members, wait another 5 mins
            return self.player_timeout(player)
        await player.disconnect()
        player.cleanup()
    
    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        print(f'Node: {node.identifier} is ready!')
    
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player:wavelink.Player, track, reason):
        if not player.channel:
            await player.stop()
            player.cleanup()

        nexttrack = player.queue.next()
        if nexttrack:
            await player.play(nexttrack)
            if player.request_channel:
                await player.request_channel.send(embed=utils.embed(f"Now playing [{nexttrack.title}]({nexttrack.uri})", emoji="cd"))
        else:
            self.bot.loop.create_task(self.player_timeout(player)) # wait 5 mins before leaving if the bot isn't playing anything
        
    @commands.command()
    async def disconnect_all_players(self, ctx):
        for guild in self.bot.guilds: # disconnect all player clients
            vc: Player = guild.voice_client
            if vc:
                await vc.disconnect()
    
    @commands.command()
    @utils.whitelisted()
    async def set_channel(self, ctx:commands.Context):
        vc: Player = ctx.voice_client
        vc.request_channel = ctx.channel
        await ctx.message.add_reaction('✅')
    
    @commands.command(aliases=['join', 'j'])
    @utils.whitelisted()
    async def connect(self, ctx: commands.Context, force=None):
        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            raise Exception('NoChannel')

        if not ctx.voice_client:
            vc: Player = await channel.connect(cls=Player())
        else:
            vc: Player = ctx.voice_client
            if self.bot.user in ctx.author.voice.channel.members and force != "force":
                raise Exception("AlreadyConnected")
            if len(vc.channel.members) > 1 and ctx.author not in vc.channel.members and force != "force":
                raise Exception("StealingBot")
            await vc.disconnect()
            vc: Player = await channel.connect(cls=Player())

        bot_member = ctx.guild.get_member(self.bot.user.id)
        await bot_member.edit(deafen=True)

        vc.request_channel = ctx.channel

        return vc
    

    @commands.command(aliases=['leave', 'l'])
    @utils.whitelisted()
    async def disconnect(self, ctx):
        vc: Player = ctx.voice_client

        await vc.disconnect()
        vc.cleanup()
        await ctx.message.add_reaction('👋')

    @commands.command(aliases=['p'])
    @utils.whitelisted()
    async def play(self, ctx: commands.Context, *, search:str):
        """Play a song with the given search query.
        If not connected, connect to the user's voice channel.
        """
        try: 
            if self.bot.user not in ctx.author.voice.channel.members:
                vc: Player = await ctx.invoke(self.connect)
            else:
                vc: Player = ctx.voice_client
        except Exception:
            pass

        playlist = None
        
        if not search:
            raise Exception("NoQuery")

        # process different track sources
        search_prefix = search.split(':')[0].lower()
        if search_prefix=='sc' or search.startswith("https://soundcloud.com/"):
            await ctx.send(embed=utils.embed(f"Searching ` {(search[3:] if search_prefix=='sc' else search[23:])} ` on **SoundCloud**", emoji='mag_right'))
            tracks = await wavelink.SoundCloudTrack.search(query=(search[3:] if search_prefix=='sc' else search[23:]))
            if not tracks:
                raise Exception("NoResults")
            to_play = tracks[0]

        elif search.startswith("https://open.spotify.com"):
            decoded = spotify.decode_url(search)
            if not decoded:
                raise Exception("SpotifyParsingError")

            await ctx.send(embed=utils.embed(f"Searching ` {search} ` on **Spotify**", emoji='mag_right'))

            if decoded['type'] == spotify.SpotifySearchType.track:
                tracks = await spotify.SpotifyTrack.search(query=decoded['id'], type=spotify.SpotifySearchType.track, return_first=True) # spotify tracks
                to_play = tracks
                tracks = [tracks]
            else:
                tracks = await spotify.SpotifyTrack.search(query=decoded['id'], type=decoded['type'], return_first=True) # albums or playlists
                to_play = tracks[0]

        else:
            await ctx.send(embed=utils.embed(f"Searching ` {search} ` on **YouTube**", emoji='mag_right'))
            tracks = await wavelink.YouTubeTrack.search(query=search)
            if not tracks:
                raise Exception("NoResults")
                
            if isinstance(tracks, wavelink.YouTubePlaylist):
                playlist = tracks.name, search
                to_play = tracks.tracks[0]
                tracks = tracks.tracks
            else:
                to_play = tracks[0]
                tracks = [tracks[0]]

        # add to queue or play
        if vc.queue.is_empty():
            await vc.play(to_play)
            await ctx.send(embed=utils.embed(f"Now playing [{to_play.title}]({to_play.uri})", emoji="cd"))
            await vc.set_pause(False)
        elif not playlist:
            await ctx.send(embed=utils.embed(f"Added [{to_play.title}]({to_play.uri}) to the queue", emoji="pencil"))
        
        if playlist:
            await ctx.send(embed=utils.embed(f"Added [{playlist[0]}]({playlist[1]}) to the queue", emoji="pencil"))

        for track in tracks:
            track.info['requester'] = ctx.author.mention

        vc.queue.add(tracks)

    @commands.command(aliases=['q'])
    async def queue(self, ctx, page: int = 1):
        vc: Player = ctx.voice_client

        if not vc or vc.queue.is_empty():
            raise Exception("QueueEmpty")

        await ctx.send(embed=vc.queue.embed(page))
    
    @commands.command()
    @utils.whitelisted()
    async def loop(self, ctx):
        '''
        enables the player's looping feature
        '''
        vc: Player = ctx.voice_client

        vc.queue.looping = True
        await ctx.message.add_reaction('🔁')
    
    @commands.command()
    @utils.whitelisted()
    async def unloop(self, ctx):
        '''
        disables the player's looping
        '''
        vc: Player = ctx.voice_client

        vc.queue.looping = False
        vc.queue.history = []
        await ctx.message.add_reaction('✅')
    
    @commands.command(aliases=['tl'])
    @utils.whitelisted()
    async def toggle_loop(self, ctx):
        vc: Player = ctx.voice_client

        if vc.queue.looping:
            await ctx.invoke(self.unloop)
        else:
            await ctx.invoke(self.loop)
    
    @commands.command()
    @utils.whitelisted()
    async def pause(self, ctx):
        vc: Player = ctx.voice_client

        await vc.set_pause(True)
        await ctx.message.add_reaction('⏸')

    @commands.command(aliases=['res'])
    @utils.whitelisted()
    async def resume(self, ctx):
        vc: Player = ctx.voice_client

        await vc.set_pause(False)
        await ctx.message.add_reaction('▶')
    
    @commands.command(aliases=['tp'])
    @utils.whitelisted()
    async def toggle_pause(self, ctx):
        vc: Player = ctx.voice_client

        if vc.is_paused():
            await ctx.invoke(self.resume)
        else:
            await ctx.invoke(self.pause)
    
    @commands.command() # clear queue and history, stop player, disconnect
    @utils.whitelisted()
    async def stop(self, ctx):
        vc: Player = ctx.voice_client

        vc.queue.tracks = []
        vc.queue.history = []
        vc.queue.looping = False
        await vc.stop()

        await ctx.message.add_reaction('⏹️')
    
    @commands.command()
    @utils.whitelisted()
    async def kill(self, ctx):
        await ctx.invoke(self.stop)
        await ctx.invoke(self.disconnect)
    
    @commands.command()
    @utils.whitelisted()
    async def clear(self, ctx):
        vc: Player = ctx.voice_client

        vc.queue.clear()
        await ctx.message.add_reaction('✅')
    
    @commands.command(aliases=['nowplaying', 'now_playing'])
    @utils.whitelisted()
    async def current(self, ctx):
        vc: Player = ctx.voice_client

        current = vc.queue.current()

        await ctx.send(embed=utils.embed(
            f"[{str(current)}]({current.uri})"
        ))
    
    @commands.command()
    @utils.whitelisted()
    async def seek(self, ctx, pos='0'):
        vc: Player = ctx.voice_client

        await vc.seek(
            min( # make sure position isn't past the length of the song
                utils.parse_time(pos), 
                vc.queue.current().length*1000
            )
        )
        await ctx.message.add_reaction('↔️')
    
    @commands.command(aliases=["next"])
    @utils.whitelisted()
    async def skip(self, ctx):
        vc: Player = ctx.voice_client

        if vc.queue.is_empty():
            raise Exception("QueueEmpty")
        
        await vc.stop()
        await ctx.message.add_reaction('⏩')
    
    @commands.command()
    @utils.whitelisted()
    async def restart(self, ctx):
        vc: Player = ctx.voice_client

        await vc.seek(0)
        ctx.invoke(self.resume)
        await ctx.message.add_reaction('⏪')
    
    @commands.command(aliases=['rm'])
    @utils.whitelisted()
    async def remove(self, ctx, i=-1):
        vc: Player = ctx.voice_client

        if i == 0:
            raise Exception("TargetCurrentTrack")

        try:
            vc.queue.delete(int(i))
        except IndexError:
            raise Exception("IndexError")
        await ctx.message.add_reaction('✅')

    @commands.command()
    @utils.whitelisted()
    async def move(self, ctx, i:int, f:int):
        vc: Player = ctx.voice_client

        if len(vc.queue.tracks) < 3:
            raise Exception("NotEnoughTracks")

        try:
            vc.queue.move(i, f)
        except IndexError:
            raise Exception("IndexError")
        await ctx.message.add_reaction('✅')

    @commands.command()
    @utils.whitelisted()
    async def shuffle(self, ctx):
        vc: Player = ctx.voice_client

        if vc.queue.len < 3:
            raise Exception("NotEnoughTracks")
        vc.queue.shuffle()
        await ctx.message.add_reaction('🔀')


def setup(bot):
    try:
        bot.add_cog(Music(bot))
    except Exception as ex:
        print(ex)
        print(ex.message)