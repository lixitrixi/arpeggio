# Imports
import discord
from discord.ext import commands
import json
import os

# Cog
class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx): # reloads all cogs
        success = True
        for file in os.listdir('cogs'):
            if file.endswith('.py'):
                try:
                    self.bot.unload_extension(f'cogs.{file[:-3]}')
                except Exception:
                    pass
                try:
                    self.bot.load_extension(f'cogs.{file[:-3]}')
                except Exception:
                    success = False
                    await ctx.send(f"{file} could not be loaded.")
        
        if success:
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('❌')

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, ext):
        for file in os.listdir('cogs'):
            if file.endswith(f'{ext}.py'):
                try:
                    self.bot.load_extension(f'cogs.{file[:-3]}')
                    await ctx.message.add_reaction('✅')
                except Exception:
                    await ctx.message.add_reaction('❌')
    
    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, ext):
        for file in os.listdir('cogs'):
            if file.endswith(f'{ext}.py'):
                try:
                    self.bot.unload_extension(f'cogs.{file[:-3]}')
                    await ctx.message.add_reaction('✅')
                except Exception:
                    await ctx.message.add_reaction('❌')

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
        await ctx.send(f"Currently on **{len(self.bot.guilds)}** guilds!")
    
    @commands.command()
    @commands.is_owner()
    async def close_bot(self, ctx):
        music = self.bot.get_cog('Music')

        for guild in self.bot.guilds: # disconnect any instances currently in VC
            player = music.get_player(guild.id)
            await player.disconnect()
        
        await self.bot.logout()
    
    @commands.command()
    @commands.is_owner()
    async def n_playing(self, ctx): # returns the number of servers arpy is playing music on
        music = self.bot.get_cog('Music')

        n = 0

        for guild in self.bot.guilds:
            player = music.get_player(guild.id)
            if not player.queue.is_empty():
                n += 1
    
        await ctx.send(f"Playing music on **{n}** guilds")
            


def setup(bot):
    bot.add_cog(Admin(bot))