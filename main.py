# Imports
import discord
from discord.ext import commands
import json
import os
from builds import get_prefix

with open('../tokens.json', 'r') as f:
    tokens = json.load(f)
    TOKEN = tokens['arpeggio']


# Initiation
bot = commands.Bot(command_prefix=get_prefix)

bot.remove_command('help')
bot.add_check(commands.guild_only())


# Events
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} | {bot.user.id}")

@bot.event
async def on_message(message):
    if message.content == '<@!732712093756948579>':
        await message.channel.send(f"Hi! My prefix is `{get_prefix(bot, message)}`")
    
    await bot.process_commands(message)

@bot.event
async def on_guild_join(guild): # adds an entry to prefixes.json (default prefix: '.')
    with open('../prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = '.'

    with open('../prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

@bot.event
async def on_guild_remove(guild):
    with open('../prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))

    with open('../prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

# Runtime

for file in os.listdir('cogs'): # load .py files in cogs folder as extensions
    if file.endswith('.py'):
        try:
            bot.load_extension(f'cogs.{file[:-3]}')
        except Exception:
            print(f"Cog '{file[:-3]}' could not be loaded")

bot.run(TOKEN)