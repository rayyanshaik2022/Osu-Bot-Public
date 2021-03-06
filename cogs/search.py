import asyncio
import time
import discord
from discord.ext import commands
from constants import *
import inspect

class SearchCog(commands.Cog):
    def __init__(self, client, client_data):
        
        self.client = client
        self.CLIENT_DATA = client_data

    @commands.group(pass_context=True)
    async def search(self, ctx):
        print(f"{inspect.stack()[0][3]} - called by {ctx.author.name}")
        
        if ctx.invoked_subcommand in [None]:

            desc = [
                "For more information try...",
                "```o.help search```"
            ]
            embed = discord.Embed(title="Invalid Search!", description="\n".join(
            desc), color=RED)
            embed.set_footer(text="Requested by " + str(ctx.author.name),
                        icon_url=ctx.author.avatar_url)
            await ctx.send("", embed=embed)
            
    @search.command(pass_context=True)
    async def stats(self, ctx):
        pass
    