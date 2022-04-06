# Imports
import discord
# from discord.ext import menus
import utils
import random
import math

# class QueueMenu(menus.Menu):
#     async def send_initial_message(self, ctx, channel, queue):
#         return await channel.send(embed=queue)
        
#     @menus.button('\N{THUMBS UP SIGN}')
#     async def on_skip(self, payload):
#         await self.message.edit(content=f'Thanks {self.ctx.author}!')

#     @menus.button('\N{THUMBS DOWN SIGN}')
#     async def on_toggle_pause(self, payload):
#         await self.message.edit(content=f"That's not nice {self.ctx.author}...")

#     @menus.button('\N{BLACK SQUARE FOR STOP}\ufe0f')
#     async def on_stop(self, payload):
#         self.stop()

# Queue class
class Queue():
    def __init__(self, source=None):
        '''
        creates a queue instance
        source (optional): pass an existing queue instance to copy
        '''
        if source:
            self.tracks = source.tracks
            self.looping = source.looping
            self.history = source.history
        else:
            self.tracks = []
            self.looping = False
            self.history = [] # if looping, add these to the queue when the last track is done
    
    def add(self, tracks: list):
        '''
        takes one or multiple track objects and appends them to the queue
        '''
        for track in tracks:
            if len(self.tracks) > 100: break
            self.tracks.append(track)
    
    @property
    def len(self):
        return len(self.tracks)
    
    def next(self):
        '''
        pops the first track and returns the next;
        if queue ends and is looping, appends first track to history and returns the first track
        '''
        if self.looping:
            self.history.append(self.tracks[0])

        self.tracks.pop(0)

        if self.is_empty():
            if self.looping:
                self.tracks = self.history
                self.history = []
                return self.tracks[0]
            else:
                return None
        else:
            return self.tracks[0]
    
    def is_empty(self):
        return self.tracks == []
    
    def delete(self, i):
        '''
        removes track at given index
        '''
        self.tracks.pop(i)
    
    def clear(self):
        '''
        clears all but the first track from the queue
        '''
        del(self.tracks[1:])
    
    def move(self, first, second):
        '''
        picks up a track and plops it at the given index, shifting all lower tracks down
        '''
        movable = self.tracks.pop(first)
        self.tracks.insert(second, movable)
    
    def shuffle(self):
        '''
        shuffles all tracks after the first
        '''
        new = self.tracks[1:]
        random.shuffle(new)
        self.tracks = [self.tracks[0]] + new
    
    def current(self):
        return self.tracks[0]
    
    def format_footer(self, page):
        final = []
        if self.looping:
            final.append("Looping")
        if len(self.tracks) > 6:
            final.append(f"Page {page} / {math.ceil((len(self.tracks)-1)/5)}")
            final.append(f"+ {len(self.tracks) - 6} track{'s' if len(self.tracks) > 7 else ''}")
        return ' | '.join(final)
    
    def embed(self, player, page=1):
        '''
        returns a Discord embed displaying the queue
        player_pos: the position of the player in the current song (milliseconds)
        page: each page displays 5 tracks
        '''
        tracks = self.tracks
        current = tracks[0]

        embed = discord.Embed(
            colour=discord.Colour.from_rgb(90, 180, 90)
        )

        if current.is_stream: # Track | @mention
            embed.add_field(name=f"Currently Streaming{' (Paused)' if player.is_paused else ''}", 
                value=f"[{str(current)}]({current.uri}) | {current.info['requester']}"
                )
        else: # Track | time/total | @mention
            embed.add_field(name=f"Currently Playing{' (Paused)' if player.is_paused else ''}", 
                value=f"[{str(current)}]({current.uri}) | {utils.format_time(player.position)} / {utils.format_time(current.length)} | {current.info['requester']}"
                )
        
        if len(self.tracks) > 1:
            up_next = []

            try:
                tracks = tracks[(page-1)*5+1:min(page*5+1, len(tracks))]
            except Exception:
                raise Exception("PageError")

            for i, track in enumerate(tracks):
                i = i+(page-1)*5+1
                if track.is_stream:
                    up_next.append(f"**{i}.** [{str(track)}]({track.uri}) | Stream | {track.info['requester']}")
                else:
                    up_next.append(f"**{i}.** [{str(track)}]({track.uri}) | {utils.format_time(track.length)} | {track.info['requester']}")

            embed.add_field(name="Up Next", value='\n\n'.join(up_next), inline=False)
        
        embed.set_footer(text=self.format_footer(page))
        
        return embed
