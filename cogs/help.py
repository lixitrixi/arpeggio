# Imports
import discord
from discord.ext import commands
import json

# Help Embeds
generalHelp = discord.Embed(
    title=":bulb:  General Commands",
    colour=discord.Colour.from_rgb(245, 206, 66)
)
generalHelp.add_field(name='_ _', value="`ping` : Displays the bot's latency\n\n`info` : Shows general information about the bot\n\n`changePrefix [new prefix]` : Changes the bot's prefix in your server")


musicHelp = discord.Embed(
    title=":notes:  Music Commands",
    colour=discord.Colour.blue()
)
musicHelp.add_field(name='_ _', value="`join` : Joins the voice channel you are in\n\n`leave` : Disconnects the bot from a voice channel\n\n`play [query]` : Searches and plays a track with the specified keywords\n\n`pause/stop` : Pauses the current track\n\n`resume` : Resumes playback\n\n`current` : Shows the currently playing track as a video")


queueHelp = discord.Embed(
    title=":page_with_curl:  Queue Commands",
    colour=discord.Colour.magenta()
)
queueHelp.add_field(name='_ _', value="`queue` : Shows the track queue for your server\n\n`skip` : Skips to the next track in the queue\n\n`clear` : Clears all songs from the queue\n\n`move [from] [to]` : Moves the track at the first index to the second index\n\n`remove [index]` : Removes the track at the specified index, defaults to the last track")


funHelp = discord.Embed(
    title=":tada:  Fun Commands",
    colour=discord.Colour.orange()
)
funHelp.add_field(name='_ _', value="`roll [value]` : Rolls a die with the given number of sides (default 1d6); supports D&D dice syntax\n\n`coin` : Flips a coin")

helpEmbeds = {'general': generalHelp, 'music': musicHelp, 'queue': queueHelp, 'fun': funHelp}


directory = discord.Embed(
    colour=discord.Colour.from_rgb(255, 60, 60)
)
directory.add_field(name="General", value="`help general`", inline=False)
directory.add_field(name="Music", value="`help music`", inline=False)
directory.add_field(name="Queue", value="`help queue`", inline=False)
directory.add_field(name="Fun", value="`help fun`", inline=False)

# Cog
class Help(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    # Commands
    @commands.command(aliases=['h'])
    async def help(self, ctx, *, category=None):
        if not category:
            Embed = directory
        
        else:
            try:
                Embed = helpEmbeds[category]
            except KeyError:
                return await ctx.send('Specified help menu does not exist')

        await ctx.send(embed=Embed)


def setup(bot):
    bot.add_cog(Help(bot))
