# Imports
import discord
from discord.ext import commands
import json
import utils

# Cog
class ErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener() # command processing
    async def on_command_error(self, ctx, error):
        error = getattr(error, 'original', error)

        print(error)

        if isinstance(error, commands.CommandNotFound):
            return

        with open('data/errors.json', 'r') as f: # get associated error message
            errors = json.load(f)
        try:
            error = errors[str(error)]
        except KeyError:
            pass # error isn't documented, just send the raw exception

        await ctx.send(
            embed=utils.embed(error, color=(255, 60, 60), emoji='error')
        )

def setup(bot):
    bot.add_cog(ErrorHandler(bot))