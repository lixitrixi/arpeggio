# Imports
import discord
from discord.ext import commands
import os
import utils
import builds

import traceback
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
                except Exception:
                    success = False
                    raise Exception(f"{file} could not be loaded")

        await ctx.invoke(self.bot.get_command('reload_utils'))
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
                    print(str(err.__traceback__))
    
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
        music = self.bot.get_cog('Music')

        for guild in self.bot.guilds: # disconnect any instances currently in VC
            player = music.get_player(guild.id)
            await player.disconnect()
        
        await self.bot.logout()
    
    @commands.command()
    @commands.is_owner()
    async def reload_queues(self, ctx):
        music = self.bot.get_cog('Music')

        for guild in self.bot.guilds:
            player = music.get_player(guild.id)

            try:
                player.queue = builds.Queue(player.queue)
            except Exception: # player queue wasn't initialized yet, ignore
                pass

    @commands.command(aliases=["gc"])
    @commands.is_owner()
    async def guild_count(self, ctx):
        guild_count = len(self.bot.guilds)

        music = self.bot.get_cog('Music')

        active_guilds = 0
        for guild in self.bot.guilds:
            player = music.get_player(guild.id)
            if not player.queue.is_empty():
                active_guilds += 1

        await ctx.send(embed=utils.embed(
            f"Guild count: {guild_count}\nActively listening guilds: {active_guilds}"
        ))
            


def setup(bot):
    bot.add_cog(Admin(bot))