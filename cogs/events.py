# Imports
import discord
from discord.ext import commands
import json
import sys
sys.path.insert(0, '../arpeggio/tools/')
import utils

# Cog
class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener() # if bot is pinged, send prefix for that guild
    async def on_message(self, message):
        if message.content == f"<@!{self.bot.user.id}>": # user mentioned bot; give prefix and help command
            await message.channel.send(
                embed=utils.embed(
                    f"Hi! My command prefix for this server is `{utils.get_prefix(self.bot, message)}`"
                    f"\nUse `{utils.get_prefix(self.bot, message)}help` for a list of commands",
                    color=(90, 160, 230)
                    )
                )

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