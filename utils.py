# Imports
import discord
from discord.ext import commands
import json

# get the bot's prefix on a given guild
def get_prefix(bot, message):
    try:
        with open('../prefixes.json', 'r') as f:
            prefixes = json.load(f)
            prefix = prefixes[str(message.guild.id)]
            return prefix
    except Exception:
        print(f"WARNING: Prefix not found for guild: {message.guild.id}")
        return "."

# embed template to share a line of feedback
def embed(content: str, color=(90, 180, 90), emoji=''):
    '''
    content: text to display
    color: rgb of embed accent color, default 
    emoji: name of emoji that should preceed text
    '''
    if emoji: # get full syntax for emoji name to include in text
        try:
            with open('data/emojis.json', 'r') as f:
                emojis = json.load(f)
            emoji = emojis[emoji]
        except KeyError:
            emoji = f":{emoji}:"

    embed = discord.Embed(
        colour = discord.Color.from_rgb(*color),
        description = f"{emoji}{' ' if emoji else ''}{content}"
    )

    return embed

def format_time(ms):
    '''
    formats milliseconds into hr:min:sec
    '''
    sec = int(
        (ms/1000) % 60
    )
    min = int(
        (ms/(1000*60)) % 60
    )
    hr = int(
        (ms/(1000*60*60)) % 60
    )

    if hr and hr < 10:
        hr = f"0{hr}"
    if min < 10:
        min = f"0{min}"
    if sec < 10:
        sec = f"0{sec}"

    if hr:
        return f"{hr}:{min}:{sec}"
    else:
        return f"{min}:{sec}"

def parse_time(time):
    time = time.split(':')
    try:
        time = list(map(int, time))
        if len(time) == 3: # hr:min:sec
            time = time[0]*(1000*60*60) + time[1]*(1000*60) + time[2]*(1000)
        elif len(time) == 2: # min:sec
            time = time[0]*(1000*60) + time[1]*(1000)
        elif len(time) == 3: # sec
            time = time[0]*(1000)
        else:
            raise Exception('ParsingError')
        
        return time
    except Exception:
        raise Exception('ParsingError')
