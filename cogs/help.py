import asyncio
import time
import discord
from discord.ext import commands
from constants import *
import inspect

class HelpCog(commands.Cog):
    def __init__(self, client, bot_data):
        
        self.client = client
        self.BOT_DATA = bot_data

    @commands.group(pass_context=True)
    async def help(self, ctx):
        logger(ctx, inspect.stack()[0][3], self.BOT_DATA)
        
        if ctx.invoked_subcommand in [None]:

            desc = [
                "```o.link (osu account/id)```",
                "**Main Commands:**",
                "```",
                "o.help stats",
                "o.help beatmap",
                "o.help practice",
                "o.help search",
                "```",
                "```",
                "o.info (@discord user)",
                "o.rank (rank #)",
                "o.pp (pp #)",
                "```"
            ]

            embed = discord.Embed(title="Help Menu", description="\n".join(
            desc), color=GREEN)
            embed.set_footer(text="Requested by " + str(ctx.author.name),
                        icon_url=ctx.author.avatar_url)
            embed.add_field(name="Other Commands",value="`o.patchnotes`, `o.invite`, `o.vote`, `o.ping`",inline=False)
            await ctx.send("", embed=embed)
            
    @help.command(pass_context=True)
    async def stats(self, ctx):
        logger(ctx, inspect.stack()[0][3], self.BOT_DATA)
        
        desc = [
                "Search for different statistics by osu username or id.",
                "```",
                "o.stats (osu user)",
                "o.stats top (osu user)",
                "o.stats recent (osu user)",
                "o.stats compare (osu user 1) (osu user 2)",
                "o.stats compare (osu user)",
                "```",
                "**Tip**: If the user has linked their osu! account you can also tag their discord.",
                "**Tip**: Once you have linked an account, you do not need to type your username in. `o.stats top` for example, will display your top plays the same as `o.stats top (your username)`"
            ]
        embed = discord.Embed(title="Stats Help Menu", description="\n".join(
        desc), color=GREEN)
        embed.set_footer(text="Requested by " + str(ctx.author.name),
                    icon_url=ctx.author.avatar_url)
        await ctx.send("", embed=embed)
    
    @help.command(pass_context=True)
    async def beatmap(self, ctx):
        logger(ctx, inspect.stack()[0][3], self.BOT_DATA)
        
        desc = [
                "Search for a beatmap.",
                "Input can be a `beatmap link`, `beatmap id`, or even the `beatmap name` (slow)",
                "**Shortcuts:**"
                "```",
                "o.beatmap (beatmap)",
                "o.bm (beatmap)",
                "o.map (beatmap)",
                "```"
            ]
        embed = discord.Embed(title="Beatmap Help Menu", description="\n".join(
        desc), color=GREEN)
        embed.set_footer(text="Requested by " + str(ctx.author.name),
                    icon_url=ctx.author.avatar_url)
        await ctx.send("", embed=embed)
    
    @help.command(pass_context=True)
    async def practice(self, ctx):
        logger(ctx, inspect.stack()[0][3], self.BOT_DATA)
        
        desc = [
                "Recommends maps to play and beat!",
                "```",
                "o.practice",
                "```",
                "**Shortcuts**",
                "```",
                "o.practice",
                "o.prac",
                "o.p"
                "```"
            ]

        embed = discord.Embed(title="Practice Help Menu", description="\n".join(
        desc), color=GREEN)
        embed.set_footer(text="Requested by " + str(ctx.author.name),
                    icon_url=ctx.author.avatar_url)
        await ctx.send("", embed=embed)

    @help.command(pass_context=True)
    async def search(self, ctx):
        logger(ctx, inspect.stack()[0][3], self.BOT_DATA)
        
        desc = [
                "Customized beatmap searching using: `osusearch.com`",
                "```",
                "o.search random",
                "o.search recommend",
                "```",
            ]

        desc = [
            "Work in progress!"
        ]

        embed = discord.Embed(title="Beatmap Help Menu", description="\n".join(
        desc), color=GREEN)
        embed.set_footer(text="Requested by " + str(ctx.author.name),
                    icon_url=ctx.author.avatar_url)
        await ctx.send("", embed=embed)