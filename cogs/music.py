# Imports
import discord
from discord.ext import commands
# from discord.ext import menus
import wavelink
import builds
import utils

class Player(wavelink.Player):
    def __init__(self):
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
    async def on_wavelink_track_end(node: wavelink.Node):
        print(f"Node {node.id} is ready!")
    
    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        print(f'Node: <{node.identifier}> is ready!')
    
    @commands.Cog.listener()
    async def on_wavelink_track_end(player, track, reason):
        player = player

        track = player.queue.next()

        if track:
            await player.play(track)
    
    async def get_tracks(self, query):
        '''
        searches a query and returns name, track object(s)
        can hand youtube playlists, in which case name will be the playlist name and multiple tracks will be returned
        '''
        if query.startswith('https://'): # if a specific link is given, load that instead of a ytsearch
            tracks = await self.bot.wavelink.get_tracks(query)
        
        else:
            tracks = await self.bot.wavelink.get_tracks(f"ytsearch:{query}")

        if not tracks:
            raise Exception("NoResults")
        
        if isinstance(tracks, wavelink.player.TrackPlaylist):
            return tracks.data['playlistInfo']['name'], tracks.tracks # playlist name, playlist content
        else:
            return str(tracks[0]), [tracks[0]]

    # check if command author is in the bot's VC, and throw error if no
    def author_in_vc(self, ctx):
        vc = ctx.guild.voice_client
        try: 
            member_ids = [member.id for member in self.bot.get_channel(vc.channel_id).members]
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
            channel = channel or ctx.author.channel.voice
        except AttributeError:
            raise Exception('NoChannel')

        vc: Player = await channel.connect(cls=Player())
        return vc
    
    @commands.command(aliases=['leave', 'l'])
    async def disconnect(self, ctx):
        vc: Player = ctx.voice_client

        if len(self.bot.get_channel(vc.channel_id).members) > 1: # if bot is alone it's ok
            self.author_in_vc(ctx)

        await vc.disconnect()
        await ctx.message.add_reaction('👋')

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, query:str=None):
        if not query:
            raise Exception("NoQuery")
        
        vc = await ctx.invoke(self.connect)

        self.author_in_vc(ctx)
        
        await ctx.send(embed=utils.embed(f"Searching ` {query} `", emoji='mag_right'))

        match query.split(':')[0].lower():
            case "sc" | "soundcloud":
                track = await wavelink.SoundCloudTrack.search(query=query)
            case "sp" | "spotify":
                ... # spotify implementation
            case _:
                track = await wavelink.YouTubeTrack.search(query=query, return_first=True)

        if vc.queue.is_empty():
            await vc.play(track)
            await ctx.send(embed=utils.embed(f"Playing __{track}__", emoji="cd"))
            await vc.set_pause(False)
        else:
            await ctx.send(embed=utils.embed(f"Added __{track}__ to the queue", emoji="pencil"))

        track.info['requester'] = ctx.author.mention
        
        vc.queue.add(track)

        if len(vc.queue.tracks) + len(track) > 100:
            await ctx.send(embed=utils.embed("There can be a maximum of 100 tracks in the queue!", color=(90, 160, 230), emoji='info'))

    @commands.command(aliases=['q'])
    async def queue(self, ctx, page: int = 1):
        player = self.get_player(ctx.guild.id)

        if player.queue.is_empty():
            raise Exception("QueueEmpty")
    
    @commands.command()
    async def loop(self, ctx):
        '''
        enables the player's looping feature
        '''
        self.author_in_vc(ctx)
        player = self.get_player(ctx.guild.id)

        player.queue.looping = True
        await ctx.message.add_reaction('🔁')
    
    @commands.command()
    async def unloop(self, ctx):
        '''
        disables the player's looping
        '''
        self.author_in_vc(ctx)
        player = self.get_player(ctx.guild.id)

        player.queue.looping = False
        player.queue.history = []
        await ctx.message.add_reaction('✅')
    
    @commands.command(aliases=['tl'])
    async def toggle_loop(self, ctx):
        self.author_in_vc(ctx)
        player = self.get_player(ctx.guild.id)

        if player.queue.looping:
            await ctx.invoke(self.unloop)
        else:
            await ctx.invoke(self.loop)
    
    @commands.command()
    async def pause(self, ctx):
        self.author_in_vc(ctx)
        player = self.get_player(ctx.guild.id)

        await player.set_pause(True)
        await ctx.message.add_reaction('⏸')

    @commands.command(aliases=['res'])
    async def resume(self, ctx):
        self.author_in_vc(ctx)
        player = self.get_player(ctx.guild.id)

        await player.set_pause(False)
        await ctx.message.add_reaction('▶')
    
    @commands.command(aliases=['tp'])
    async def toggle_pause(self, ctx):
        self.author_in_vc(ctx)
        player = self.get_player(ctx.guild.id)

        if player.is_paused:
            await ctx.invoke(self.resume)
        else:
            await ctx.invoke(self.pause)
    
    @commands.command() # clear queue and history, stop player
    async def stop(self, ctx):
        self.author_in_vc(ctx)
        player = self.get_player(ctx.guild.id)

        player.queue.tracks = []
        player.queue.history = []
        player.queue.looping = False
        await player.stop()

        await ctx.message.add_reaction('⏹')
    
    @commands.command()
    async def clear(self, ctx):
        self.author_in_vc(ctx)
        player = self.get_player(ctx.guild.id)

        player.queue.clear()
        await ctx.message.add_reaction('✅')
    
    @commands.command(aliases=['nowplaying', 'now_playing'])
    async def current(self, ctx):
        player = self.get_player(ctx.guild.id)

        current = player.queue.current()

        await ctx.send(embed=utils.embed(
            f"[{str(current)}]({current.uri})"
        ))
    
    @commands.command()
    async def seek(self, ctx, pos='0'):
        self.author_in_vc(ctx)
        player = self.get_player(ctx.guild.id)

        await player.seek(min(utils.parse_time(pos), player.queue.current().length)) # make sure position isn't past the length of the song
        await ctx.message.add_reaction('↔️')
    
    @commands.command()
    async def skip(self, ctx):
        self.author_in_vc(ctx)
        player = self.get_player(ctx.guild.id)

        if player.queue.is_empty():
            raise Exception("QueueEmpty")
        
        await player.stop()
        await ctx.message.add_reaction('⏩')
        
        if len(player.queue.tracks) > 0:
            next = player.queue.current()
            await ctx.send(embed=utils.embed(f"Playing [{str(next)}]({next.uri})", emoji="cd"))
    
    @commands.command()
    async def restart(self, ctx):
        self.author_in_vc(ctx)
        player = self.get_player(ctx.guild.id)

        await player.seek(0)
        player.set_pause(False)
        await ctx.message.add_reaction('⏪')
    
    @commands.command()
    async def remove(self, ctx, i=-1):
        self.author_in_vc(ctx)
        player = self.get_player(ctx.guild.id)

        if i == 0:
            raise Exception("TargetCurrentTrack")

        try:
            player.queue.delete(int(i))
        except IndexError:
            raise Exception("IndexError")
        await ctx.message.add_reaction('✅')

    @commands.command()
    async def move(self, ctx, i:int, f:int):
        self.author_in_vc(ctx)
        player = self.get_player(ctx.guild.id)

        if len(player.queue.tracks) < 3:
            raise Exception("NotEnoughTracks")

        try:
            player.queue.move(i, f)
        except IndexError:
            raise Exception("IndexError")
        await ctx.message.add_reaction('✅')

    @commands.command()
    async def shuffle(self, ctx):
        self.author_in_vc(ctx)
        player = self.get_player(ctx.guild.id)

        if len(player.queue.tracks) < 3:
            raise Exception("NotEnoughTracks")
        player.queue.shuffle()
        await ctx.message.add_reaction('🔀')


def setup(bot):
    try:
        bot.add_cog(Music(bot))
    except Exception as ex:
        print(ex)
        print(ex.message)