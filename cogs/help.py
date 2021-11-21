# Imports
import discord
from discord.ext import commands
import json
import utils

with open('data/commands.json', 'r') as f:
    command_dict = json.load(f)

embeds = {
    'general': utils.embed('\n\n'.join([f"` {key} ` : {command_dict['general'][key]}" for key in command_dict['general'].keys()])),
    'music': utils.embed('\n\n'.join([f"` {key} ` : {command_dict['music'][key]}" for key in command_dict['music'].keys()])),
    'fun': utils.embed('\n\n'.join([f"` {key} ` : {command_dict['fun'][key]}" for key in command_dict['fun'].keys()])),
}

# Cog
class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=['h']) # if no category is given, send the directory, otherwise send the specfic category of commands
    async def help(self, ctx, *, cat=None):
        prefix = utils.get_prefix(self.bot, ctx.message)
        if not cat:
            embed = utils.embed(f"Use `{prefix}help (page)` for specific commands!\n\nHelp pages:\n- " + '\n- '.join(command_dict.keys()), color=(90, 160, 230))
        else:
            if cat in ['general', 'gen']:
                embed = embeds['general']
                embed.title = ":bulb:  General Commands"
            elif cat in ['music', 'queue']:
                embed = embeds['music']
                embed.title = ":notes:  Music Commands"
            elif cat in ['fun']:
                embed = embeds['fun']
                embed.title = ":tada:  Fun Commands"
            else:
                raise Exception(f"Specified help page does not exist")
            
            embed.color = discord.Color.from_rgb(90, 160, 230)
            embed.set_footer(text=f"(required)⠀[optional]⠀|⠀My command prefix for this server is: {prefix}")
        
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))