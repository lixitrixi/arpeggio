# Imports
import discord
from discord.ext import commands
import wavelink
import builds
import utils


# Cog
class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, 'wavelink'): # add wavelink client
            self.bot.wavelink = wavelink.Client(bot=self.bot)

        self.bot.loop.create_task(self.start_nodes())
    
    async def start_nodes(self):
        await self.bot.wait_until_ready()

        node = await self.bot.wavelink.initiate_node(host='0.0.0.0',
                                              port=2333,
                                              rest_uri='http://0.0.0.0:2333',
                                              password='youshallnotpass',
                                              identifier='TEST',
                                              region='us_central')
        
        node.set_hook(self.on_lavalink_event)
    
    async def on_lavalink_event(self, event):
        if isinstance(event, wavelink.events.TrackEnd):
            player = event.player

            track = player.queue.next()

            if track:
                await player.play(track)
    
    def get_player(self, guild_id):
        '''
        returns the player object for the given guild
        '''
        player = self.bot.wavelink.get_player(guild_id)

        if not hasattr(player, 'queue'):
            player.queue = builds.Queue()

        return player
    
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
        player = self.get_player(ctx.guild.id)
        try: 
            member_ids = [member.id for member in self.bot.get_channel(player.channel_id).members]
        except AttributeError:
            raise Exception("NotInSameVoice")
        if not ctx.author.id in member_ids:
            raise Exception("NotInSameVoice")
    
    # music commands
    @commands.command(aliases=['s', 'ytsearch'])
    async def search(self, ctx, *, query=None):
        '''
        searches a query on youtube and returns top 5 results
        '''
        if not query:
            raise Exception("NoQuery")

        await ctx.send(embed=utils.embed(f"Searching  ` {query} `", emoji='mag_right'))

        tracks = await self.bot.wavelink.get_tracks(f"ytsearch:{query}")

        if not tracks:
            raise Exception("NoResults")

        results = utils.embed(
            '\n\n'.join([f"**{i+1}.** [{str(track)}]({track.uri}) | {utils.format_time(track.length)}" for i, track in enumerate(tracks[0:5])])
        )

        await ctx.send(embed=results)
    
    @commands.command(aliases=['join', 'j'])
    async def connect(self, ctx):
        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            raise Exception("NoChannel")

        player = self.get_player(ctx.guild.id)

        if player.channel_id == channel.id:
            raise Exception("AlreadyConnected")

        elif player.channel_id and len(self.bot.get_channel(player.channel_id).members) > 1:
            raise("StealingBot")

        await ctx.send(embed=utils.embed(f"Connecting to **{channel.name}**", emoji="satellite"))
        await player.connect(channel.id)
        await player.set_pause(False)
    
    @commands.command(aliases=['leave', 'l'])
    async def disconnect(self, ctx):
        player = self.get_player(ctx.guild.id)

        if len(self.bot.get_channel(player.channel_id).members) > 1: # if bot is alone it's ok
            self.author_in_vc(ctx)

        await player.disconnect()
        await ctx.message.add_reaction('👋')

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, query=None):
        if not query:
            raise Exception("NoQuery")
        
        player = self.get_player(ctx.guild.id)

        if not player.is_connected:
            await ctx.invoke(self.connect)

        self.author_in_vc(ctx)
        
        await ctx.send(embed=utils.embed(f"Searching ` {query} `", emoji='mag_right'))

        name, tracks = await self.get_tracks(query)

        if len(tracks) == 1:
            name = f"[{str(tracks[0])}]({tracks[0].uri})"

        if player.queue.is_empty():
            await player.play(tracks[0])
            await ctx.send(embed=utils.embed(f"Playing __{name}__", emoji="cd"))
            await player.set_pause(False)
        else:
            await ctx.send(embed=utils.embed(f"Added __{name}__ to the queue", emoji="pencil"))

        for track in tracks: # attribute author's mention string to each track
            track.info['requester'] = ctx.author.mention
        
        player.queue.add(tracks)
    
    @commands.command(aliases=['q'])
    async def queue(self, ctx, page: int = 1):
        player = self.get_player(ctx.guild.id)

        if player.queue.is_empty():
            raise Exception("QueueEmpty")
        
        await ctx.send(embed=player.queue.embed(player.position, page=page))
    
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
    
    @commands.command() # clear queue and history, stop player
    async def stop(self, ctx):
        self.author_in_vc(ctx)
        player = self.get_player(ctx.guild.id)

        player.queue.tracks = []
        player.queue.history = []
        player.queue.looping = False
        await player.stop()

        await ctx.message.add_reaction('⏹️')
    
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
    bot.add_cog(Music(bot))