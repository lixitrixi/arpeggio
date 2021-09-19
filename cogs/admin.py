# Imports
import discord
from discord.ext import commands
import json
import os

# Cog
class Admin(commands.cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx): # reloads all cogs
        for file in os.listdir('cogs'):
            if file.endswith('.py'):
                self.bot.unload_extension(f'cogs.{file[:-3]}')
                self.bot.load_extension(f'cogs.{file[:-3]}')
        
        await ctx.message.add_reaction('✅')

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, ext):
        for file in os.listdir('cogs'):
            if file.endswith(f'{ext}.py'):
                self.bot.load_extension(f'cogs.{file[:-3]}')
                await ctx.message.add_reaction('✅')

    @commands.command()
    @commands.is_owner()
    async def set_status(self, ctx, *, text): # changes the bot's playing status
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(text))
        await ctx.message.add_reaction('✅')

    @commands.command()
    @commands.is_owner()
    async def clear_status(self, ctx):
        await self.bot.change_presence(status=discord.Status.online, activity=None)
        await ctx.message.add_reaction('✅')

    @commands.command()
    @commands.is_owner()
    async def guild_count(self, ctx):
        with open('data/prefixes.json', 'r') as f:
            prefixes = json.load(f)

        await ctx.send(f"Currently on {len(prefixes.keys())} guilds!")

def setup(bot):
    bot.add_cog(Admin(bot))