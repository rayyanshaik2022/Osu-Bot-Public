import asyncio
import time
import discord
from discord.ext import commands
from constants import *
import requests
import inspect

def generate_beatmap_page(data : dict, s_data : dict, mode = ""):

    desc = [
        f"Mapped by {data['creator']}#{data['creator_id']}"
    ]
    embed = discord.Embed(title=f"{data['title']} by {data['artist']}", description="\n".join(
        desc), color=PINK)
    embed.set_thumbnail(url=f"https://b.ppy.sh/thumb/{data['beatmapset_id']}l.jpg")

    diffs = [
        "```",
        "Star Difficulty:   " + str(round(float(data['difficultyrating']),2)) + " ☆",
        "Circle Size:       " + str(float(data['diff_size'])),
        "HP Drain:          " + str(float(data['diff_drain'])),
        "Approach Rate:     " + str(float(data['diff_approach'])),
        "Overall:           " + str(float(data['diff_overall'])),
        "```"
    ]
    embed.add_field(name=f"Difficulty | {data['version']}",value="\n".join(diffs),inline=False)
    embed.add_field(name="Status",value=["Graveyard", "WIP", "Pending", "Ranked", "Approved", "Qualified", "Loved"][int(data['approved'])+2],inline=False)
    embed.add_field(name="Bpm",value=str(float(data['bpm'])) ,inline=True)
    embed.add_field(name="Time",value=data['total_length']+'s',inline=True)
    embed.add_field(name="Max Combo",value=data['max_combo'],inline=True)

    print(s_data)
    pp_desc = [f"{x[1:]}% : {s_data[f'pp{mode}'][x]}pp" for x in s_data[f'pp{mode}'].keys()]
    embed.add_field(name="Estimated PP",value="\n".join(pp_desc),inline=True)
    
    return embed

class CalculateCog(commands.Cog):
    def __init__(self, client, bot_data):
        
        self.client = client
        self.BOT_DATA = bot_data

    @commands.group(pass_context=True,aliases=['calc'])
    async def calculate(self, ctx, *, map_id):
        print(f"{inspect.stack()[0][3]} - called by {ctx.author.name}")

        if ctx.invoked_subcommand in [None]:
            
            url = f"https://beatconnect.io/api/search/?s=ranked&m=std&q={map_id}&diff_range=0-10&token={BEATCONNECT_API}"
            r = requests.get(url).json()

            beatmap = None
            for bmsets in r['beatmaps']:
                for bm in bmsets['beatmaps']:
                    if str(bm['id']) == map_id:
                        beatmap = bm
                
            url = f"https://osu.ppy.sh/api/get_beatmaps?k={OLD_OSU_API}&b={map_id}"
            more_data = requests.get(url).json()[0]

            #TODO: "beatmap" variable does not have right data
            embed_none = generate_beatmap_page(more_data, beatmap)
            embed_dt = generate_beatmap_page(more_data, beatmap, "_dt")
            embed_hd = generate_beatmap_page(more_data, beatmap, "_hd")
            embed_hr = generate_beatmap_page(more_data, beatmap, "_hr")
            embed_hdhr = generate_beatmap_page(more_data, beatmap, "_hdhr")
            embed_dthd = generate_beatmap_page(more_data, beatmap, "_dthd")
            embed_dthr = generate_beatmap_page(more_data, beatmap, "_dthr")
            embed_dthdhr = generate_beatmap_page(more_data, beatmap, "_dthdhr")

            await ctx.send("", embed=embed_dthdhr)
            #1816585