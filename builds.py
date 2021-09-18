# Imports
import discord
import math
import random

# Functions
def format_time(ms): # formats milliseconds to hrs:min:sec
    minutes = int((ms / 1000) / 60)
    seconds = int((ms / 1000) % 60)

    if seconds < 10:
        seconds = f"0{seconds}"

    return f"{minutes}:{seconds}"

def format_page_count(length, page):
    returnString = f""

    if length - page*5 > 0:
        returnString = f"+ {length - page*5} tracks | "
    
    returnString += f"Page {page} / {math.ceil(length/5)}"

    return returnString

def add_apos(word): # correctly formats a word with an apostraphe
    if word.endswith('s'):
        return f"{word}'"
    else:
        return f"{word}'s"


# Classes
class Queue:
    def __init__(self):
        self.tracks = [] # list of (track obj, requester)
    
    def next(self):
        self.tracks.pop(0)

        if self.tracks:
            return self.tracks[0][0]
        else:
            return None
        
    def add(self, tracks):
        for track in tracks:
            self.tracks.append(track)
    
    def is_empty(self):
        return self.tracks == []
    
    def delete(self, index):
        self.tracks.pop(index)
    
    def clear(self):
        del(self.tracks[1:])
    
    def move(self, first, second):
        movable = self.tracks.pop(first)

        self.tracks.insert(second, movable)
    
    def format(self, player_pos, page=1): # returns a Discord embed with the current and next track(s)
        queue_embed = discord.Embed(
            colour=discord.Colour.from_rgb(255, 59, 59)
        )

        current = self.tracks[0]

        if current[0].is_stream:
            queue_embed.add_field(name="Currently Streaming", value=f"[{str(current[0])}]({current[0].uri}) | {current[1]}", inline=False)
        else:
            queue_embed.add_field(name="Currently Playing", value=f"[{str(current[0])}]({current[0].uri}) | {format_time(player_pos)} / {format_time(current[0].length)} | {current[1]}", inline=False)
        
        if len(self.tracks) > 1:
            queue_list = []
            
            for index, entry in enumerate(self.tracks[((page-1)*5)+1:page*5+1]):
                track = entry[0]
                requester = entry[1]
                if track.is_stream:
                    queue_list.append(f"**{index+1+((page-1)*5)}.** [{str(track)}]({track.uri}) | Stream | {requester}")
                else:  
                    queue_list.append(f"**{index+1+((page-1)*5)}.** [{str(track)}]({track.uri}) | {format_time(track.length)} | {requester}")

            queue_embed.add_field(name="Queue", value='\n\n'.join(queue_list), inline=False)

            if len(self.tracks) > 6:
                queue_embed.set_footer(text=format_page_count(len(self.tracks)-1, page))

        return queue_embed

class Playlist:
    def __init__(self, owner, tracks): #takes list of tracks attributed to the owner
        self.tracks = tracks # list of tracks
        self.owner = owner
    
    def is_empty(self):
        return self.tracks == []

    def add(self, tracks):
        self.tracks += tracks

    def compress(self):
        return [track.uri for track in self.tracks]
    
    def delete(self, index):
        self.tracks.pop(index)

    def clear(self):
        self.tracks = []
    
    def shuffle(self):
        random.shuffle(self.tracks)
    
    def format(self):
        playlist_embed = discord.Embed(
        colour=discord.Colour.from_rgb(255, 60, 60)
        )
    
        playlist_embed.add_field(name="\a", value='\n\n'.join([f"**{i+1}.** [{str(track)}]({track.uri}) | {format_time(track.length)}" for i, track in enumerate(self.tracks)]), inline=False)

        playlist_embed.set_author(name=f"{add_apos(self.owner.display_name)} Playlist", icon_url=self.owner.avatar_url)
        
        return playlist_embed
