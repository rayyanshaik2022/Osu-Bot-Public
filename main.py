import asyncio
import json
import requests
import os
import time
from datetime import date
import copy
from bs4 import BeautifulSoup
import urllib3
from collections.abc import Sequence
import inspect

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

import discord
import discord.ext.commands as commands
from discord.utils import get
from discord import Intents

from constants import *

from collections import Counter
from difflib import SequenceMatcher

from cogs.stats import StatsCog 
from cogs.help import HelpCog
from cogs.calculate import CalculateCog
from cogs.practice import PracticeCog

intents = discord.Intents(members=True, guilds=True)

prefix = "o."
client = commands.Bot(command_prefix=prefix, description='An osu! tracker bot',chunk_guilds_at_startup=False)
client.remove_command("help")

class local:
    SERVER_DATA = {}
    CLIENT_DATA = {}
    BOT_DATA = {}
    LOG = None

def generate_beatmapset_page(data : dict):
    desc = [
        "Mapped by: " + data[0]['creator'] + "#" + data[0]['creator_id']
    ]
    embed = discord.Embed(title=f"{data[0]['title']} by {data[0]['artist']}", description="\n".join(
        desc), color=PINK)
    embed.set_thumbnail(url=f"https://b.ppy.sh/thumb/{data[0]['beatmapset_id']}l.jpg")

    difficulties = ", ".join( [str(x) + "☆" for x in sorted([round(float(x['difficultyrating']),2) for x in data],reverse=True)] )
    embed.add_field(name="Star Difficulties",value=difficulties,inline=False)
    map_url = "https://osu.ppy.sh/beatmapsets/" + data[0]['beatmapset_id']
    embed.add_field(name="Download Beatmap Set",value=f"[{map_url}]({map_url})",inline=False)
    embed.add_field(name="Play Count",value="{:,}".format(sum([int(x['playcount']) for x in data])) + " plays",inline=False)
    
    return embed

def generate_beatmap_page(data : dict):
    
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
    embed.add_field(name="Status",value=["Graveyard", "WIP", "Pending", "Ranked", "Approved", "Qualified", "Loved"][int(data['approved'])+2],inline=False)
    embed.add_field(name="Bpm",value=str(float(data['bpm'])) ,inline=True)
    embed.add_field(name="Time",value=data['total_length']+'s',inline=True)
    embed.add_field(name="Plays",value="{:,}".format(int(data['playcount'])),inline=True)
    embed.add_field(name="Passes",value="{:,}".format(int(data['passcount'])) + f" ({round(100*int(data['passcount'])/int(data['playcount']),2)})%",inline=True)
    embed.add_field(name="Max Combo",value=data['max_combo'],inline=True)
    
    return embed

async def save_data():
    '''
    - Periodically saves CLIENT_DATA as a json file
    '''

    while True:
        minutes = 20
        await asyncio.sleep(60*minutes)

        with open('client_data.json', 'w') as f:
            json.dump(local.CLIENT_DATA, f, indent=4)
            print('[=] Client-data json successfully updated')
        
        with open('bot_data.json', 'w') as f:
            json.dump(local.BOT_DATA, f, indent=4)
            print('[=] Bot-data json successfully updated')

# Async loops
client.loop.create_task(save_data())

# Load data
if os.path.exists("client_data.json"):
    with open('client_data.json', 'r') as f:

        local.CLIENT_DATA = json.load(f)
        # Merges player data with 'default data' to account for new keys
        print("[=] Client-data file properly loaded")
else:
    with open('client_data.json', 'w') as f:
        json.dump({}, f)
        print('[+] New Client-data file')

# Load data
if os.path.exists("bot_data.json"):
    with open('bot_data.json', 'r') as f:

        local.BOT_DATA = json.load(f)
        # Merges player data with 'default data' to account for new keys
        print("[=] Bot-data file properly loaded")
else:
    with open('bot_data.json', 'w') as f:
        json.dump({}, f)
        print('[+] New Bot-data file')

