# Imports
from ast import alias
import discord
from discord.ext import commands
# from discord.ext import menus
import wavelink
import sys
sys.path.append('../arpeggio/')
import builds
import utils

class Player(wavelink.Player):
    def __init__(self):
        super().__init__()
        self.queue = builds.Queue()

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
                                            password='youshallnotpass')
    
    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        print(f'Node: {node.identifier} is ready!')
    
    @commands.Cog.listener()
    async def on_wavelink_track_end(player, track, reason):
        track = player.queue.next()

        if track:
            await player.play(track)
    
    # async def get_tracks(self, query):
    #     '''
    #     searches a query and returns name, track object(s)
    #     can hand youtube playlists, in which case name will be the playlist name and multiple tracks will be returned
    #     '''
    #     if query.startswith('https://'): # if a specific link is given, load that instead of a ytsearch
    #         tracks = await self.bot.wavelink.get_tracks(query)
        
    #     else:
    #         tracks = await self.bot.wavelink.get_tracks(f"ytsearch:{query}")

    #     if not tracks:
    #         raise Exception("NoResults")
        
    #     if isinstance(tracks, wavelink.player.TrackPlaylist):
    #         return tracks.data['playlistInfo']['name'], tracks.tracks # playlist name, playlist content
    #     else:
    #         return str(tracks[0]), [tracks[0]]

    # check if command author is in the bot's VC, and throw error if no
    def author_in_vc(self, ctx):
        vc: Player = ctx.voice_client
        try: 
            member_ids = [member.id for member in self.bot.get_channel(vc.channel.id).members]
        except AttributeError:
            raise Exception("NotInSameVoice")
        if not ctx.author.id in member_ids:
            raise Exception("NotInSameVoice")
    
    # @commands.command(aliases=['join', 'j'])
    # async def connect(self, ctx):
    #     if not hasattr(ctx.author.voice, 'channel'):
    #         raise Exception("NoChannel")
    #     channel = ctx.author.voice.channel

    #     if player.channel_id == channel.id:
    #         raise Exception("AlreadyConnected")
    #     elif player.channel_id and len(self.bot.get_channel(player.channel_id).members) > 1:
    #         raise Exception("StealingBot")
        
    #     if not ctx.voice_client:
    #         vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
    #     else:
    #         vc: wavelink.Player = ctx.voice_client
        
    #     await ctx.send(embed=utils.embed(f"Connecting to **{channel.name}**", emoji="satellite"))
    #     player: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)

    #     await player.set_pause(False)
    #     await ctx.guild.change_voice_state(channel=channel, self_deaf=True) # you're welcome skye

    #     return player

    @commands.command(aliases=['join', 'j'])
    async def connect(self, ctx: commands.Context):
        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            raise Exception('NoChannel')

        if not ctx.voice_client:
            vc: Player = await channel.connect(cls=Player())
        else:
            vc: Player = ctx.voice_client
        return vc
    
    @commands.command(aliases=['leave', 'l'])
    async def disconnect(self, ctx):
        vc: wavelink.Player = ctx.voice_client

        if len(self.bot.get_channel(vc.channel_id).members) > 1: # if bot is alone it's ok
            self.author_in_vc(ctx)

        await vc.disconnect()
        await ctx.message.add_reaction('👋')

    # @commands.command(aliases=['p'])
    # async def play(self, ctx, *, query:str=None):
    #     if not query:
    #         raise Exception("NoQuery")
        
    #     vc = await ctx.invoke(self.connect)

    #     self.author_in_vc(ctx)
        
    #     await ctx.send(embed=utils.embed(f"Searching ` {query} `", emoji='mag_right'))

    #     pre = query.split(':')[0].lower()
    #     if pre in ["sc" , "soundcloud"]:
    #         track = await wavelink.SoundCloudTrack.search(query=query)
    #     elif pre in ["sp" | "spotify"]:
    #         ... # spotify implementation
    #     else:
    #         track = await wavelink.YouTubeTrack.search(query=query, return_first=True)

    #     if vc.queue.is_empty():
    #         await vc.play(track)
    #         await ctx.send(embed=utils.embed(f"Playing __{track}__", emoji="cd"))
    #         await vc.set_pause(False)
    #     else:
    #         await ctx.send(embed=utils.embed(f"Added __{track}__ to the queue", emoji="pencil"))

    #     track.info['requester'] = ctx.author.mention
        
    #     vc.queue.add(track)

    #     if len(vc.queue.tracks) + len(track) > 100:
    #         await ctx.send(embed=utils.embed("There can be a maximum of 100 tracks in the queue!", color=(90, 160, 230), emoji='info'))

    @commands.command(aliases=['p'])
    async def play(self, ctx: commands.Context, *, search):
        """Play a song with the given search query.
        If not connected, connect to our voice channel.
        """
        if not ctx.voice_client:
            vc: Player = await ctx.author.voice.channel.connect(cls=Player)
        else:
            vc: Player = ctx.voice_client

        # process different track sources
        search_prefix = search.split(':')[0].lower()
        if search_prefix=='sc':
            await ctx.send(embed=utils.embed(f"Searching ` {search} ` on SoundCloud", emoji='mag_right'))
            partial = wavelink.PartialTrack(query=search.split(':')[1], cls=wavelink.SoundCloudTrack)
        elif search_prefix=='sp':
            raise "Spotify tracks are not supported yet"
        else:
            await ctx.send(embed=utils.embed(f"Searching ` {search} ` on YouTube", emoji='mag_right'))
            partial = wavelink.PartialTrack(query=search, cls=wavelink.YouTubeTrack)

        # add to queue or play
        if vc.queue.is_empty():
            track = await vc.play(partial)
            await ctx.send(embed=utils.embed(f"Now playing [{track.title}]({track.uri})", emoji="cd"))
            await vc.set_pause(False)
        else:
            await ctx.send(embed=utils.embed(f"Added [{track.title}]({track.uri}) to the queue", emoji="pencil"))
        
        vc.queue.add(partial)

    @commands.command(aliases=['q'])
    async def queue(self, ctx, page: int = 1):
        vc: Player = ctx.voice_client

        if vc.queue.is_empty():
            raise Exception("QueueEmpty")

        await ctx.send(vc.embed(vc, page))
    
    @commands.command()
    async def loop(self, ctx):
        '''
        enables the player's looping feature
        '''
        self.author_in_vc(ctx)
        vc: Player = ctx.voice_client

        vc.queue.looping = True
        await ctx.message.add_reaction('🔁')
    
    @commands.command()
    async def unloop(self, ctx):
        '''
        disables the player's looping
        '''
        self.author_in_vc(ctx)
        vc: Player = ctx.voice_client

        vc.queue.looping = False
        vc.queue.history = []
        await ctx.message.add_reaction('✅')
    
    @commands.command(aliases=['tl'])
    async def toggle_loop(self, ctx):
        self.author_in_vc(ctx)
        vc: Player = ctx.voice_client

        if vc.queue.looping:
            await ctx.invoke(self.unloop)
        else:
            await ctx.invoke(self.loop)
    
    @commands.command()
    async def pause(self, ctx):
        self.author_in_vc(ctx)
        vc: Player = ctx.voice_client

        await vc.set_pause(True)
        await ctx.message.add_reaction('⏸')

    @commands.command(aliases=['res'])
    async def resume(self, ctx):
        self.author_in_vc(ctx)
        vc: Player = ctx.voice_client

        await vc.set_pause(False)
        await ctx.message.add_reaction('▶')
    
    @commands.command(aliases=['tp'])
    async def toggle_pause(self, ctx):
        self.author_in_vc(ctx)
        vc: Player = ctx.voice_client

        if vc.is_paused:
            await ctx.invoke(self.resume)
        else:
            await ctx.invoke(self.pause)
    
    @commands.command() # clear queue and history, stop player
    async def stop(self, ctx):
        self.author_in_vc(ctx)
        vc: Player = ctx.voice_client

        vc.queue.tracks = []
        vc.queue.history = []
        vc.queue.looping = False
        await vc.stop()

        await ctx.message.add_reaction('⏹')
    
    @commands.command()
    async def clear(self, ctx):
        self.author_in_vc(ctx)
        vc: Player = ctx.voice_client

        vc.queue.clear()
        await ctx.message.add_reaction('✅')
    
    @commands.command(aliases=['nowplaying', 'now_playing'])
    async def current(self, ctx):
        vc: Player = ctx.voice_client

        current = vc.queue.current()

        await ctx.send(embed=utils.embed(
            f"[{str(current)}]({current.uri})"
        ))
    
    @commands.command()
    async def seek(self, ctx, pos='0'):
        self.author_in_vc(ctx)
        vc: Player = ctx.voice_client

        await vc.seek(min(utils.parse_time(pos), vc.queue.current().length)) # make sure position isn't past the length of the song
        await ctx.message.add_reaction('↔️')
    
    @commands.command()
    async def skip(self, ctx):
        self.author_in_vc(ctx)
        vc: Player = ctx.voice_client

        if vc.queue.is_empty():
            raise Exception("QueueEmpty")
        
        await vc.stop()
        await ctx.message.add_reaction('⏩')
        
        if len(vc.queue.tracks) > 0:
            next = vc.queue.current()
            await ctx.send(embed=utils.embed(f"Playing [{str(next)}]({next.uri})", emoji="cd"))
    
    @commands.command()
    async def restart(self, ctx):
        self.author_in_vc(ctx)
        vc: Player = ctx.voice_client

        await vc.seek(0)
        vc.set_pause(False)
        await ctx.message.add_reaction('⏪')
    
    @commands.command()
    async def remove(self, ctx, i=-1):
        self.author_in_vc(ctx)
        vc: Player = ctx.voice_client

        if i == 0:
            raise Exception("TargetCurrentTrack")

        try:
            vc.queue.delete(int(i))
        except IndexError:
            raise Exception("IndexError")
        await ctx.message.add_reaction('✅')

    @commands.command()
    async def move(self, ctx, i:int, f:int):
        self.author_in_vc(ctx)
        vc: Player = ctx.voice_client

        if len(vc.queue.tracks) < 3:
            raise Exception("NotEnoughTracks")

        try:
            vc.queue.move(i, f)
        except IndexError:
            raise Exception("IndexError")
        await ctx.message.add_reaction('✅')

    @commands.command()
    async def shuffle(self, ctx):
        self.author_in_vc(ctx)
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