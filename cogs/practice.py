import asyncio
import time
import discord
from discord.ext import commands
from constants import *
import inspect
import requests
import random
from calculations import *

def generate_beatmap_page(data : dict, bm):
    
    desc = [
        f"Mapped by {data['creator']}#{data['creator_id']}"
    ]
    embed = discord.Embed(title=f"{data['title']} by {data['artist']}", description="\n".join(
        desc), color=PINK)
    embed.set_thumbnail(url=f"https://b.ppy.sh/thumb/{data['beatmapset_id']}l.jpg")

    diffs = [
        f"Beatmap ID: `{data['beatmap_id']}`",
        "```",
        "Star Difficulty:   " + str(round(float(data['difficultyrating']),2)) + " ☆",
        "Circle Size:       " + str(float(data['diff_size'])),
        "HP Drain:          " + str(float(data['diff_drain'])),
        "Approach Rate:     " + str(float(data['diff_approach'])),
        "Overall:           " + str(float(data['diff_overall'])),
        "```"
    ]
    embed.add_field(name=f"Difficulty | {data['version']}",value="\n".join(diffs),inline=False)

    desc = [
        "```",
        f"Accuracy:         {round(accuracy(int(bm['count50']), int(bm['count100']), int(bm['count300']), int(bm['countmiss'])),2)}%",
        f"Max Combo:        {bm['maxcombo']}/{data['max_combo']}",
        f"PP:               {bm['pp']}",
        f"Misses:           {bm['countmiss']}",
        f"Rank:             {bm['rank']}",
        "```"
    ]
    embed.add_field(name="Your stats",value="\n".join(desc), inline=False)
    
    return embed

class PracticeCog(commands.Cog):
    def __init__(self, client, client_data, bot_data):
        
        self.client = client
        self.CLIENT_DATA = client_data
        self.BOT_DATA = bot_data

    @commands.group(pass_context=True, aliases=['p', 'prac'])
    async def practice(self, ctx):
        logger(ctx, inspect.stack()[0][3], self.BOT_DATA)
        
        if ctx.invoked_subcommand in [None]:

            desc = [
            "Currently analyzing top 100 plays..."
            ]
            embed = discord.Embed(title="Analyzing Plays...", description="\n".join(
            desc), color=ORANGE)
            embed.set_footer(text="Requested by " + str(ctx.author.name),
                        icon_url=ctx.author.avatar_url)
            msg = await ctx.send("", embed=embed)

            if str(ctx.author.id) in self.CLIENT_DATA:
                user = self.CLIENT_DATA[str(ctx.author.id)]['username']
                total = 100
                url = f"https://osu.ppy.sh/api/get_user_best?u={user}&limit={total}&k={OLD_OSU_API}"
                data = requests.get(url).json()
                
                total_pp = 0
                total_combo = 0
                total_miss = 0
                total_acc = 0
                choke_scores = []

                for bm in data:
                    total_pp += float(bm['pp'])
                    total_combo += int(bm['maxcombo'])
                    total_miss += int(bm['countmiss'])
                    total_acc += int(accuracy(int(bm['count50']), int(bm['count100']), int(bm['count300']), int(bm['countmiss'])))
                
                avg_acc = total_acc/len(data)
                avg_pp = total_pp/len(data)

                desc = [
                    f"Averages for top {total} plays",
                    "Analyzing choke plays..."
                    "```",
                    f"Average pp         :  {round(avg_pp)}",
                    f"Average max combo  :  {round(total_combo/len(data))}",
                    f"Average misses     :  {round(total_miss/len(data))}",
                    f"Average accuracy   :  {round(avg_acc)}" 
                    "```"
                ]
                embed = discord.Embed(title=f"{user}'s Analysis", description="\n".join(
                desc), color=ORANGE)
                embed.set_footer(text="Requested by " + str(ctx.author.name),
                            icon_url=ctx.author.avatar_url)
                await msg.edit(embed=embed)

                choke_scores = [choke(bm['countmiss'], bm['rank'], int(avg_pp), float(bm['pp']), int(bm['count100']), int(bm['maxcombo']), bm['perfect']) for bm in data]
                zipped = zip(choke_scores, data)

                display_maps = 3
                sorted_chokes = sorted(zipped, key=lambda x: x[0], reverse=True)[:35]

                random_maps = []
                for i in range(display_maps):
                    picked = random.choice(sorted_chokes)
                    random_maps.append(picked)
                    sorted_chokes.remove(picked)
                    
                desc = [
                    f"Averages for top {total} plays",
                    "```",
                    f"Average pp         :  {round(avg_pp)}",
                    f"Average max combo  :  {round(total_combo/len(data))}",
                    f"Average misses     :  {round(total_miss/len(data))}",
                    f"Average accuracy   :  {round(avg_acc)}",
                    "```",
                    "All plays have been analyzed!",
                    "Click the emojis to see recommended maps to practice."
                ]
                embed = discord.Embed(title=f"{user}'s Analysis", description="\n".join(
                desc), color=GREEN)
                embed.set_footer(text="Requested by " + str(ctx.author.name),
                            icon_url=ctx.author.avatar_url)
                await msg.edit(embed=embed)

                #print(requests.get(f"https://osu.ppy.sh/api/get_beatmaps?k={OLD_OSU_API}&s={data[0]['beatmap_id']}").json())

                pages = [generate_beatmap_page(requests.get(f"https://osu.ppy.sh/api/get_beatmaps?k={OLD_OSU_API}&b={d[1]['beatmap_id']}").json()[0], d[1]) for d in random_maps]
                pages.insert(0, embed)
                first_page = pages[0]
                current_page = 0

                for i, embed in enumerate(pages):
                    embed.set_footer(text="Requested by " + str(ctx.author.name) + " | Page "+ str(i+1) +"/" + str(len(pages)),
                    icon_url=ctx.author.avatar_url)

                if len(pages) <= 1:
                    return 

                start_time = time.time()
                timeout = 60*4 # in seconds
                await msg.add_reaction("\U000025c0") # Back
                await msg.add_reaction("\U000025b6") # Forward

                while time.time() - start_time <= timeout:

                    def check(reaction, user):
                        return user == ctx.author and str(reaction.emoji) in ["\U000025c0","\U000025b6"]

                    try:
                        reaction, user = await self.client.wait_for('reaction_add', timeout=(5), check=check)
                    except asyncio.TimeoutError:
                        pass
                    else:
                        if str(reaction.emoji) == "\U000025b6":
                            if current_page + 1 < len(pages):
                                current_page += 1
                            await msg.remove_reaction("\U000025b6", ctx.author)
                        elif str(reaction.emoji) == "\U000025c0":
                            if current_page - 1 >= 0:
                                current_page -= 1
                            await msg.remove_reaction("\U000025c0", ctx.author)
                    

                        await msg.edit(embed=pages[current_page])

            else:
                desc = [
                        "An osu! account must be linked to use this feature!",
                        "You can link your account using this command:",
                        "```o.link (username)```"
                    ]
                embed = discord.Embed(title="No account linked!", description="\n".join(
                    desc), color=RED)
                embed.set_footer(text="Requested by " + str(ctx.author.name),
                    icon_url=ctx.author.avatar_url)
                await ctx.send("", embed=embed)
        

        