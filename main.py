# Imports
import discord
from discord.ext import commands
import json
import os
import importlib
import utils

# get bot token from outside repo
with open('../tokens.json', 'r') as f:
    tokens = json.load(f)
TOKEN = tokens['arpeggio']

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
        except Exception:
            print(f"Cog '{file[:-3]}' could not be loaded")

if __name__ == "__main__":
    bot.run(TOKEN)
