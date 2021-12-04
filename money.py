import json
import math
import operator
import os
import random
import re
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from io import BytesIO

import discord
import discord.ext
import humanfriendly
import requests
from discord.ext import commands, tasks
from num2words import num2words
from PIL import Image, ImageDraw, ImageFont, ImageOps

import botlib
import costlib
import graph
import imageyoink
import secret_data
import settings
import shop
import sqlbullshit
import utils

null = None
filepath = os.path.abspath(os.path.dirname(__file__))
random.seed(os.urandom(32))
sql = sqlbullshit.sql("data.db", "user")

font = ImageFont.truetype(f"{filepath}/static/font.ttf", size=30)
thiccfont = ImageFont.truetype(f"{filepath}/static/thiccfont.ttf", size=45)

payday = 60 * 60 * 48

img = None


def notation(inp):
    """
    Gets the input and returns {inp} social credits 1% of the time, otherwise ${inp}
    If the input is a whole number, return an int version of it
    Examples:
    2.4: $2.4
    35.2: 35.2 social credits (1% chance)
    5: $5
    """
    inp = round(inp, 2)
    if inp % 1 == 0:
        inp = int(inp)
    if random.uniform(0, 1) < botlib.configs("money", "socialcreditchance"):
        return f"{inp} social credits"
    else:
        return f"${inp}"


def geticon(ctx):
    """geticon
    \nGets the user's icon and writes it to a file in the background

    Parameters
    ----------
    ctx : idfk
            context object
    """
    # Read all the data from the page you get from looking at a user's icon url
    imgdata = requests.get(ctx.author.avatar_url).content
    # Write that juicy binary to a file
    with open(f"{filepath}/static/userimgs/{ctx.author.id}", "wb") as f:
        f.write(imgdata)


def moneyenabled(id):

    if os.path.isfile(f"{filepath}/serversettings/{id}/cashenabled.txt"):
        return False
    else:
        return True


def ranktoid(dbid):
    userrank = sql.get(dbid, "rank")
    rankid = ranks[userrank]
    return rankid  # simply gets a user's id and turns it into their rank's id


# simple function to check if a user can buy something. Price must be an int.
def canbuy(price, id):
    bal = sql.get(id, "money")
    if bal >= price:
        return True
    else:
        return False


def doesexist(ctx):
    if sql.get(ctx.author.id, "money") is None:
        sql.adduser(ctx.author.id)
        sql.set(ctx.author.name, ctx.author.id, "name")
        print(f"Created account for id {ctx.author.id}")
    return True


def taxrate(ctx, val):

    dbid = ctx.author.id
    amount = sql.get(dbid, "loans")
    if amount == 0:
        return val
    elif val < amount:
        reval = round((val / 100) * 30, 2)
        sql.take(val - reval, dbid, "loans")
        return val - reval
    else:
        sql.set(0, dbid, "loans")
        return val - amount


ranks = dict()

with open(f"{filepath}/json/ranks.json", "r") as f:
    d = json.load(f)
    for x in d:
        ranks[int(x)] = d[x]


namestorank = dict()

for x in ranks:
    f = ranks[x]["name"]
    namestorank[(f.lower()).replace(" ", "")] = x
with open(f"{filepath}/json/prices.json", "r") as f:
    j = json.load(f)
    cost = j[-1][1]
    cycle = j[-1][0]
countdown = null
refresh = botlib.configs("stocks", "refresh")
precost = 50
leaderboard = []
lb = null
idtoname = {}
with open(f"{filepath}/json/prices.json") as f:
    prices = json.load(f)

day = 60 * 60 * 24


