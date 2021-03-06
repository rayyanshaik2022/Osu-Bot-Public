import asyncio
import time
import discord
from discord.ext import commands
from discord.utils import get
import requests
from constants import *
import calculations
import inspect

class StatsCog(commands.Cog):
    def __init__(self, client, client_data, bot_data):
        
        self.client = client
        self.CLIENT_DATA = client_data
        self.BOT_DATA = bot_data

    @commands.group(pass_context=True, aliases=['s','statistics'])
    async def stats(self, ctx):

        if ctx.invoked_subcommand in [None]:
            logger(ctx, inspect.stack()[0][3], self.BOT_DATA)
            args = ctx.message.content.split()[1:]
            if args == []:
                if str(ctx.author.id) in self.CLIENT_DATA:
                    user = self.CLIENT_DATA[str(ctx.author.id)]['user_id']
                else:
                    desc = [
                    "```o.link (username/id)```",
                    "or",
                    "```o.stats (username/id)```"
                    ]
                    embed = discord.Embed(title="No account linked!", description="\n".join(
                        desc), color=RED)
                    embed.set_footer(text="Requested by " + str(ctx.author.name),
                        icon_url=ctx.author.avatar_url)
                    await ctx.send("", embed=embed)
                    # end method
                    return
            else:
                user = args[0]
                try:
                    b = await ctx.message.guild.fetch_member(user[3:-1])
                except:
                    b = None
                
                if b != None:
                    user_id = b.id
                    if str(user_id) in self.CLIENT_DATA.keys():
                        user = self.CLIENT_DATA[str(user_id)]['username']
                    else:
                        desc = [
                        "This user has not linked their osu! account!",
                        "Try:",
                        "```o.stats (username/id)```",
                        ]
                        embed = discord.Embed(title="Cannot find user!", description="\n".join(
                            desc), color=RED)
                        embed.set_footer(text="Requested by " + str(ctx.author.name),
                            icon_url=ctx.author.avatar_url)
                        await ctx.send("", embed=embed)
                        return


            response = requests.get(f"https://osu.ppy.sh/api/get_user?u={user}&k={OLD_OSU_API}")
            data = response.json()

            if data != []:
                data = data[0]

                signature = f"http://lemmmy.pw/osusig/sig.php?colour=hexff66aa&uname={data['username']}&countryrank&flagstroke&darktriangles&onlineindicator=undefined&xpbar"
                
                desc = []
                embed = discord.Embed(title=f"{data['username']}'s Stats", description="\n".join(
                            desc), color=PINK)
                embed.set_footer(text="Requested by " + str(ctx.author.name),
                            icon_url=ctx.author.avatar_url)

                embed.add_field(name="ID",value=data['user_id'],inline=True)
                embed.add_field(name="Join Date",value=data['join_date'].split()[0],inline=True)
                embed.add_field(name="Country",value=data['country'],inline=True)
                embed.add_field(name="Total PP",value="{:,}".format(int(float(data['pp_raw']))),inline=True)
                embed.add_field(name="Global Rank",value="{:,}".format(int(data['pp_rank'])),inline=True)
                embed.add_field(name="Country Rank",value="{:,}".format(int(data['pp_country_rank'])),inline=True)
                embed.add_field(name="Accuracy",value= str(round(float(data['accuracy']),2))+"%" ,inline=True)
                embed.add_field(name="Playtime",value= "{:,}".format(int(int(data['total_seconds_played'])/(60*60)))+" hours" ,inline=True)
                embed.add_field(name="Play Count",value=data['playcount'] + " plays" ,inline=True)
                embed.add_field(name="Plays per Hour",value=f"{round( int(data['playcount'])/(int(data['total_seconds_played'])/3600)  ,1)} p/h" ,inline=True)
                embed.add_field(name="Level",value=str(int(float(data['level']))) ,inline=True)

                embed.set_thumbnail(url=f"http://s.ppy.sh/a/{data['user_id']}")
                embed.set_image(url=signature)

                await ctx.send("", embed=embed)
            else:

                desc = [
                    "```o.stats (username/id)```"
                    ]
                embed = discord.Embed(title="Invalid username/id", description="\n".join(
                    desc), color=RED)
                embed.set_footer(text="Requested by " + str(ctx.author.name),
                    icon_url=ctx.author.avatar_url)
                await ctx.send("", embed=embed)

    @stats.command(pass_context=True)
    async def compare(self, ctx, player1 : str = None, player2 : str = None):
        logger(ctx, inspect.stack()[0][3], self.BOT_DATA)

        if not player1:
            desc = [
                "```.stats compare (osu user)```",
                "or",
                "```.stats compare (osu user 1) (osu user 2)```"
            ]
            embed = discord.Embed(title="No user provided!", description="\n".join(
                desc), color=RED)
            embed.set_footer(text="Requested by " + str(ctx.author.name),
                icon_url=ctx.author.avatar_url)
            await ctx.send("", embed=embed)
            # end method
            return

        if player1 and not player2:
            player2 = player1

            if str(ctx.author.id) in self.CLIENT_DATA:
                player1 = self.CLIENT_DATA[str(ctx.author.id)]['user_id']
            else:
                desc = [
                "```.stats compare (osu user)```",
                "or link your account with",
                "```.link (username/id)```"
                ]
                embed = discord.Embed(title="No account linked!", description="\n".join(
                    desc), color=RED)
                embed.set_footer(text="Requested by " + str(ctx.author.name),
                    icon_url=ctx.author.avatar_url)
                await ctx.send("", embed=embed)
                # end method
                return

         
            try:
                b = await ctx.message.guild.fetch_member(player2[3:-1])
            except:
                b = None
            
            if b != None:
                user_id = b.id
                if str(user_id) in self.CLIENT_DATA.keys():
                    player2 = self.CLIENT_DATA[str(user_id)]['username']
                else:
                    desc = [
                    "This user has not linked their osu! account!",
                    "Try:",
                    "```o.stats compare (osu user 1) (osu user 2)",
                    "o.stats compare (osu user)```",
                    ]
                    embed = discord.Embed(title="Cannot find user!", description="\n".join(
                        desc), color=RED)
                    embed.set_footer(text="Requested by " + str(ctx.author.name),
                        icon_url=ctx.author.avatar_url)
                    await ctx.send("", embed=embed)
                    return

        # Try to get data
        response = requests.get(f"https://osu.ppy.sh/api/get_user?u={player1}&k={OLD_OSU_API}")
        player1_data = response.json()

        response = requests.get(f"https://osu.ppy.sh/api/get_user?u={player2}&k={OLD_OSU_API}")
        player2_data = response.json()

        # error if a username/id is invalid
        if player1_data == [] or player2_data == []:
            desc = [
                "```.stats compare (osu name/id)```",
                "or",
                "```.stats compare (osu name/id) (osu name/id)```"
            ]
            embed = discord.Embed(title="Invalid users provided!", description="\n".join(
                desc), color=RED)
            embed.set_footer(text="Requested by " + str(ctx.author.name),
                icon_url=ctx.author.avatar_url)
            await ctx.send("", embed=embed)
            # end method
            return

        player1_data = player1_data[0]
        player2_data = player2_data[0]

        desc = []
        embed = discord.Embed(title=f"{player1_data['username']} vs {player2_data['username']}", description="\n".join(
                    desc), color=PINK)
        embed.set_footer(text="Requested by " + str(ctx.author.name),
                    icon_url=ctx.author.avatar_url)

        zipped = [(player1_data['username'], player1_data['pp_raw']), (player2_data['username'], player2_data['pp_raw'])]
        pp_winner = max(zipped, key=lambda x: float(x[1]))[0]
        pp_diff = abs(float(zipped[0][1])-float(zipped[1][1]))
        embed.add_field(name="PP Difference",value= f"{pp_winner} `+{'{:,}'.format((int(pp_diff)))}pp`" ,inline=False)

        zipped = [(player1_data['username'], player1_data['pp_rank']), (player2_data['username'], player2_data['pp_rank'])]
        rank_winner = min(zipped, key=lambda x: float(x[1]))[0]
        rank_diff = abs(float(zipped[0][1])-float(zipped[1][1]))
        embed.add_field(name="Rank Difference",value= f"{rank_winner} `+{'{:,}'.format((int(rank_diff)))}`" ,inline=False)

        zipped = [(player1_data['username'], player1_data['accuracy']), (player2_data['username'], player2_data['accuracy'])]
        acc_winner = max(zipped, key=lambda x: float(x[1]))[0]
        acc_diff = abs(float(zipped[0][1])-float(zipped[1][1]))
        embed.add_field(name="Accuracy Difference",value= f"{acc_winner} `+{'{:,}'.format(round(acc_diff, 2))}%`" ,inline=False)

        zipped = [(player1_data['username'], player1_data['level']), (player2_data['username'], player2_data['level'])]
        level_winner = max(zipped, key=lambda x: float(x[1]))[0]
        level_diff = abs(float(zipped[0][1])-float(zipped[1][1]))
        embed.add_field(name="Level Difference",value= f"{level_winner} `+{'{:,}'.format(int(level_diff))}`" ,inline=True)

        zipped = [(player1_data['username'], int(int(player1_data['total_seconds_played'])/3600)), (player2_data['username'], int(int(player2_data['total_seconds_played'])/3600))]
        level_winner = max(zipped, key=lambda x: float(x[1]))[0]
        level_diff = abs(float(zipped[0][1])-float(zipped[1][1]))
        embed.add_field(name="Play Time Difference",value= f"{level_winner} `+{'{:,}'.format(int(level_diff))} hours`" ,inline=False)

        await ctx.send("", embed=embed)

    @stats.command(pass_context=True)
    async def top(self, ctx, user : str = None):
        logger(ctx, inspect.stack()[0][3], self.BOT_DATA)

        if user == None:
            if str(ctx.author.id) in self.CLIENT_DATA:
                user = self.CLIENT_DATA[str(ctx.author.id)]['user_id']
            else:
                desc = [
                "```o.link (username/id)```",
                "or",
                "```o.stats top (username/id)```"
                ]
                embed = discord.Embed(title="No account linked!", description="\n".join(
                    desc), color=RED)
                embed.set_footer(text="Requested by " + str(ctx.author.name),
                    icon_url=ctx.author.avatar_url)
                await ctx.send("", embed=embed)
                # end method
                return
        
        try:
            b = await ctx.message.guild.fetch_member(user[3:-1])
        except:
            b = None
        
        if b != None:
            user_id = b.id
            if str(user_id) in self.CLIENT_DATA.keys():
                user = self.CLIENT_DATA[str(user_id)]['username']
            else:
                desc = [
                "This user has not linked their osu! account!",
                "Try:",
                "```o.stats top (osu user)```",
                ]
                embed = discord.Embed(title="Cannot find user!", description="\n".join(
                    desc), color=RED)
                embed.set_footer(text="Requested by " + str(ctx.author.name),
                    icon_url=ctx.author.avatar_url)
                await ctx.send("", embed=embed)
                return
        
        response = requests.get(f"https://osu.ppy.sh/api/get_user_best?u={user}&k={OLD_OSU_API}&limit=5")
        data = response.json()

        response_suppl = requests.get(f"https://osu.ppy.sh/api/get_user?u={user}&k={OLD_OSU_API}")
        data_suppl = response_suppl.json()

        if data_suppl != []:
            data_suppl = data_suppl[0]
            
            full_desc = []
            

            for i, play in enumerate(data):

                beatmap_page = requests.get(f"https://osu.ppy.sh/api/get_beatmaps?k={OLD_OSU_API}&b={data[i]['beatmap_id']}")
                beatmap_info = beatmap_page.json()[0]

                accuracy = calculations.accuracy(int(data[i]['count50']), int(data[i]['count100']), int(data[i]['count300']), int(data[i]['countmiss']))
                
                if data[i]['rank'] in play_table:
                    c_emoji = play_table[data[i]['rank']]
                else:
                    c_emoji = ":x:"

                current_mods = " ".join([MODS[mod] for mod in fn_bits(int(play['enabled_mods']))])

                desc = [
                    f"**[{beatmap_info['title']} by {beatmap_info['creator']}](https://osu.ppy.sh/beatmapsets/{beatmap_info['beatmapset_id']}#osu/{play['beatmap_id']})**",
                    f"{c_emoji} {accuracy}%",
                    f"Mods: {current_mods}",
                    f"{beatmap_info['version']} | {round(float(beatmap_info['difficultyrating']),2)}☆",
                    "PP : " + play['pp'] + " • x" + data[i]['maxcombo'] +"/" + beatmap_info['max_combo'],
                ]
                full_desc.extend(desc)
                #embed.add_field(name=f"[{beatmap_info['title']} by {beatmap_info['creator']}](https://www.google.com)",value="\n".join(desc),inline=False)

            embed = discord.Embed(title=f"{data_suppl['username']}'s Top Plays", description="\n".join(
                        full_desc), color=PINK)
            embed.set_footer(text="Requested by " + str(ctx.author.name),
                        icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=f"http://s.ppy.sh/a/{data_suppl['user_id']}")
            await ctx.send("", embed=embed)
        else:

            desc = [
                "```o.stats top (username/id)```"
                ]
            embed = discord.Embed(title="Invalid username/id", description="\n".join(
                desc), color=RED)
            embed.set_footer(text="Requested by " + str(ctx.author.name),
                icon_url=ctx.author.avatar_url)
            await ctx.send("", embed=embed)

    @stats.command(pass_context=True)
    async def recent(self, ctx, user : str = None):
        logger(ctx, inspect.stack()[0][3], self.BOT_DATA)
        
        if user == None:
            if str(ctx.author.id) in self.CLIENT_DATA:
                user = self.CLIENT_DATA[str(ctx.author.id)]['user_id']
            else:
                desc = [
                "```o.link (username/id)```",
                "or",
                "```o.stats recent (username/id)```"
                ]
                embed = discord.Embed(title="No account linked!", description="\n".join(
                    desc), color=RED)
                embed.set_footer(text="Requested by " + str(ctx.author.name),
                    icon_url=ctx.author.avatar_url)
                await ctx.send("", embed=embed)
                # end method
                return
        
        try:
            b = await ctx.message.guild.fetch_member(user[3:-1])
        except:
            b = None
        
        if b != None:
            user_id = b.id
            if str(user_id) in self.CLIENT_DATA.keys():
                user = self.CLIENT_DATA[str(user_id)]['username']
            else:
                desc = [
                "This user has not linked their osu! account!",
                "Try:",
                "```o.stats recent (osu user)```",
                ]
                embed = discord.Embed(title="Cannot find user!", description="\n".join(
                    desc), color=RED)
                embed.set_footer(text="Requested by " + str(ctx.author.name),
                    icon_url=ctx.author.avatar_url)
                await ctx.send("", embed=embed)
                return

        response = requests.get(f"https://osu.ppy.sh/api/get_user_recent?u={user}&k={OLD_OSU_API}&limit=5")
        data = response.json()

        response_suppl = requests.get(f"https://osu.ppy.sh/api/get_user?u={user}&k={OLD_OSU_API}")
        data_suppl = response_suppl.json()

        if data_suppl != []:
            data_suppl = data_suppl[0]
            
            full_desc = []
            

            for i, play in enumerate(data):

                beatmap_page = requests.get(f"https://osu.ppy.sh/api/get_beatmaps?k={OLD_OSU_API}&b={data[i]['beatmap_id']}")
                beatmap_info = beatmap_page.json()[0]

                accuracy = calculations.accuracy(int(data[i]['count50']), int(data[i]['count100']), int(data[i]['count300']), int(data[i]['countmiss']))
                
                if data[i]['rank'] in play_table:
                    c_emoji = play_table[data[i]['rank']]
                else:
                    c_emoji = ":x:"

                try:
                    current_mods = " ".join([MODS[mod] for mod in fn_bits(int(play['enabled_mods']))])
                except:
                    current_mods = "None"     

                desc = [
                    f"**[{beatmap_info['title']} by {beatmap_info['creator']}](https://osu.ppy.sh/beatmapsets/{beatmap_info['beatmapset_id']}#osu/{play['beatmap_id']})**",
                    f"{c_emoji} {accuracy}%",
                    f"Mods: {current_mods}",
                    f"{beatmap_info['version']} | {round(float(beatmap_info['difficultyrating']),2)}☆",
                    "Date : " + play['date'],
                ]
                full_desc.extend(desc)
                #embed.add_field(name=f"[{beatmap_info['title']} by {beatmap_info['creator']}](https://www.google.com)",value="\n".join(desc),inline=False)

            embed = discord.Embed(title=f"{data_suppl['username']}'s Recent Plays", description="\n".join(
                        full_desc), color=PINK)
            embed.set_footer(text="Requested by " + str(ctx.author.name),
                        icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=f"http://s.ppy.sh/a/{data_suppl['user_id']}")
            await ctx.send("", embed=embed)
        else:

            desc = [
                "```o.stats recent (username/id)```"
                ]
            embed = discord.Embed(title="Invalid username/id", description="\n".join(
                desc), color=RED)
            embed.set_footer(text="Requested by " + str(ctx.author.name),
                icon_url=ctx.author.avatar_url)
            await ctx.send("", embed=embed)
