# Imports
import discord
from discord.ext import commands
import json
import utils

# Cog
class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener() # add new entry when joining a guild
    async def on_guild_join(self, guild):
        with open('../prefixes.json', 'r') as f:
            prefixes = json.load(f)

        prefixes[str(guild.id)] = '.'

        with open('../prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)

    @commands.Cog.listener() # delete entry when leaving a guild
    async def on_guild_remove(self, guild):
        with open('../prefixes.json', 'r') as f:
            prefixes = json.load(f)

        prefixes.pop(str(guild.id))

        with open('../prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)

def setup(bot):
    bot.add_cog(Events(bot))