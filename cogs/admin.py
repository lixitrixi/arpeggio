# Imports
import os
import importlib
import discord
from discord.ext import commands
# from discord.ext import menus
import wavelink
import music
import sys
sys.path.append('../arpeggio/')
import builds
import utils

# Cog
class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx): # reloads all cogs
        for file in os.listdir('cogs'):
            if file.endswith('.py'):
                try:
                    self.bot.unload_extension(f'cogs.{file[:-3]}')
                except Exception:
                    pass
                try:
                    self.bot.load_extension(f'cogs.{file[:-3]}')
                except Exception as ex:
                    raise Exception(f"{file} could not be loaded")

        await ctx.invoke(self.bot.get_command('reload_utils'))
        await ctx.invoke(self.bot.get_command('reload_queues'))
        await ctx.message.add_reaction('✅')

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, ext):
        for file in os.listdir('cogs'):
            if file.endswith(f'{ext}.py'):
                try:
                    self.bot.load_extension(f'cogs.{file[:-3]}')
                    await ctx.message.add_reaction('✅')
                except Exception as err:
                    await ctx.message.add_reaction('❌')
    
    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, ext):
        if ext == 'admin':
            return await ctx.send("You fool! Use reload instead")

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
    async def close_bot(self, ctx):
        for guild in self.bot.guilds: # disconnect all player clients
            vc: music.Player = guild.voice_client
            await vc.disconnect()
        
        await self.bot.close()
    
    @commands.command()
    @commands.is_owner()
    async def reload_queues(self, ctx):
        importlib.reload(builds)

        for player in wavelink.NodePool.get_node().players:
            if hasattr(player, 'queue'):
                player.queue = builds.Queue(player.queue)

        await ctx.message.add_reaction('✅')

    @commands.command(aliases=["gc"])
    @commands.is_owner()
    async def guild_count(self, ctx):
        guild_count = len(self.bot.guilds)

        active_guilds = 0
        for player in wavelink.NodePool.get_node().players:
            if not player.queue.is_empty():
                active_guilds += 1

        await ctx.send(embed=utils.embed(
            f"Guild count: {guild_count}\nActively listening guilds: {active_guilds}"
        ))
            

def setup(bot):
    bot.add_cog(Admin(bot))