class money(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cost.start()
        self.IRS.start()

    @commands.check(doesexist)
    @commands.command(aliases=["acc", "balance", "bal", "a"])
    async def account(self, ctx, *, target: discord.Member = null):

        utils.log(ctx)

        if settings.check(ctx.message.guild.id, "get", "economy"):
            # If no target was specified set yourself as the target
            if target == null:
                # Check if you exist
                if sql.doesexist(ctx.author.id):
                    # Set the target id, name and ctx as your own
                    tid = ctx.author.id
                    tname = ctx.author.name
                    tuser = ctx.author
                else:
                    # Create an account if you don't exist
                    sql.adduser(ctx.author.id)
                    sql.set(ctx.author.name, ctx.author.id, "name")
                    # if the user does not have an account, create one
                    await ctx.send("Account created!")
                    return
            else:
                # If the target exists, great! Set the shit
                if sql.doesexist((target.id)):
                    tid = target.id
                    tname = target.name
                    tuser = target
                else:
                    # if the user pings someone who does not have an account, send this
                    await ctx.send("That user does not have an account set up")
                    return
            # Load the path to the user's image, even if it does not exist
            if str(tid) in os.listdir(filepath + "/static/banners"):
                banner = Image.open(f"{filepath}/static/banners/{tid}").convert("RGBA")
            else:
                banner = Image.open(f"{filepath}/static/banner.png").convert("RGBA")
            imagepath = f"{filepath}/static/userimgs/{tuser.id}"

            # If we don't have the user's image, get it
            if str(ctx.author.id) not in os.listdir(f"{filepath}/static/userimgs"):
                await ctx.send("Gathering data...")
                await tuser.avatar_url.save(imagepath)
            # if it does exist, shove their ID in a thread to update the user's icon in the background
            else:
                try:
                    threading.Thread(
                        target=geticon,
                        name=f"Icon finder for {ctx.author.name}",
                        args=(ctx,),
                        daemon=True,
                    ).start()
                # If for some reason we can't get the user's image, use a dummy pic
                except Exception:
                    print("Users image not found")
                    imagepath = filepath + "/static/unknown.png"
            # Open our lovely image. If it doesn't work, fall back to a dummy image
            try:
                img = Image.open(imagepath).convert("RGBA")
            except Exception:
                img = Image.open(filepath + "/static/unknown.png", "RGBA")
            # Bal, stocks, rank and wallet cap variables to make reading this code easier
            bal = round(sql.get(tid, "money"), 2)
            stocks = sql.get(tid, "stocks")
            rank = ranks[sql.get(tid, "rank")]["name"]
            cap = ranks[sql.get(tid, "rank")]["cap"]
            # For some reason, each letter is 27 pixels wide with the dummy thicc font
            namelen = 27 * len(tname)
            # Resize the pfp to a standard size, so we don't get timmy setting his pfp
            # to a 3.8TB image of heavy from tf2 then crashing this whole thing
            img = img.resize((180, 180), Image.ANTIALIAS)
            # Give me a red border and everyone else a black one. Cos I wanna be special.
            if tuser.id in secret_data.admins:
                img = ImageOps.expand(img, border=5, fill="red")
            else:
                img = ImageOps.expand(img, border=5, fill="black")

            # Resize the banner to a set size
            banner = banner.resize((745, 270), Image.ANTIALIAS)
            # Give the banner a nice black border
            banner = ImageOps.expand(banner, border=5, fill="black")

            # Stick the user's icon onto it now
            banner.paste(img, [45, 45])
            # Set up the snake based drawing tablet
            d = ImageDraw.Draw(banner, mode="RGBA")
            # Draw a grey rectangle so we can see if people use a custom banner
            # Create a new plain image
            rect = Image.new("RGBA", (750, 270))
            # Set up the snake based drawing tablet for the rectangle
            rectdraw = ImageDraw.Draw(rect, mode="RGBA")
            # Draw the fucker
            rectdraw.rectangle(
                ((270, 22.5), (722.5, 248.5)),
                fill=(255, 255, 255, 100),
                outline="black",
            )
            # Paste it onto the banner
            banner.paste(rect, mask=rect)
            # Write the user's bal on there
            d.text((282, 75), f"Balance: {notation(bal)}", fill="black", font=font)
            # MMMMM STONKS
            d.text((283, 119), f"Owned stocks: {stocks}", fill="black", font=font)
            # Take a guess what this line does
            d.text((282, 163), f"Rank: {rank}", fill="black", font=font)
            # Add the user's wallet cap
            d.text((285, 208), f"Wallet cap: {notation(cap)}", fill="black", font=font)
            # Write the user's name in dummy thicc font
            d.text((285, 20), tname, fill="black", font=thiccfont)
            # Underline the user's name with some fucky maths
            d.line(((285, 70), ((285 + namelen), 70)), fill=(26, 26, 26), width=5)
            # Waaaa, uploads need to be files whaaaaaa!
            # Suck my fat juicy cock Discord
            with BytesIO() as img_bin:
                banner.save(img_bin, "PNG", optimize=True)
                img_bin.seek(0)
                await ctx.send(file=discord.File(fp=img_bin, filename=f"{tname}.png"))

        else:
            await ctx.send("Sorry, economy is disabled on this server")

    @commands.check(doesexist)
    @commands.command()
    async def pay(self, ctx, amount, target: discord.Member = null):  # paying someone
        if settings.check(ctx.message.guild.id, "get", "economy"):
            # finds the balance of the sender
            urval = int(sql.get(ctx.message.author.id, "money"))
            thrid = target.id  # target's ID
            if sql.doesexist(thrid) is False:
                await ctx.send("That user does not have an account set up")

            elif (
                amount.isnumeric is False
            ):  # if you try paying someone something that isn't a number
                await ctx.send("You need to give me a number")
            elif thrid == ctx.message.author.id:  # if you try paying yourself
                await ctx.send("You can't pay yourself")
            elif int(amount) < 1:
                await ctx.send("You can't pay less than $1 to someone")
            # if either you have less than $1 or you try and pay more than you have
            elif (int(amount) >= urval) or (urval - int(amount) < 0):
                await ctx.send("Sorry, you don't have enough money")
            elif sql.get(thrid, "money") + int(amount) > int(
                ranks[sql.get(thrid, "rank")]["cap"]
            ):
                await ctx.send("Sorry, that goes over their wallet cap")
            else:  # if you can actually pay them
                amount = int(amount)
                sql.take(amount, ctx.author.id, "money")
                sql.add(amount, target.id, "money")
                # inform the person that they were paid
                await ctx.send(f"{notation(amount)} was transferred to {target.name}")
                # send dm to target. Still not working
                await target.send(
                    f"{ctx.message.author} just payed you {notation(amount)}!\n({ctx.guild.name})"
                )
        else:
            await ctx.send("Sorry, economy has been turned off for this server")

    @commands.check(doesexist)
    @commands.command()
    # adds money to an account. Only I can use it
    async def add(self, ctx, arg1, target: discord.Member):
        utils.log(ctx)
        if settings.check(ctx.message.guild.id, "get", "economy"):
            if ctx.message.author.id == 451643725475479552:
                sql.add(float(arg1), target.id, "money")
                await ctx.send(f"\\{notation(float(arg1))} added")
            else:
                await ctx.send("Nope")
        else:
            await ctx.send("Sorry, economy is disabled on this server")

    @commands.check(doesexist)
    @commands.command()
    # adds money to an account. Only I can use it
    async def set(self, ctx, arg1, target: discord.Member):
        utils.log(ctx)
        if settings.check(ctx.message.guild.id, "get", "economy"):
            if ctx.message.author.id == 451643725475479552:
                arg1 = float(arg1)
                sql.set(arg1, target.id, "money")
                await ctx.send(f"Balance set to {notation(arg1)} for {target}")
            else:
                await ctx.send("Nope")
        else:
            await ctx.send("Sorry, economy is disabled on this server")

    @commands.check(doesexist)
    @commands.command()
    # adds money to an account. Only I can use it
    async def setstock(self, ctx, arg1, target: discord.Member):
        utils.log(ctx)
        if settings.check(ctx.message.guild.id, "get", "economy"):
            if ctx.message.author.id == 451643725475479552:
                arg1 = int(arg1)
                sql.set(arg1, target.id, "stocks")
                await ctx.send(f"Stocks set to {arg1} for {target}")
            else:
                await ctx.send("Nope")
        else:
            await ctx.send("Sorry, economy is disabled on this server")

    @commands.check(doesexist)
    @commands.command(pass_context=True)
    @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    async def daily(self, ctx):
        utils.log(ctx)
        if settings.check(ctx.message.guild.id, "get", "economy"):
            if sql.doesexist(int(ctx.message.author.id)):
                r = random.randint(20, 50)
                if (
                    sql.get(ctx.message.author.id, "money") + r
                    <= ranks[sql.get(ctx.author.id, "rank")]["cap"]
                ):
                    amnt = taxrate(ctx, r)
                    sql.add(amnt, ctx.message.author.id, "money")
                    await ctx.send(f"{notation(amnt)} was added to your account")
                else:
                    await ctx.send("Sorry, that goes over your wallet cap")
            else:
                await ctx.send("You do not have an account. Do -account to make one")
        else:
            await ctx.send("Sorry, economy is disabled on this server")

    @daily.error
    async def daily_error(self, ctx, error):
        utils.log(ctx)
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(
                f"You can only do daily once a day. Try again in {humanfriendly.format_timespan(error.retry_after)}"
            )
        else:
            raise error

    @commands.check(doesexist)
    @commands.command(aliases=["stock", "stonk", "stonks"])
    async def stocks(self, ctx, action=null, count=null):
        utils.log(ctx)
        if settings.check(ctx.message.guild.id, "get", "economy"):
            global stock
            global cost
            global countdown
            user = int(ctx.message.author.id)
            if sql.get(user, "stocks") == null:
                await ctx.send("You need to create an account with -account first")
            else:
                if action == "sell":
                    if count == "all":
                        # work out how many the can buy with their currant bal and then set that to the number they are trying to buy
                        count = int(sql.get(user, "stocks"))
                        if count <= 0:
                            await ctx.send("Sorry, you don't own any stocks")
                elif action == "buy":
                    if count == "all":
                        bal = sql.get(user, "money")
                        # if "all" is used, work out how many they can sell buy just setting number to sell as how many stocks they own
                        count = math.floor(bal / cost)
                        if count <= 0:
                            await ctx.send("Sorry, you can't afford any stocks")
                            return

                stockcount = sql.get(user, "stocks")
                bal = sql.get(ctx.message.author.id, "money")
                try:
                    timeto = countdown - datetime.now()
                except NameError:
                    pass
                if action == null:
                    comment = botlib.stockcomment(ctx, cost)
                    if comment[0] == "url":
                        await ctx.send(
                            f"Current price of stocks: **{notation(cost)}**\nYou currently own {stockcount} stocks\nTime until stock price change: {humanfriendly.format_timespan(timeto)}"
                        )
                        await ctx.send(comment[1])
                    else:
                        await ctx.send(
                            f"Current price of stocks: **{notation(cost)}**\nYou currently own {stockcount} stocks\nTime until stock price change: {humanfriendly.format_timespan(timeto)}{comment}"
                        )  # if no options are specified, show current price and hw many the user owns.
                else:
                    count = int(count)
                    fcost = round((float(count) * cost), 2)
                    if count <= 0:
                        await ctx.send(
                            "You need to enter a number that is over 0"
                        )  # if they own no stocks or can't afford any when using "all", or they try and enter a number below 1. Can't buy 0 stocks or negative stocks
                    elif action == "buy" and (fcost > bal):
                        # if they can't afford the number of stocks they specified
                        await ctx.send("You don't have enough money")
                    elif (action == "sell") and (count > int(stockcount)):
                        # if they try sell more stocks than they own.
                        await ctx.send("You don't own that many stocks")
                    elif action == "buy":
                        sql.take(taxrate(ctx, fcost), user, "money")
                        sql.add(count, user, "stocks")
                        # if they can actually buy stocks, run this to do all the account manipulaion.
                        await ctx.send(f"{count} stocks bought for {notation(fcost)}")
                    elif action == "sell":
                        # Makes sure that the sold stocks won't exceed the wallet cap of their rank.
                        if (
                            sql.get(ctx.message.author.id, "money") + fcost
                            <= ranks[sql.get(user, "rank")]["cap"]
                        ):
                            sql.add(taxrate(ctx, fcost), user, "money")
                            sql.take(count, user, "stocks")
                            await ctx.send(f"{count} stocks sold for {notation(fcost)}")
                        else:
                            c = 1
                            while (
                                cost * c + bal
                                < ranks[sql.get(ctx.author.id, "rank")]["cap"]
                            ):
                                c += 1
                            count = c - 1
                            fcost = cost * count

                            sql.add(taxrate(ctx, fcost), user, "money")
                            sql.take(count, user, "stocks")
                            await ctx.send(
                                f"Since that amount of sold stocks would go over your wallet cap, you are only selling {count} stocks for {notation(fcost)}"
                            )
                    elif action == "calc":
                        await ctx.send(
                            # simply calculates how much the specified stocks would cost.
                            f"{count} stocks at {notation(cost)} is worth ${round((count * cost), 2)}"
                        )
        else:
            await ctx.send("Sorry, economy is disabled on this server")

    @commands.command()
    async def stockset(self, ctx, arg):
        utils.log(ctx)
        if ctx.message.author.id == 451643725475479552:
            global cost
            cost = float(arg)
            await ctx.send(f"Stock price set to {arg}")

    @commands.check(doesexist)
    @commands.command(aliases=["ranks"])
    async def rank(self, ctx, ag1=null, rank=null):  # allows someone to buy a rank
        if settings.check(ctx.message.guild.id, "get", "economy"):
            global ranks, namestorank  # idk if this is needed but it can't hurt to have it
            # "user" is easier to type than "ctx.message.author.id"
            user = ctx.message.author.id
            if ag1 != "buy":  # if they don't have "buy" as their first arg, send prices
                embed = discord.Embed(
                    title="Ranks",
                    description="The price of different ranks",
                    color=0x1E00FF,
                )
                embed.set_thumbnail(
                    url="https://lh3.googleusercontent.com/proxy/07h14DsTB_1a1UudwyVJz7OICAz9RSOE0uLEI3ox3vFTdjvM4hJolKhXaAEk0UeSeE2V92Qgv8ScFee0Zm9GoR-VKc6EadFPwYIVw93O6-EiSvI"
                )
                for x in namestorank:
                    if x != "bronze":
                        # loops through all the ranks so I don't have to hardcode it
                        embed.add_field(
                            name=ranks[namestorank[x]]["name"],
                            value=f"${ranks[namestorank[x]]['price']}",
                            inline=True,
                        )
                embed.set_footer(text='Use "-rank buy [rank name]" to buy a rank')
                await ctx.send(embed=embed)
            else:  # if they do have it, start doing stuff
                crank = sql.get(int(user), "rank")
                crankv = ranks[crank]["price"]
                if rank not in namestorank:
                    await ctx.send("That rank doesn't exist")
                    return
                val = ranks[namestorank[rank]]["price"]
                if rank == null:
                    # if they don't enter a rank to buy
                    await ctx.send("Please choose a rank to buy")
                elif (rank.lower() in namestorank) is False:
                    # if the rank does not appear in the ranks list (dict)
                    await ctx.send("That was not a valid rank")
                elif canbuy(val, user) is False:
                    # explains itself
                    await ctx.send("You do not have enough money to buy this")
                elif crankv > val:
                    await ctx.send("You can't buy a lower rank")
                elif crankv == int(ranks[namestorank[rank.lower()]]["price"]):
                    await ctx.send("You can't buy your current rank")
                else:
                    cost = (
                        0 - val
                    )  # turn the value into a negative so you can buy it properly
                    rnum = namestorank[rank]
                    sql.set(rnum, user, "rank")
                    # takes the money from the account (adds a negative value)
                    sql.add(cost, user, "money")
                    # let them know
                    await ctx.send(f"Rank {rank} was bought for {notation(val)}")
        else:
            await ctx.send("Sorry, economy is disabled on this server")

    @commands.check(doesexist)
    @commands.command(aliases=["leaderboard", "leader", "board"])
    # command to create a leaderboard of the 5 richest users.
    async def lb(self, ctx):
        utils.log(ctx)
        # since turning the user ids to usernames is pretty slow, it is recompiled every 10 mins
        global leaderboard
        global lb
        global idtoname
        global ranks
        leaderboard = []
        lb = null
        lb = discord.Embed(
            title="Leaderboard", description="Current leaderboard", color=0xFFD700
        )
        db = sqlite3.Connection(filepath + "/data.db")
        cur = db.cursor()
        cur.execute("select id,money,stocks from user")
        resp = cur.fetchall()
        for id, money, stocks in resp:
            totalval = (money) + (int(stocks) * cost)
            totalval = totalval + ranks[sql.get(id, "rank")]["price"]
            totalval = round(totalval, 2)
            leaderboard.append((id, totalval))

        leaderboard = sorted(
            leaderboard,  # sorts the net worths of everyone into order.
            key=operator.itemgetter(1),
            reverse=True,
        )
        c = 0
        count = 1
        for x in leaderboard:
            if x[0] == ctx.message.author.id:
                break
            count = count + 1
        for x in leaderboard:
            c = c + 1
            if c <= 5:  # makes sure you only get the first 5 results.
                try:
                    lb.add_field(
                        name=idtoname[x[0]], value=f"${x[1]}", inline=False
                    )  # tries to get the username from the precompiled list
                except KeyError:
                    lb.add_field(
                        name=await self.bot.fetch_user(x[0]),
                        value=f"${x[1]}",
                        inline=False,
                    )  # if it can't, just work it out on the fly.
        lb.set_footer(
            # turns the number into a placing. eg; 2 becomes 2nd, 5 becomes 5th, ect.
            text=f"Your position: {num2words(count, to='ordinal_num')} out of {len(leaderboard)}"
        )
        await ctx.send(embed=lb)

    # IDEA: How do players get materials to sell? If anyone can get the materials easily, there is no point in having shops so it needs an element of randomness. Myabe a lootbox sort of system? That could be interesting. Another option is you do stuff like -mine or -cut to get base materials. The base materials can then be crafted into more advanced stuff. -mine and -cut would have a cooldown. Also doing -mine would yeild stone, a small bit of metal, and very rarely gems. This way you have an element of randomness but can still be player directed. This could be interesting but would need HEAVY balancing.
    # IDEA: the shops could be set up in a way so a new shop database is added and inside is this structure: {top level of dict: {user1id: [{item1: [amount, price]}, {item2: [amount, price]}]}}. This is a bit confusing but it would be a much more compact version of what it could be. Since it is using a database, it means we can use tinyDB's search function so people can search by user, item and price. I would also have a precompiled dict of everyone's id to their username so it doesn't lag heaps when opening the store and it has to find the name of every ID.
    # IDEA: Possible idea is that people can run stores and shops as separate things. When you make a store you can set the tax rate (What percentage of the selling price will go to your account) for people's stalls. Less tax rate on stores would be more popular but you would get a lot more competition. It would be a decent way for people to earn money if they can afford it but don't wanna grind out materials. This needs some heavy refinement and won't be implemented straight away but could be an interesting idea for the future.
    # IDEA: I would also need to divide shops up into pages. So we don't get every shop on 1 embed, it would shop 10 items at once and then you would go to the next page. Maybe bugger about with the menus lib? The method of doing this would probably be to compile the items into a list then devide it into a lot of parts, each made up of 10 items. Then add each one to a dict with the key being a number that increases for each page there is. Then just call that page number and loop throught the value to create an embed field. Might be pretty intense and I can't really precompile it but it would live update. I would also run a function every 10 mins to prune all shops with an item count of 0.
    @commands.check(doesexist)
    @commands.command(aliases=["inventory", "i"])
    async def inv(self, ctx):
        utils.log(ctx)
        try:
            user = ctx.message.author
            head, sep, tail = str(user).partition("#")
            uitems = shop.owneditems(ctx.message.author.id)[str(ctx.message.author.id)]
            embed = discord.Embed(
                title=f"{head}'s Items", description="Owned items", color=0x8800FF
            )
            embed.set_thumbnail(url=user.avatar_url)
            for x in uitems:
                embed.add_field(name=x, value=uitems[x], inline=True)
            await ctx.send(embed=embed)
        except Exception:
            await ctx.send("Your inventory is empty")

    @commands.check(doesexist)
    @commands.command(aliases=["price", "p"])
    async def prices(self, ctx):
        utils.log(ctx)
        global prices
        global img
        if img is None:
            img = graph.create(prices[-288:])
        with BytesIO() as img_bin:
            img.save(img_bin, format="PNG")
            img_bin.seek(0)
            await ctx.send(
                file=discord.File(fp=img_bin, filename=f"{prices[-1][0]}.png")
            )

    v = 50

    @tasks.loop(minutes=refresh)
    async def cost(self):
        global cost
        global refresh
        global cycle
        global countdown
        global img
        print(f"Refresh: {refresh}")

        countdown = datetime.now() + timedelta(minutes=refresh)
        cycle = cycle + 1
        cost = costlib.gencost(cost)
        prices.append((cycle, cost))
        img = None
        while len(prices) > (60 * 24 * 2) / refresh:
            prices.pop(0)
        with open(f"{filepath}/json/prices.json", "w") as f:
            json.dump(prices, f, sort_keys=True, indent=4)

        print(f"stock price is {notation(cost)}\nCycle is {cycle}")
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"Stock price at {notation(cost)}",
            )
        )
        if cycle > 1:
            for x in sql.getall("id", mode="field"):
                user = await self.bot.fetch_user(x[0])
                idtoname[x[0]] = user.name

    @commands.command()
    async def banner(self, ctx, *, args: str = None):
        utils.log(ctx)
        if args is None:
            await ctx.send("Please enter a url")
            return
        bal = sql.get(ctx.author.id, "money")
        if bal >= 1000:
            url = imageyoink.sorter(args)
            if url is not False:
                size = int(requests.get(url, stream=True).headers["Content-length"])
                if size > 50000000:
                    await ctx.send("That image is too big")
                    return
                data = requests.get(url).content
                f = open(filepath + "/static/banners/" + str(ctx.author.id), "wb")
                f.write(data)
                f.close()
                await ctx.send("Banner image was updated!")
                sql.take(1000, ctx.author.id, "money")
            else:
                await ctx.send("That is not a valid image")
        else:
            await ctx.send("Not enough money")

    @commands.command(aliases=["loans", "carwarranty"])
    async def loan(self, ctx, inp1=None, inp2=None, inp3=None):
        utils.log(ctx)
        loanrate = 15
        bal = sql.get(ctx.author.id, "money")
        owed = sql.get(ctx.author.id, "loans")
        cs = sql.get(ctx.author.id, "creditscore")
        loancap = ranks[sql.get(ctx.author.id, "rank")]["loancap"]

        reg = re.compile(r"\d+\.?\d*")

        with open(f"{filepath}/json/taxes.json", "r") as r:
            r = json.load(r)
            if str(ctx.author.id) in r:
                unpaid = r[str(ctx.author.id)]["amount"]
            else:
                unpaid = 0
            if inp1 == "take":
                if inp2 is None:
                    await ctx.send("Please give an amount")
                    return
                isnum = False if reg.search(inp2) is None else True
                if isnum:
                    inp2 = reg.search(inp2).group(0)
                    val = float(inp2)
                    if val > loancap:
                        await ctx.send(
                            f"Sorry, that goes over your loan cap ({notation(loancap)})"
                        )
                        return

                    if owed > 200:
                        await ctx.send(
                            "Sorry, you already owe a fair bit of money. Pay some off then try later."
                        )
                    elif cs <= -25:
                        await ctx.send("Sorry, your credit score is too low.")
                    else:
                        if val < 1:
                            await ctx.send("You can't take out that amount")
                            return
                        tax = (val / 100) * loanrate
                        if str(ctx.author.id) in r:
                            loancost = owed + val + tax
                            r[str(ctx.author.id)]["amount"] = unpaid + loancost
                            sql.add(val, ctx.author.id, "money")
                            await ctx.send(
                                f"You took out a loan of {notation(val)}. You have 2 days to pay it off, plus a {loanrate}% fee."
                            )
                        else:
                            loancost = val + tax
                            r[str(ctx.author.id)] = {
                                "amount": val + tax,
                                "time": time.time(),
                            }
                            sql.add(val, ctx.author.id, "money")
                            await ctx.send(
                                f"You took out a loan of {notation(val)}. You have 2 days to pay it off, plus a {loanrate}% fee."
                            )
                else:
                    await ctx.send("That was not a valid input")
            elif inp1 == "pay":
                if inp2 is None:
                    await ctx.send("Please give an amount")
                    return
                if (str(ctx.author.id) not in r) and (
                    sql.get(ctx.author.id, "loans") <= 0
                ):
                    await ctx.send("You don't have any loans dumbass")
                    return
                if inp2 is None:
                    if bal < unpaid and bal < owed:
                        await ctx.send(
                            f"Sorry, you don't have enough to pay off the loan. You need another {notation(owed - bal)}"
                        )
                    else:
                        if bal >= unpaid and unpaid != 0:
                            r.pop(str(ctx.author.id))
                            sql.take(unpaid, ctx.author.id, "money")
                            await ctx.send("You just paid off your loan! Well done!")
                        elif bal >= owed:
                            sql.set(0, ctx.author.id, "loans")
                            sql.take(owed, ctx.author.id, "money")
                            await ctx.send("You just paid off your debt! Well done!")
                else:
                    isnum = False if reg.search(inp2) is None else True
                    if isnum is False:
                        await ctx.send("That was not a valid input")
                    else:
                        inp2 = reg.search(inp2).group(0)
                        amount = float(inp2)
                        if amount < 1:
                            await ctx.send(
                                f"Sorry, you can't pay less than {notation(1)}"
                            )

                        else:
                            if unpaid > 0:
                                if amount < unpaid:
                                    r[str(ctx.author.id)]["amount"] = unpaid - amount
                                    sql.take(amount, ctx.author.id, "money")
                                    await ctx.send(
                                        f"Well done, you just paid off {notation(amount)} of your loan!"
                                    )
                                else:
                                    r.pop(str(ctx.author.id))
                                    sql.take(unpaid, ctx.author.id, "money")
                                    await ctx.send(
                                        "You just paid off your loan! Well done!"
                                    )
                            else:
                                if amount < owed:
                                    sql.take(amount, ctx.author.id, "loans")
                                    sql.take(amount, ctx.author.id, "money")
                                    await ctx.send(
                                        f"Well done, you just paid off {notation(amount)} of your debt!"
                                    )
                                else:
                                    sql.set(0, ctx.author.id, "loans")
                                    sql.take(owed, ctx.author.id, "money")
                                    await ctx.send(
                                        "Well done, you just paid off of your debt!"
                                    )

            else:
                # Send the user a nice embed to show them their current loans
                if str(ctx.author.id) not in r and owed == 0:
                    await ctx.send("You don't have any loans")
                else:

                    if unpaid > 0:
                        timeremaining = time.strftime(
                            "%H:%M:%S",
                            time.gmtime(r[str(ctx.author.id)]["time"] - time.time()),
                        )
                        embed = discord.Embed(
                            title=f"{ctx.author.name}'s Loans",
                            description=f"You have a loan of {notation(unpaid)} due in {timeremaining}",
                            color=discord.Color.blue(),
                        )
                        if owed > 0:
                            embed.add_field(
                                name="You also owe", value=f"{notation(owed)}"
                            )
                    else:
                        embed = discord.Embed(
                            title=f"{ctx.author.name}'s debt",
                            description=f"You have a debt of {notation(owed)}.",
                            color=discord.Color.blue(),
                        )
                    embed.add_field(name="Credit score", value=cs)
                    embed.set_footer(text=f"You have {notation(round(bal, 2))}")
                    await ctx.send(embed=embed)

            with open(f"{filepath}/json/taxes.json", "w") as j:
                json.dump(r, j)

    @tasks.loop(seconds=day)
    async def IRS(self):
        with open(filepath + "/json/taxes.json") as f:
            if os.path.getsize(f"{filepath}/json/taxes.json") == 0:
                with open(filepath + "/taxes.json", "w") as fw:
                    ob = {"0": -1}
                    json.dump(ob, fw)
            f = json.load(f)
            f = dict(f)
            droppers = []
            for x in f:
                if x != "0":
                    amount = f[x]["amount"]
                    t = f[x]["time"]
                    if t < time.time() + payday:
                        sqlt = sqlbullshit.sql("data.db", "user")
                        try:
                            sqlt.add(amount, int(x), "loans")
                            droppers.append(x)
                            user = self.bot.get_user(int(x))
                            name = await self.bot.fetch_user(int(x))
                            name = name.display_name
                            if random.randint(0, 100) == 1:
                                msg = f"Hello {name}, we have been trying to reach you about your car's extended warrenty. Please check in with us by running -carwarranty"
                            else:
                                msg = f"""So, {name}, I hear you haven't paid back your loan of {notation(amount)}. Good for you, I'm in a nice mood.
\nI'm going to start just taking your money, kapish? It's that or your kneecaps.
\nDon't make me send Vinny around again. I hope you remember what happened to your kids last time."""
                            await user.send(msg)
                        except sqlbullshit.SQLerror:
                            user = self.bot.get_user(int(451643725475479552))
                            await user.send(
                                f"A user with the id {x} has caused problems by not existing. pls fix"
                            )
            for x in droppers:
                f.pop(x)
            droppers = list()
            with open(filepath + "/taxes.json", "w") as fw:
                json.dump(f, fw)


def setup(bot: commands.Bot):
    bot.add_cog(money(bot))
