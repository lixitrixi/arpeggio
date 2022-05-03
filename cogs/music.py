# Imports
import discord
from discord.ext import commands
# from discord.ext import menus
import wavelink
from wavelink.ext import spotify
import sys
sys.path.append('../arpeggio/')
import builds
import utils

class Player(wavelink.Player):
    def __init__(self):
        super().__init__()
        self.queue = builds.Queue(vc=self)

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
                                            spotify_client=spotify.SpotifyClient(client_id="b4729e0a7b144f44bfda14a3111cf016", client_secret="2b2403ab693446a2bf3ef5f7221b77c2"))
    
    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        print(f'Node: {node.identifier} is ready!')
    
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player, track, reason):
        track = player.queue.next()

        if track:
            await player.play(track)
    
    def author_in_vc(self, ctx):
        vc: Player = ctx.voice_client
        try: 
            member_ids = [member.id for member in self.bot.get_channel(vc.channel.id).members]
        except AttributeError:
            raise Exception("NotInSameVoice")
        if not ctx.author.id in member_ids:
            raise Exception("NotInSameVoice")
    
    @commands.command()
    async def disconnect_all_players(self, ctx):
        for guild in self.bot.guilds: # disconnect all player clients
            vc: Player = guild.voice_client
            await vc.disconnect()

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
            if vc.channel.id == ctx.author.voice.channel.id:
                raise Exception("AlreadyConnected")
            if len(vc.channel.members) > 1 and ctx.author.id not in [m.id for m in vc.channel.members]:
                raise Exception("StealingBot")
            await vc.disconnect()
            vc: Player = await channel.connect(cls=Player())

        client = ctx.guild.voice_client
        if client:
            channel = client.channel
            await client.main_ws.voice_state(ctx.guild.id, channel.id, self_deafen=True)

        return vc
    
    @commands.command(aliases=['leave', 'l'])
    async def disconnect(self, ctx):
        vc: wavelink.Player = ctx.voice_client

        if len(self.bot.get_channel(vc.channel.id).members) > 1: # if bot is alone it's ok
            self.author_in_vc(ctx)

        await vc.disconnect()
        await ctx.message.add_reaction('👋')

    @commands.command(aliases=['p'])
    async def play(self, ctx: commands.Context, *, search):
        """Play a song with the given search query.
        If not connected, connect to the user's voice channel.
        """
        if not search:
            raise Exception("NoQuery")

        if not ctx.voice_client:
            vc: Player = await ctx.invoke(self.connect)
        else:
            vc: Player = ctx.voice_client

        # process different track sources
        search_prefix = search.split(':')[0].lower()
        if search_prefix=='sc':
            await ctx.send(embed=utils.embed(f"Searching ` {search[3:]} ` on SoundCloud", emoji='mag_right'))
            tracks = await wavelink.SoundCloudTrack.search(query=search[3:])
            if not tracks:
                raise Exception("NoResults")
            track = tracks[0]
        elif search_prefix=='sp':
            await ctx.send(embed=utils.embed(f"Searching ` {search[3:]} ` on Spotify", emoji='mag_right'))
            tracks = await spotify.SpotifyTrack.search(query=search[3:])
            if not tracks:
                raise Exception("NoResults")
            track = tracks[0]
        else:
            await ctx.send(embed=utils.embed(f"Searching ` {search} ` on YouTube", emoji='mag_right'))
            tracks = await wavelink.YouTubeTrack.search(query=search)
            if not tracks:
                raise Exception("NoResults")
            track = tracks[0]

        if not track:
            raise Exception("NoResults")

        # add to queue or play
        if vc.queue.is_empty():
            await vc.play(track)
            await ctx.send(embed=utils.embed(f"Now playing [{track.title}]({track.uri})", emoji="cd"))
            await vc.set_pause(False)
        else:
            await ctx.send(embed=utils.embed(f"Added [{track.title}]({track.uri}) to the queue", emoji="pencil"))

        track.info['requester'] = ctx.author.mention

        vc.queue.add([track])

    @commands.command(aliases=['q'])
    async def queue(self, ctx, page: int = 1):
        vc: Player = ctx.voice_client

        if not vc or vc.queue.is_empty():
            raise Exception("QueueEmpty")

        await ctx.send(embed=vc.queue.embed(page))
    
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
    
    @commands.command() # clear queue and history, stop player, disconnect
    async def stop(self, ctx):
        self.author_in_vc(ctx)
        vc: Player = ctx.voice_client

        vc.queue.tracks = []
        vc.queue.history = []
        vc.queue.looping = False
        await vc.stop()

        await ctx.message.add_reaction('⏹️')
    
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