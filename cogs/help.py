# Imports
import discord
from discord.ext import commands
import json
from reactionmenu import ReactionMenu
import utils


with open('data/commands.json', 'r') as f:
    command_dict = json.load(f)

embeds = []

for section in command_dict.keys():
    embed = discord.Embed(
        title = f"{section[0].upper()}{section[1:]} Commands",
        description = '\n\n'.join([f"` {key} ` : {command_dict[section][key]}" for key in command_dict[section].keys()])
    )
    embeds.append(embed)

# Cog
class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=['h']) # send a reaction menu for viewing different help pages
    async def help(self, ctx):
        help_menu = ReactionMenu(ctx, back_button='◀️', next_button='▶️', config=ReactionMenu.STATIC, show_page_director=False, navigation_speed=ReactionMenu.FAST)

        for embed in embeds:
            embed.set_footer(text=f"(required) [optional] | This server's prefix is: {utils.get_prefix(self.bot, ctx.message)}")
            help_menu.add_page(embed)
        
        await help_menu.start()


def setup(bot):
    bot.add_cog(Help(bot))