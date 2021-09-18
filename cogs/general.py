# Imports
import discord
from discord.ext import commands
import json

# Cog
class General(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    # Commands
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Pong! ({round(self.bot.latency*1000)}ms)')
    
    @commands.command(aliases=['change_prefix', 'changeprefix'])
    @commands.has_permissions(administrator=True)
    async def changePrefix(self, ctx, prefix):
        
        with open('data/prefixes.json', 'r') as f:
            prefixes = json.load(f)

        prefixes[str(ctx.guild.id)] = prefix

        with open('data/prefixes.json', 'w') as f: #updates the file
            json.dump(prefixes, f, indent=4)

        await ctx.send(f"Server prefix was changed to  `{prefix}`")
    
    # @commands.command(aliases=['invite'])
    @commands.command()
    async def info(self, ctx):
        infoEmbed = discord.Embed(
            colour=discord.Colour.from_rgb(255, 60, 60)
        )

        infoEmbed.set_thumbnail(url='https://cdn.discordapp.com/attachments/566302530053734450/740368259584622592/Anime_Girl_Arppegio.png')
        infoEmbed.add_field(name="About", value=f"Arpeggio is a simple-to-use music bot that comes with everything you need to streamline your music playing experience!", inline=False)
        infoEmbed.add_field(name="Credits", value="Developed by <@!402954494406819862> and <@!454041644912738324> with invaluable help from the amazing volunteers at the Pythonista Guild.", inline=False)
        infoEmbed.add_field(name="Links", value="[Support Server](https://discord.gg/fmPTwfw) | [Invite!](https://discord.com/api/oauth2/authorize?client_id=732712093756948579&permissions=3427392&scope=bot) | [GitHub](https://github.com/lixitrixi/Arpeggio)")

        await ctx.send(embed=infoEmbed)

    # Errors
    @changePrefix.error
    async def changePrefix_error(self, ctx, error):
        
        if isinstance(error, commands.MissingPermissions): #if user does not have admin perms
            await ctx.send("Administrator permissions are recquired to use this command!")
    
        if isinstance(error, commands.MissingRequiredArgument): #if a prefix is not given
            await ctx.send("Be sure to specify a prefix!")

def setup(bot):
    bot.add_cog(General(bot))
