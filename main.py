# Imports
import discord
from discord.ext import commands
import json
import os

with open('/root/tokens.json', 'r') as f:
    tokens = json.load(f)
    TOKEN = tokens['arpeggio']

# Functions
def get_prefix(bot, message):
    with open('data/prefixes.json', 'r') as f:
        prefixes = json.load(f)

    try:
        return prefixes[str(message.guild.id)]
    except KeyError:
        return '.'


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
    if '<@!732712093756948579>' in message.content.split():
        await message.channel.send(f"Hi! My prefix is `{get_prefix(bot, message)}`")
    
    await bot.process_commands(message)

@bot.event
async def on_guild_join(guild): # adds an entry to prefixes.json (default prefix: '.')
    with open('data/prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = '.'

    with open('data/prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

@bot.event
async def on_guild_remove(guild):
    with open('data/prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))

    with open('data/prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)


# Admin Commands
@bot.command()
@commands.is_owner()
async def reload(ctx): # reloads all cogs
    for file in os.listdir('cogs'):
        if file.endswith('.py'):
            bot.unload_extension(f'cogs.{file[:-3]}')
            bot.load_extension(f'cogs.{file[:-3]}')
    
    await ctx.message.add_reaction('✅')

@bot.command()
@commands.is_owner()
async def load(ctx, ext):
    for file in os.listdir('cogs'):
        if file.endswith(f'{ext}.py'):
            bot.load_extension(f'cogs.{file[:-3]}')
            await ctx.message.add_reaction('✅')

@bot.command()
@commands.is_owner()
async def set_status(ctx, *, text): # changes the bot's playing status
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(text))
    await ctx.message.add_reaction('✅')


# Runtime

for file in os.listdir('cogs'): # load .py files in cogs folder as extensions
    if file.endswith('.py'):
        bot.load_extension(f'cogs.{file[:-3]}')

bot.run(TOKEN)