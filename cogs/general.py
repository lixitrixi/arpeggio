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
        await ctx.send(embed=utils.embed(
            f'Pong! ({round(self.bot.latency*1000)}ms)',
            color=(90, 160, 230)
        ))
    
    @commands.command(aliases=['changePrefix', 'changeprefix', 'set_prefix', 'setPrefix', 'setprefix'])
    @commands.has_permissions(administrator=True)
    async def change_prefix(self, ctx, prefix):
        
        with open('../prefixes.json', 'r') as f:
            prefixes = json.load(f)

        prefixes[str(ctx.guild.id)] = prefix

        with open('../prefixes.json', 'w') as f: #updates the file
            json.dump(prefixes, f, indent=4)

        await ctx.send(embed=utils.embed(
            f"Server prefix was changed to  `{prefix}`",
            color=(90, 160, 230)
        ))
    
    @commands.command()
    async def invite(self, ctx):
        await ctx.send(embed=utils.embed(
            "Invite me [here](https://discord.com/api/oauth2/authorize?client_id=732712093756948579&permissions=11889728&scope=bot)!",
            color=(90, 160, 230)
            ))
    
    @commands.command()
    async def vote(self, ctx):
        await ctx.send(embed=utils.embed(
            "Vote for me [here](https://top.gg/bot/732712093756948579/vote)!", emoji='upvote',
            color=(90, 160, 230)
            ))
    
    @commands.command(aliases=['links', 'support'])
    async def info(self, ctx):
        await ctx.send(embed=utils.embed(
            "[Support Server](https://discord.gg/fmPTwfw) | [Invite!](https://discord.com/api/oauth2/authorize?client_id=732712093756948579&permissions=11889728&scope=bot) | [Top.gg](https://top.gg/bot/732712093756948579) | [Vote!](https://top.gg/bot/732712093756948579/vote) | [GitHub](https://github.com/lixitrixi/arpeggio)",
            color=(90, 160, 230)
        ))
    
    @commands.command(aliases=["blacklist"])
    @commands.has_permissions(administrator=True)
    async def blocklist(self, ctx, member):
        mem_id = member[2:-1]
        await ctx.send(mem_id)

        with open("../blacklist.json", 'r') as f:
            blacklists = json.load(f)
        try:
            ids = set(blacklists[ctx.guild.id])
        except KeyError:
            ids = set()
        
def setup(bot):
    bot.add_cog(General(bot))