# COGS
client.add_cog(StatsCog(client, local.CLIENT_DATA, local.BOT_DATA))
client.add_cog(HelpCog(client, local.BOT_DATA))
client.add_cog(CalculateCog(client, local.BOT_DATA))
client.add_cog(PracticeCog(client, local.CLIENT_DATA, local.BOT_DATA))

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    print("------------")

    activity = discord.Game(name=f"o.help | tracking osu plays")
    await client.change_presence(status=discord.Status.online, activity=activity)

@client.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send("Thank you for adding OsuBot!\nCommand prefix: `o.`\nHere is my command list:")
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
            embed.add_field(name="Other Commands",value="`o.patchnotes`, `o.invite`, `o.ping`",inline=False)
            await channel.send("", embed=embed)
            break

@client.command(pass_context=True)
async def link(ctx, username : str = None):
    logger(ctx, inspect.stack()[0][3], local.BOT_DATA)

    if username == None:

        if str(ctx.author.id) in local.CLIENT_DATA:
            desc = [
                "Link a different account with:",
                "```.link (username/id)```"
            ]
            embed = discord.Embed(title="Account already linked!", description="\n".join(
                desc), color=GREEN)
            embed.set_footer(text="Requested by " + str(ctx.author.name),
                icon_url=ctx.author.avatar_url)
            await ctx.send("", embed=embed)
        else:
            desc = [
                "```.link (username/id)```"
            ]
            embed = discord.Embed(title="Link your osu! account", description="\n".join(
                desc), color=GREEN)
            embed.set_footer(text="Requested by " + str(ctx.author.name),
                icon_url=ctx.author.avatar_url)
            await ctx.send("", embed=embed)
    else:
        # Check to see if username/id is valid
        response = requests.get(f"https://osu.ppy.sh/api/get_user?u={username}&k={OLD_OSU_API}")
        data = response.json()

        # username / id does not exist
        if data == []:
            desc = [
            "```.link (username/id)```"
            ]
            embed = discord.Embed(title="Invalid username/id", description="\n".join(
                desc), color=RED)
            embed.set_footer(text="Requested by " + str(ctx.author.name),
                icon_url=ctx.author.avatar_url)
            await ctx.send("", embed=embed)
        else:

            data = data[0]

            # Data setup here

            local.CLIENT_DATA[str(ctx.author.id)] = {}
            local.CLIENT_DATA[str(ctx.author.id)]['username'] = data['username']
            local.CLIENT_DATA[str(ctx.author.id)]['user_id'] = data['user_id'] 

            desc = [
            "Discord user: `" + ctx.author.name + "` linked to osu! account: ",
            "`"+data['username'] + "#" + data['user_id']+"`"
            ]
            embed = discord.Embed(title="Account link successful!", description="\n".join(
                desc), color=GREEN)
            embed.set_footer(text="Requested by " + str(ctx.author.name),
                icon_url=ctx.author.avatar_url)
            await ctx.send("", embed=embed)

