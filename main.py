# Imports
import discord
from discord.ext import commands
import json
import os
import importlib
from cogs.music import SPOTIFY_SECRET
import utils

# get bot token from outside repo
with open('../tokens.json', 'r') as f:
    tokens = json.load(f)
TOKEN = tokens['arpeggio']
SPOTIFY_SECRET = tokens['spotify']

# initiation
bot = commands.Bot(command_prefix=utils.get_prefix)
bot.remove_command('help') # we add our own later
bot.add_check(commands.guild_only())


# Events
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} | {bot.user.id}")

@bot.event
async def on_message(msg):
    if msg.content == bot.user.mention: # user mentioned bot; give prefix and help command
            return await msg.channel.send(
                embed=utils.embed(
                    f"Hi! My command prefix for this server is `{utils.get_prefix(bot, msg)}`"
                    f"\nUse `{utils.get_prefix(bot, msg)}help` for a list of commands",
                    color=(90, 160, 230)
                )
            )
    elif msg.content.startswith(f"<@!{bot.user.id}>"):
        msg.content.replace(bot.user.mention+' ', utils.get_prefix(bot, msg))
        msg.content.replace(bot.user.mention, utils.get_prefix(bot, msg))

    cont = msg.content.split()
    try:
        f = cont.pop(0)
    except Exception:
        return
    f = f.lower()
    msg.content = f + (' ' + ' '.join(cont) if cont else '')

    await bot.process_commands(msg)

@bot.command()
async def reload_utils(ctx):
    importlib.reload(utils)
    await ctx.message.add_reaction('✅')

# load cogs
for file in os.listdir('cogs'): # load .py files in cogs folder as extensions
    if file.endswith('.py'):
        try:
            bot.load_extension(f'cogs.{file[:-3]}')
        except Exception as ex:
            print(f"Cog '{file[:-3]}' could not be loaded:\n{ex}")

if __name__ == "__main__":
    bot.run(TOKEN)
