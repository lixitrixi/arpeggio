# Imports
import discord
from discord.ext import commands
import random as r
import dice

class Fun(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    # Commands
    @commands.command()
    async def roll(self, ctx, val="1d6"):
        try:
            roll_results = dice.roll(val)
        except Exception:
            return await ctx.send('Invalid input form: use either a single integer or something of the form "#d#"\nEx: 3d4 (rolls a 4-sided die 3 times and returns the sum)')

        await ctx.send(f"{ctx.author.mention}\n**{sum(roll_results)}**  ({', '.join(map(str, roll_results))})") # ex:  3d4 -> "8 (3, 2, 3)"
    
    @commands.command(aliases=['coinflip'])
    async def coin(self, ctx):
        await ctx.send(r.choice(['Heads!', 'Tails!']))
    
    @commands.command(aliases=['random_list', 'randomlist'])
    async def rlist(self, ctx, n): # returns randomized list of numbers 1-n
        rlist = [*range(1,n+1)]
        r.shuffle(rlist)
        await ctx.send(f"{ctx.author.mention}\n**{str(rlist)}**")

        
def setup(bot):
    bot.add_cog(Fun(bot))