@client.command(pass_context=True, aliases=['bm', 'map'])
async def beatmap(ctx, *, id_ : str = None):
    logger(ctx, inspect.stack()[0][3], local.BOT_DATA)

    if "osu.ppy.sh" in id_ or id_.isdigit():
        if "osu.ppy.sh" in id_:
            if "#" in id_:
                splitter = id_.index("#")
                id_ = id_[31:splitter]
            else:
                id_ = id_[31:]

        url = f"https://osu.ppy.sh/api/get_beatmaps?k={OLD_OSU_API}&s={id_}"
        response = requests.get(url)
        data = response.json()
        
        if data != []:
            data = sorted(data, key=lambda x: float(x['difficultyrating']), reverse=True)
            desc = [
                    "Mapped by: " + data[0]['creator'] + "#" + data[0]['creator_id']
            ]
            embed = discord.Embed(title=f"{data[0]['title']} by {data[0]['artist']}", description="\n".join(
                desc), color=PINK)
            embed.set_footer(text="Requested by " + str(ctx.author.name) + " | Page 1/" + str(1+len(data)),
                icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=f"https://b.ppy.sh/thumb/{id_}l.jpg")

            diffs = [str(round(float(x['difficultyrating']),2)) for x in data]
            embed.add_field(name="Star Difficulties",value="☆, ".join(diffs)+"☆",inline=False)
            map_url = "https://osu.ppy.sh/beatmapsets/" + data[0]['beatmapset_id']
            embed.add_field(name="Download Beatmap Set",value=f"[{map_url}]({map_url})",inline=False)
            embed.add_field(name="More Information",value="Interact with the arrows to see difficulty specific information",inline=False)

            msg = await ctx.send("", embed=embed)

            first_page = embed
            current_page = 0
            total_pages = len(data)+1 # starts from 0-len

            pages = [generate_beatmap_page(d) for d in data]
            for i, embed in enumerate(pages):
                embed.set_footer(text="Requested by " + str(ctx.author.name) + " | Page "+ str(i+2) +"/" + str(1+len(data)),
                icon_url=ctx.author.avatar_url)
            pages.insert(0, first_page)

            start_time = time.time()
            timeout = 120 # in seconds
            await msg.add_reaction("\U000025c0") # Back
            await msg.add_reaction("\U000025b6") # Forward

            while time.time() - start_time <= timeout:

                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) in ["\U000025c0","\U000025b6"]

                try:
                    reaction, user = await client.wait_for('reaction_add', timeout=(5), check=check)
                except asyncio.TimeoutError:
                    pass
                else:
                    if str(reaction.emoji) == "\U000025b6":
                        if current_page + 1 < total_pages:
                            current_page += 1
                        await msg.remove_reaction("\U000025b6", ctx.author)
                    elif str(reaction.emoji) == "\U000025c0":
                        if current_page - 1 >= 0:
                            current_page -= 1
                        await msg.remove_reaction("\U000025c0", ctx.author)
                

                    await msg.edit(embed=pages[current_page])
                    
        else:
            desc = [
                    "```.beatmap (beatmap set id)```",
                    "or",
                    "```.bm (beatmap set id)```"
            ]
            embed = discord.Embed(title="Invalid beatmap set id!", description="\n".join(
                desc), color=RED)
            embed.set_footer(text="Requested by " + str(ctx.author.name),
                icon_url=ctx.author.avatar_url)
            await ctx.send("", embed=embed)
            return
    else:
        #id_ = id_.replace(" ", "%20")
        print(id_)
        url = f"https://osusearch.com/search/?title={id_}&query_order=play_count"

        '''
        response = requests.get(url, timeout=(10,3))
        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.find_all("div", class_="truncate beatmap-title")
        print(links)'''

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--silent")
        options.add_experimental_option("prefs",{"download.default_directory":"/databricks/driver"})
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.get(url)
        await asyncio.sleep(2.5)
        #truncate beatmap-title
        html = driver.page_source.lower()
        driver.close()
        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all("a", string=id_)

        # no maps
        if links == []:
            desc = [
                    "```.beatmap (name/beatmap set id/link)```",
                    "or",
                    "```.bm (name/beatmap set id/link)```"
            ]
            embed = discord.Embed(title="No beatmaps found!", description="\n".join(
                desc), color=RED)
            embed.set_footer(text="Requested by " + str(ctx.author.name),
                icon_url=ctx.author.avatar_url)
            await ctx.send("", embed=embed)
            return
        
        beatmap_ids = []
        for href in links:
            href = str(href)
            start = str(href).index("b") + 2
            end = href.index(">")-1
            beatmap_ids.append(href[start:end])
        
        if len(beatmap_ids) > 3:
            beatmap_ids = beatmap_ids[:3]

        data = [requests.get(f"https://osu.ppy.sh/api/get_beatmaps?k={OLD_OSU_API}&b={x}").json() for x in beatmap_ids]
        pages = [generate_beatmapset_page(requests.get(f"https://osu.ppy.sh/api/get_beatmaps?k={OLD_OSU_API}&s={d[-1]['beatmapset_id']}").json()) for d in data]

        first_page = pages[0]
        current_page = 0

        for i, embed in enumerate(pages):
            embed.set_footer(text="Requested by " + str(ctx.author.name) + " | Page "+ str(i+1) +"/" + str(len(pages)),
            icon_url=ctx.author.avatar_url)

        msg = await ctx.send("", embed=first_page)

        if len(pages) <= 1:
            return 

        start_time = time.time()
        timeout = 120 # in seconds
        await msg.add_reaction("\U000025c0") # Back
        await msg.add_reaction("\U000025b6") # Forward

        while time.time() - start_time <= timeout:

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["\U000025c0","\U000025b6"]

            try:
                reaction, user = await client.wait_for('reaction_add', timeout=(5), check=check)
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

