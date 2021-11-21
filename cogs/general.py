# Imports
import discord
from discord.ext import commands
import json
import utils

# Cog
class General(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Commands
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Pong! ({round(self.bot.latency*1000)}ms)')
    
    @commands.command(aliases=['changePrefix', 'changeprefix', 'set_prefix', 'setPrefix', 'setprefix'])
    @commands.has_permissions(administrator=True)
    async def change_prefix(self, ctx, prefix):
        
        with open('../prefixes.json', 'r') as f:
            prefixes = json.load(f)

        prefixes[str(ctx.guild.id)] = prefix

        with open('../prefixes.json', 'w') as f: #updates the file
            json.dump(prefixes, f, indent=4)

        await ctx.send(f"Server prefix was changed to  `{prefix}`")
    
    @commands.command()
    async def invite(self, ctx):
        await ctx.send(embed=utils.embed("Invite me [here](https://discord.com/api/oauth2/authorize?client_id=732712093756948579&permissions=3427392&scope=bot)!"))
    
    @commands.command()
    async def vote(self, ctx):
        await ctx.send(embed=utils.embed("Vote for me [here](https://top.gg/bot/732712093756948579/vote)!", emoji='upvote'))
    
    @commands.command(aliases=['links'])
    async def info(self, ctx):
        await ctx.send(embed=utils.embed(
            "[Support Server](https://discord.gg/fmPTwfw) | [Invite!](https://discord.com/api/oauth2/authorize?client_id=732712093756948579&permissions=3427392&scope=bot) | [Vote!](https://top.gg/bot/732712093756948579/vote) | [GitHub](https://github.com/lixitrixi/arpeggio)",
            color = (90, 160, 230)
        ))

def setup(bot):
    bot.add_cog(General(bot))