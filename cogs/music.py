# Imports
import discord
from discord.ext import commands
import wavelink
import json
from builds import *


# Cog
class Music(commands.Cog):

    # Functions
    def __init__(self, bot):
        self.bot = bot
        self.playlists = {}

        if not hasattr(bot, 'wavelink'):
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
        player = self.bot.wavelink.get_player(guild_id)

        if not hasattr(player, 'queue'):
            player.queue = Queue()

        return player

    async def get_tracks(self, query):
        if query.startswith('https://'): # if a specific link is given, load that instead of a ytsearch
            tracks = await self.bot.wavelink.get_tracks(query)
        
        else:
            tracks = await self.bot.wavelink.get_tracks(f"ytsearch:{query}")

        if not tracks:
            print(f"No tracks found for '{query}'")
            return None
        
        if isinstance(tracks, wavelink.player.TrackPlaylist):
            return tracks.data['playlistInfo']['name'], tracks.tracks # playlist name, playlist content
        
        else:
            return str(tracks[0]), [tracks[0]] # track name, track
    
    async def author_in_vc(self, ctx):
        player = self.get_player(ctx.guild.id)
        return ctx.author.id in [member.id for member in self.bot.get_channel(player.channel_id).members]


    # Music Commands
    @commands.command(aliases=['s', 'search'])
    async def ytsearch(self, ctx, *, query: str = None):

        await ctx.send(f":mag_right:  Searching  `{query}`")

        tracks = await self.bot.wavelink.get_tracks(f"ytsearch:{query}")

        if not tracks:
            search_error = discord.Embed(
                colour=discord.Colour.from_rgb(255, 59, 59)
            )

            search_error.add_field(name=":confused:  Couldn't find any results", value="Try searching again or contact my [Support Server](https://discord.gg/P7aBBRM)")

            return await ctx.send(embed=search_error)
        
        results = discord.Embed(
            colour=discord.Colour.from_rgb(255,59,59)
            )
        
        results.add_field(name=f"Results", value='\n\n'.join([f"**{i+1}.** [{str(tracks[i])}]({tracks[i].uri}) | {format_time(tracks[i].length)}" for i in range(5)]))

        await ctx.send(embed=results)

    @commands.command(name='join', aliases=['connect'])
    async def _connect(self, ctx):
        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            return await ctx.send('No channel to join!')

        player = self.get_player(ctx.guild.id)
        await ctx.send(f':satellite:  Connecting to **{channel.name}**')
        await player.connect(channel.id)
    
    @commands.command(aliases=['disconnect'])
    async def leave(self, ctx):
        player = self.get_player(ctx.guild.id)

        listening_members = self.bot.get_channel(player.channel_id).members

        if ctx.author not in listening_members and len(listening_members) > 1:
            return await ctx.send("Stealing the music bot is not allowed!")

        await player.disconnect()
        await ctx.message.add_reaction('👋')

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, query):

        if not query:
            return await ctx.send(f"Try that again with some keywords, a video link, or a playlist link!")
        
        player = self.get_player(ctx.guild.id)

        if not player.is_connected:
            await ctx.invoke(self._connect)

        if not self.author_in_vc(ctx):
            return await ctx.send('You must be in the same channel as the bot to use this command!')

        await ctx.send(f":mag_right:  Searching  `{query}`")

        name, tracks = await self.get_tracks(query)

        if not tracks:
            search_error = discord.Embed(
                colour=discord.Colour.from_rgb(255, 59, 59)
            )

            search_error.add_field(name=":confused:  Couldn't find any results", value="Try searching again or contacting my [Support Server](https://discord.gg/P7aBBRM)")

            return await ctx.send(embed=search_error)

        if player.queue.is_empty():
            await player.play(tracks[0])
            await ctx.send(f":cd:  Playing __{name}__")

        else:
            await ctx.send(f":pencil:  Added __{name}__ to the queue")

        player.queue.add([(track, ctx.author.mention) for track in tracks])
    
    @commands.command(aliases=['q'])
    async def queue(self, ctx, page: int = 1):
        player = self.get_player(ctx.guild.id)

        if player.queue.is_empty():
            return await ctx.send("Nothing is currently playing!")

        await ctx.send(embed=player.queue.format(player.position, page))
    
    @commands.command(aliases=['stop'])
    async def pause(self, ctx):
        player = self.get_player(ctx.guild.id)
        
        if not self.author_in_vc(ctx):
            return await ctx.send('You must be in the same channel as the bot to use this command!')

        await player.set_pause(True)
        await ctx.message.add_reaction('⏸')
    
    @commands.command()
    async def resume(self, ctx):
        player = self.get_player(ctx.guild.id)

        if not self.author_in_vc(ctx):
            return await ctx.send('You must be in the same channel as the bot to use this command!')

        await player.set_pause(False)
        await ctx.message.add_reaction('▶')
    
    @commands.command()
    async def skip(self, ctx):
        player = self.get_player(ctx.guild.id)

        if not self.author_in_vc(ctx):
            return

        if player.queue.is_empty():
            return await ctx.send("Nothing to skip!")
        
        await player.stop()
        await ctx.message.add_reaction('⏩')

        await ctx.send(f":cd:  Playing __{str(player.queue.tracks[0]['track'])}__")
    
    @commands.command()
    async def seek(self, ctx, pos=0):
        player = self.get_player(ctx.guild.id)

        if not self.author_in_vc(ctx):
            return await ctx.send('You must be in the same channel as the bot to use this command!')
        
        time = parse_time(pos)
        if not time:
            return await ctx.send("Try again using either `seek (position in seconds)` or `seek (min):(sec)`")
        try:
            await player.seek(pos)
        except Exception:
            return await ctx.send(":confused: There was an error finding that position in the current track.")
    
    @commands.command()
    async def remove(self, ctx, index: int = -1):
        player = self.get_player(ctx.guild.id)

        if not self.author_in_vc(ctx):
            return await ctx.send('You must be in the same channel as the bot to use this command!')

        if len(player.queue.tracks) < 2:
            return await ctx.send("No tracks to remove!")

        if index == 0:
            return await ctx.send("Specified index is outside of the queue's range!")

        try:
            player.queue.delete(index)
        except IndexError:
            return await ctx.send("Specified index is outside of the queue's range!")
        
        await ctx.message.add_reaction('✅')
    
    @commands.command()
    async def clear(self, ctx):
        player = self.get_player(ctx.guild.id)

        if not self.author_in_vc(ctx):
            return await ctx.send('You must be in the same channel as the bot to use this command!')

        player.queue.clear()

        await ctx.message.add_reaction('✅')
    
    @commands.command()
    async def move(self, ctx, first: int, second: int):
        player = self.get_player(ctx.guild.id)

        if not self.author_in_vc(ctx):
            return await ctx.send('You must be in the same channel as the bot to use this command!')

        if len(player.tracks) < 3:
            return await ctx.send("Not enough songs in the queue to move!")

        player.queue.move(first, second)

        await ctx.message.add_reaction('✅')
    

def setup(bot):
    bot.add_cog(Music(bot))