@client.command(pass_context=True)
async def rank(ctx, val : str = None):
    logger(ctx, inspect.stack()[0][3], local.BOT_DATA)

    try:
        val = int(val)
    except:
        desc = [
            "```.rank (rank #)```",
        ]
        embed = discord.Embed(title="Invalid input!", description="\n".join(
            desc), color=RED)
        embed.set_footer(text="Requested by " + str(ctx.author.name),
            icon_url=ctx.author.avatar_url)
        await ctx.send("", embed=embed)
        # end method
        return
    
    response = requests.get(f"https://osudaily.net/api/pp?k={OSU_DAILY_API}&m=0&t=rank&v={val}")
    data = response.json()

    desc = [
            "pp : ~" + str(data['pp']),
            "rank : " + "{:,}".format(int(val))
    ]
    embed = discord.Embed(title="Rank to PP", description="\n".join(
        desc), color=PINK)
    embed.set_footer(text="Requested by " + str(ctx.author.name),
        icon_url=ctx.author.avatar_url)
    await ctx.send("", embed=embed)
    # end method
    return

@client.command(pass_context=True)
async def pp(ctx, val : str = None):
    logger(ctx, inspect.stack()[0][3], local.BOT_DATA)
    
    try:
        val = int(val)
    except:
        desc = [
            "```.pp (pp #)```",
        ]
        embed = discord.Embed(title="Invalid input!", description="\n".join(
            desc), color=RED)
        embed.set_footer(text="Requested by " + str(ctx.author.name),
            icon_url=ctx.author.avatar_url)
        await ctx.send("", embed=embed)
        # end method
        return
    
    response = requests.get(f"https://osudaily.net/api/pp?k={OSU_DAILY_API}&m=0&t=pp&v={val}")
    data = response.json()

    desc = [
            "pp : " + str(val),
            "rank : ~" + "{:,}".format(int(data['rank']))
    ]
    embed = discord.Embed(title="PP to Rank", description="\n".join(
        desc), color=PINK)
    embed.set_footer(text="Requested by " + str(ctx.author.name),
        icon_url=ctx.author.avatar_url)
    await ctx.send("", embed=embed)
    # end method
    return

@client.command(pass_context=True)
async def ping(ctx):
    logger(ctx, inspect.stack()[0][3], local.BOT_DATA)
    await ctx.send(f'Pong! {round(client.latency,3)}s reply')

@client.command(pass_context=True)
async def info(ctx, user : discord.User = "None"):
    logger(ctx, inspect.stack()[0][3], local.BOT_DATA)

    if type(user) == str:
        desc = [
            "```o.info (@discord user)```",
        ]
        embed = discord.Embed(title=f"Invalid Input!", description="\n".join(
            desc), color=RED)
        embed.set_footer(text="Requested by " + str(ctx.author.name),
            icon_url=ctx.author.avatar_url)
        await ctx.send("", embed=embed)
        return

    if str(user.id) in local.CLIENT_DATA:
        desc = [
            "```osu! username: " + local.CLIENT_DATA[str(user.id)]['username'] + "```",
        ]
        embed = discord.Embed(title=f"{user.name}'s Information", description="\n".join(
            desc), color=PINK)
        embed.set_footer(text="Requested by " + str(ctx.author.name),
            icon_url=ctx.author.avatar_url)
        await ctx.send("", embed=embed)
    else:
        desc = [
            "```This user has not linked an osu! account!```",
        ]
        embed = discord.Embed(title=f"{user.name}'s Information", description="\n".join(
            desc), color=RED)
        embed.set_footer(text="Requested by " + str(ctx.author.name),
            icon_url=ctx.author.avatar_url)
        await ctx.send("", embed=embed)

