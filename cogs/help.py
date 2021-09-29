# Imports
import discord
from discord.ext import commands
import json
from builds import get_prefix

# Help Embeds
generalHelp = discord.Embed(
    title=":bulb:  General Commands",
    colour=discord.Colour.from_rgb(245, 206, 66)
)
generalHelp.add_field(name='_ _', value="`ping` : Displays the bot's latency\n\n`info` : Shows general information about the bot\n\n`changePrefix [new prefix]` : Changes the bot's prefix in your server")


with open('data/commands.json', 'r') as f:
    command_list = json.load(f)

generalHelp = discord.Embed(
    title=":bulb:  General Commands",
    colour=discord.Colour.from_rgb(245, 206, 66)
)
generalHelp.add_field(name='_ _', value='\n\n'.join([f"`{key}` {command_list['general'][key]}" for key in command_list['general'].keys()]))

musicHelp = discord.Embed(
    title=":notes:  Music Commands",
    colour=discord.Colour.from_rgb(245, 206, 66)
)
musicHelp.add_field(name='_ _', value='\n\n'.join([f"`{key}` {command_list['music'][key]}" for key in command_list['music'].keys()]))

funHelp = discord.Embed(
    title=":tada:  Fun Commands",
    colour=discord.Colour.from_rgb(245, 206, 66)
)
funHelp.add_field(name='_ _', value='\n\n'.join([f"`{key}` {command_list['fun'][key]}" for key in command_list['fun'].keys()]))

helpEmbeds = {'general': generalHelp, 'music': musicHelp, 'fun': funHelp}

directory = discord.Embed(
    colour=discord.Colour.from_rgb(255, 60, 60)
)
directory.add_field(name="General", value="`help general`", inline=False)
directory.add_field(name="Music", value="`help music`", inline=False)
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
                # Embed.set_footer(f"My prefix on this server is {get_prefix(self.bot, ctx)}")
            except KeyError:
                return await ctx.send('Specified help menu does not exist')

        await ctx.send(embed=Embed)


def setup(bot):
    bot.add_cog(Help(bot))