@client.command(pass_context=True)
async def patchnotes(ctx):
    logger(ctx, inspect.stack()[0][3], local.BOT_DATA)
    desc = [
        "Version - **1.0.0**",
        "Last Updated - **2/6/2021**",
        "\> Commands now support tagging @discorduser",
        "\> Added `o.practice` and 'choke' algorithm",
        "\> Working on `o.beatmap` optimizations",
        "\> Custom emojis added for mods",
        "Bot created by Turkey#3157"
    ]
    embed = discord.Embed(title="Patch Notes", description="\n".join(
        desc), color=GREEN)
    embed.set_footer(text="Requested by " + str(ctx.author.name),
        icon_url=ctx.author.avatar_url)
    await ctx.send("", embed=embed)

@client.command(pass_context=True)
async def invite(ctx):
    logger(ctx, inspect.stack()[0][3], local.BOT_DATA)

    embed = discord.Embed(title="Invite Link", description="[Click Here](https://discord.com/api/oauth2/authorize?client_id=799470485124939786&permissions=1275456576&scope=bot)", color=PINK)
    embed.set_footer(text="Requested by " + str(ctx.author.name),
        icon_url=ctx.author.avatar_url)
    await ctx.send("", embed=embed)


@client.command(pass_context=True)
async def vote(ctx):
    logger(ctx, inspect.stack()[0][3], local.BOT_DATA)

    embed = discord.Embed(title="Vote Link", description="[Click Here](https://top.gg/bot/799470485124939786)", color=PINK)
    embed.set_footer(text="Requested by " + str(ctx.author.name),
        icon_url=ctx.author.avatar_url)
    await ctx.send("", embed=embed)

@client.command(pass_context=True)
async def admin(ctx, more : str = False):
    print(f"{inspect.stack()[0][3]} - called by {ctx.author.name}")
    if ctx.author.id == 181125845358870528:

        if more == "help":
            for guild in client.guilds:
                flag = True
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).send_messages:
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
                        embed.add_field(name="Other Commands",value="`o.patchnotes`, `o.invite`, `o.ping`",inline=False)
                        try:
                            flag = False
                            await channel.send("", embed=embed)
                            break
                        except:
                            pass
                        
                        
                if flag:
                    await ctx.author.send("Could not send to: " + str(guild.name))
            await ctx.author.send("Completed sending help message!")
        elif more == "vote":
            for guild in client.guilds:
                flag = True
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).send_messages:
                        desc = [
                            "Show your support for OsuBot by voting and leaving a 5 star review!",
                            "[Voting Link | Click Here](https://top.gg/bot/799470485124939786)",
                            "Thanks!"
                        ]

                        embed = discord.Embed(title="Want to support OsuBot?", description="\n".join(
                        desc), color=PINK)
                        try:
                            flag = False
                            await channel.send("", embed=embed)
                            break
                        except:
                            pass
                                        
                if flag:
                    await ctx.author.send("Could not send to: " + str(guild.name))
            await ctx.author.send("Completed sending help message!")
        elif more == "users":
            await ctx.send(f"Total Users: {len(local.CLIENT_DATA.keys())}")
        elif more == "stats":
            
            a = []
            for w in sorted(local.BOT_DATA, key=local.BOT_DATA.get, reverse=True):
                a.append(f"{w} : {local.BOT_DATA[w]}")
            b = "\n".join(a)
            await ctx.send(b)
        elif more == "purge":
            for guild in client.guilds:
                if int(guild.member_count) <= 4:
                    try:
                        await ctx.send(f"Left Guild: {guild.name}")
                        await guild.leave()
                    except:
                        await ctx.send(f"Error with {guild.name}")

        else:
            total_server = len(client.guilds)
            total_users = 0

            if more != False:
                await ctx.author.send("New Request: ")

            for guild in client.guilds:
                if more != False:
                    await ctx.author.send(guild.name + " | " + str(guild.member_count) + " members")

                total_users += guild.member_count
            
            await ctx.send("Total Guilds: " + str(total_server))
            await ctx.send("Total Users: " + str(total_users))

@client.event
async def on_message(message):

    if message.author.id is client.user.id:
        return    

    await client.process_commands(message)

client.run(DISCORD_API, bot=True)
