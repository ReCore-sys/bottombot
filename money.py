from ast import alias
import json
import math
import operator
import os
import random
from datetime import date, datetime, timedelta
import sqlite3
import secret_data
import threading
import requests

import discord
from PIL import Image, ImageDraw, ImageFont, ImageOps
import discord.ext
import humanfriendly
import matplotlib.pyplot as plt
from discord.ext import commands, tasks
from num2words import num2words
from io import BytesIO

import botlib
import settings
import shop
import sqlbullshit

null = None
filepath = os.path.abspath(os.path.dirname(__file__))
random.seed(15)
sql = sqlbullshit.sql("data.db", "user")

font = ImageFont.truetype(f"{filepath}/static/font.ttf", size=35)
thiccfont = ImageFont.truetype(f"{filepath}/static/thiccfont.ttf", size=45)


def geticon(ctx):
    """geticon
    \nGets the user's icon and writes it to a file in the background

    Parameters
    ----------
    ctx : ¯\\\_(ツ)_/¯
        context object
    """
    # Read all the data from the page you get from looking at a user's icon url
    imgdata = requests.get(ctx.author.avatar_url).content
    # Write that juicy binary to a file
    with open(f"{filepath}/static/userimgs/{ctx.author.id}", "wb") as f:
        f.write(imgdata)


def stockfind(dbid):  # function to find how many stock a person owns
    return sql.get(dbid, "stocks")


def moneyenabled(id):
    if os.path.isfile(
            f"{filepath}/serversettings/{id}/cashenabled.txt") == True:
        return False
    else:
        return True


def addstock(
    user, amount
):  # Slightly less simple function to add money to a user's balance. Use negative numbers to remove money
    return sql.add(amount, user, "stocks")


def balfind(dbid):  # function to find the balance of the id dbid
    return sql.get(dbid, "money")


def rankfind(dbid):  # same as above but for ranks, not bal
    ranknum = sql.get(dbid, "rank")
    return ranknum


def ranktoid(dbid):
    userrank = rankfind(dbid)
    rankid = ranks[userrank]
    return rankid  # simply gets a user's id and turns it into their rank's id


# simple function to check if a user can buy something. Price must be an int.
def canbuy(price, id):
    bal = balfind(id)
    if bal >= price:
        return True
    else:
        return False


def addmoney(
    user, amount
):  # Slightly less simple function to add money to a user's balance. Use negative numbers to remove money
    sql.add(amount, user, "money")


def doesexist(ctx):
    if sql.get(ctx.author.id, "money") == None:
        sql.adduser(ctx.author.id)
        sql.set(ctx.author.name, ctx.author.id, "name")
        print(f"Created account for id {ctx.author.id}")
    return True


ranks = {
    1: {
        "price": 0,
        "name": "Bronze",
        "cap": 1000
    },
    2: {
        "price": 750,
        "name": "Silver",
        "cap": 7500
    },
    3: {
        "price": 1500,
        "name": "Gold",
        "cap": 12000
    },
    4: {
        "price": 5000,
        "name": "Platinum",
        "cap": 25000
    },
    5: {
        "price": 10000,
        "name": "Diamond",
        "cap": 100000
    },
    6: {
        "price": 20000,
        "name": "Demigod",
        "cap": 75000
    },
    7: {
        "price": 50000,
        "name": "Immortal",
        "cap": 175000
    },
    8: {
        "price": 100000,
        "name": "Ascendant",
        "cap": 200000
    },
    9: {
        "price": 150000,
        "name": "Tax Man",
        "cap": 200000
    }

}
v = 50
loops = 10000
upchance = 1
downchance = 10
decay = 0.2
reducedecay = 0.999
decays = []

namestorank = dict()

for x in ranks:
    f = ranks[x]["name"]
    namestorank[(f.lower()).replace(" ", "")] = x

cost = 50
countdown = null
refresh = 10
cycle = 0
precost = 50
leaderboard = []
lb = null
idtoname = {}
prices = list()


class money(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cost.start()

    # shows the user's account

    @commands.check(doesexist)
    @commands.command(aliases=["acc", "balance", "bal", "a"])
    async def account(self, ctx, *, target: discord.Member = null):
        banner = Image.open(f"{filepath}/static/banner.png")
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
            imagepath = f"{filepath}/static/userimgs/{tuser.id}"

            # If we don't have the user's image, get it
            if str(ctx.author.id) not in os.listdir(f"{filepath}/static/userimgs"):
                await ctx.send("Gathering data...")
                await tuser.avatar_url.save(imagepath)
            # if it does exist, shove their ID in a thread to update the user's icon in the background
            else:
                try:
                    threading.Thread(target=geticon,
                                     name=f"Icon finder for {ctx.author.name}", args=(ctx,), daemon=True).start()
                # If for some reason we can't get the user's image, use a dummy pic
                except:
                    print("Users image not found")
                    imagepath = filepath + "/static/unknown.png"
            # Open our lovely image
            img = Image.open(imagepath)
            # Bal, stocks and rank variables to make reading this code easier
            bal = round(sql.get(tid, "money"), 2)
            stocks = stockfind(tid)
            rank = ranks[rankfind(tid)]["name"]
            # For some reason, each letter is 27 pixels wide with the dummy thicc font
            namelen = 27*len(tname)
            # Resize the pfp to a standard size, so we don't get timmy setting his pfp
            # to a 3.8TB image of heavy from tf2 then crashing this whole thing
            img = img.resize((178, 178))
            # Give me a red border and everyone else a black one. Cos I wanna be special.
            if tuser.id in secret_data.admins:
                img = ImageOps.expand(img, border=5, fill='red')
            else:
                img = ImageOps.expand(img, border=5, fill='black')

            # Resize the banner to a set size
            banner = banner.resize((735, 268))

            # Stick the user's icon onto it now
            banner.paste(img, [45, 45])
            # Set up the snake based drawing tablet
            d = ImageDraw.Draw(banner)
            # Write the user's bal on there
            d.text((250, 75), f"Balance: ${bal}", fill="black", font=font)
            # MMMMM STONKS
            d.text(
                (250, 120), f"Owned stocks: {stocks}", fill="black", font=font)
            # Take a guess what this line does
            d.text((250, 165), f"Rank: {rank}", fill="black", font=font)
            # Write the user's name in dummy thicc font
            d.text((390-namelen/2, 20), tname, fill="black", font=thiccfont)
            # Underline the user's name with some fucky maths
            d.line(((390-namelen/2, 70), ((390 + namelen/2), 70)),
                   fill=(26, 26, 26), width=5)
            # Waaaa, uploads need to be files whaaaaaa!
            # Suck my fat juicy cock Discord
            with BytesIO() as img_bin:
                banner.save(img_bin, 'PNG')
                img_bin.seek(0)
                await ctx.send(file=discord.File(fp=img_bin, filename=f'{tname}.png'))

        else:
            await ctx.send("Sorry, economy is disabled on this server")

    @commands.check(doesexist)
    @commands.command()
    async def pay(self,
                  ctx,
                  arg1,
                  target: discord.Member = null):  # paying someone
        if settings.check(ctx.message.guild.id, "get", "economy"):
            # finds the balance of the sender
            urval = int(balfind(ctx.message.author.id))
            # finds the bal of the target
            thrval = int(balfind(int(target.id)))
            thrid = target.id  # target's ID
            if target == null:
                # if that user's balance is null, they don't exist
                await ctx.send(
                    "Sorry, that person either does not exist or has not set up their account."
                )
            elif arg1.isnumeric == False:  # if you try paying someone something that isn't a number
                await ctx.send("You need to give me a number")
            elif thrid == ctx.message.author.id:  # if you try paying yourself
                await ctx.send("You can't pay yourself")
            elif int(arg1) < 1:
                await ctx.send("You can't pay less than $1 to someone")
            # if either you have less than $1 or you try and pay more than you have
            elif (int(arg1) >= urval) or (urval - int(arg1) < 0):
                await ctx.send("Sorry, you don't have enough money")
            elif balfind(thrid) + int(arg1) > int(ranks[rankfind(thrid)]['cap']):
                await ctx.send("Sorry, that goes over their wallet cap")
            else:  # if you can actually pay them
                arg1 = int(arg1)
                sql.take(arg1, ctx.author.id, "money")
                sql.add(arg1, target.id, "money")
                # inform the person that they were paid
                await ctx.send(f"${arg1} was transferred to <@!{target.id}>")
                # send dm to target. Still not working
                await target.send(
                    f"{ctx.message.author} just payed you ${arg1}!\n({ctx.guild.name})"
                )
        else:
            await ctx.send("Sorry, economy has been turned off for this server"
                           )

    @commands.check(doesexist)
    @commands.command()
    # adds money to an account. Only I can use it
    async def add(self, ctx, arg1, target: discord.Member):
        if settings.check(ctx.message.guild.id, "get", "economy"):
            if ctx.message.author.id == 451643725475479552:
                sql.add(float(arg1), target.id, "money")
                await ctx.send(f"${arg1} added")
            else:
                await ctx.send("Nope")
        else:
            await ctx.send("Sorry, economy is disabled on this server")

    @commands.check(doesexist)
    @commands.command()
    # adds money to an account. Only I can use it
    async def set(self, ctx, arg1, target: discord.Member):
        if settings.check(ctx.message.guild.id, "get", "economy"):
            if ctx.message.author.id == 451643725475479552:
                arg1 = float(arg1)
                sql.set(arg1, target.id, "money")
                await ctx.send(f"Balance set to ${arg1} for {target}")
            else:
                await ctx.send("Nope")
        else:
            await ctx.send("Sorry, economy is disabled on this server")

    @commands.check(doesexist)
    @commands.command()
    # adds money to an account. Only I can use it
    async def setstock(self, ctx, arg1, target: discord.Member):
        if settings.check(ctx.message.guild.id, "get", "economy"):
            if ctx.message.author.id == 451643725475479552:
                arg1 = float(arg1)
                sql.set(arg1, target.id, "stock")
                await ctx.send(f"Stocks set to {arg1} for {target}")
            else:
                await ctx.send("Nope")
        else:
            await ctx.send("Sorry, economy is disabled on this server")

    @commands.check(doesexist)
    @commands.command(pass_context=True)
    @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    async def daily(self, ctx):
        if settings.check(ctx.message.guild.id, "get", "economy"):
            if balfind != null:
                r = random.randint(20, 50)
                if balfind(ctx.message.author.id) + r <= ranks[rankfind(ctx.author.id)]['cap']:
                    addmoney(ctx.message.author.id, r)
                    await ctx.send(f"${r} was added to your account")
                else:
                    await ctx.send("Sorry, that goes over your wallet cap")
            else:
                await ctx.send(
                    "You do not have an account. Do -account to make one")
        else:
            await ctx.send("Sorry, economy is disabled on this server")

    @daily.error
    async def daily_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(
                f"You can only do daily once a day. Try again in {humanfriendly.format_timespan(error.retry_after)}"
            )

    @commands.check(doesexist)
    @commands.command(aliases=["stock", "stonk", "stonks"])
    async def stocks(self, ctx, action=null, count=null):
        if settings.check(ctx.message.guild.id, "get", "economy"):
            global stock
            global cost
            global countdown
            user = int(ctx.message.author.id)
            if stockfind(user) == null:
                await ctx.send(
                    "You need to create an account with -account first")
            else:
                if action == "sell":
                    if count == "all":
                        # work out how many the can buy with their currant bal and then set that to the number they are trying to buy
                        count = stockfind(user)
                elif action == "buy":
                    if count == "all":
                        bal = balfind(user)
                        # if "all" is used, work out how many they can sell buy just setting number to sell as how many stocks they own
                        count = math.floor(bal / cost)

                stockcount = stockfind(user)
                bal = balfind(ctx.message.author.id)
                try:
                    timeto = countdown - datetime.now()
                except:
                    pass
                if action == null:
                    await ctx.send(
                        f"Current price of stocks: **${cost}**\nYou currently own {stockcount} stocks\nTime until stock price change: {humanfriendly.format_timespan(timeto)}"
                    )  # if no options are specified, show current price and hw many the user owns.
                else:
                    count = int(count)
                    fcost = round((float(count) * cost), 2)
                    if count <= 0:
                        await ctx.send(
                            "You need to enter a number that is over 0")  # if they own no stocks or can't afford any when using "all", or they try and enter a number below 1. Can't buy 0 stocks or negative stocks
                    elif action == "buy" and (fcost > bal):
                        # if they can't afford the number of stocks they specified
                        await ctx.send("You don't have enough money")
                    elif (action == "sell") and (count > int(stockcount)):
                        # if they try sell more stocks than they own.
                        await ctx.send("You don't own that many stocks")
                    elif action == "buy":
                        addmoney(user, (0 - fcost))
                        addstock(user, count)
                        # if they can actually buy stocks, run this to do all the account manipulaion.
                        await ctx.send(f"{count} stocks bought for ${fcost}")
                    elif action == "sell":
                        # Makes sure that the sold stocks won't exceed the wallet cap of their rank.
                        if balfind(ctx.message.author.id) + fcost <= ranks[rankfind(user)]['cap']:
                            addmoney(user, fcost)
                            addstock(user, (0 - count))
                            await ctx.send(f"{count} stocks sold for ${fcost}")
                        else:
                            await ctx.send(
                                "Sorry, that goes over your wallet cap")
                    elif action == "calc":
                        await ctx.send(
                            # simply calculates how much the specified stocks would cost.
                            f"{count} stocks at ${cost} is worth ${round((count * cost), 2)}"
                        )
        else:
            await ctx.send("Sorry, economy is disabled on this server")

    @commands.check(doesexist)
    @commands.command(aliases=["ranks"])
    async def rank(self,
                   ctx,
                   ag1=null,
                   rank=null):  # allows someone to buy a rank
        if settings.check(ctx.message.guild.id, "get", "economy"):
            global ranks, namestorank  # idk if this is needed but it can't hurt to have it
            # "user" is easier to type than "ctx.message.author.id"
            user = ctx.message.author.id
            if ag1 != "buy":  # if they don't have "buy" as their first arg, send prices
                embed = discord.Embed(
                    title="Ranks",
                    description="The price of different ranks",
                    color=0x1e00ff)
                embed.set_thumbnail(
                    url="https://lh3.googleusercontent.com/proxy/07h14DsTB_1a1UudwyVJz7OICAz9RSOE0uLEI3ox3vFTdjvM4hJolKhXaAEk0UeSeE2V92Qgv8ScFee0Zm9GoR-VKc6EadFPwYIVw93O6-EiSvI"
                )
                for x in namestorank:
                    if x != "bronze":
                        # loops through all the ranks so I don't have to hardcode it
                        embed.add_field(name=ranks[namestorank[x]]["name"],
                                        value=f"${ranks[namestorank[x]]['price']}",
                                        inline=True)
                embed.set_footer(
                    text='Use "-rank buy [rank name]" to buy a rank')
                await ctx.send(embed=embed)
            else:  # if they do have it, start doing stuff
                crank = rankfind(int(user))
                crankv = ranks[crank]["price"]
                val = ranks[namestorank['rank']]["price"]
                if rank == null:
                    # if they don't enter a rank to buy
                    await ctx.send("Please choose a rank to buy")
                elif (rank.lower() in namestorank) == False:
                    # if the rank does not appear in the ranks list (dict)
                    await ctx.send("That was not a valid rank")
                elif canbuy(val, user) == False:
                    # explains itself
                    await ctx.send("You do not have enough money to buy this")
                elif crankv > val:
                    await ctx.send("You can't buy a lower rank")
                elif crankv == int(ranks[rank.lower()]):
                    await ctx.send("You can't buy your current rank")
                else:
                    cost = 0 - val  # turn the value into a negative so you can buy it properly
                    rnum = namestorank[rank]
                    sql.set(rnum, user, "rank")
                    # takes the money from the account (adds a negative value)
                    addmoney(user, cost)
                    # let them know
                    await ctx.send(f"Rank {rank} was bought for ${val}")
        else:
            await ctx.send("Sorry, economy is disabled on this server")

    @commands.check(doesexist)
    @commands.command(aliases=["leaderboard", "leader", "board"])
    # command to create a leaderboard of the 5 richest users.
    async def lb(self, ctx):
        # since turning the user ids to usernames is pretty slow, it is recompiled every 10 mins
        global leaderboard
        global lb
        global idtoname
        global ranks
        leaderboard = []
        lb = null
        lb = discord.Embed(title="Leaderboard",
                           description="Current leaderboard",
                           color=0xFFD700)
        db = sqlite3.Connection(filepath + "/data.db")
        cur = db.cursor()
        cur.execute("select id,money,stocks from user")
        resp = cur.fetchall()
        for id, money, stocks in resp:
            totalval = (money) + (int(stocks) * cost)
            totalval = totalval + ranks[rankfind(id)]["price"]
            totalval = round(totalval, 2)
            leaderboard.append((id, totalval))

        leaderboard = sorted(leaderboard,  # sorts the net worths of everyone into order.
                             key=operator.itemgetter(1),
                             reverse=True)
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
                    lb.add_field(name=idtoname[x[0]],
                                 value=f"${x[1]}",
                                 inline=False)  # tries to get the username from the precompiled list
                except:
                    lb.add_field(name=await self.bot.fetch_user(x[0]),
                                 value=f"${x[1]}",
                                 inline=False)  # if it can't, just work it out on the fly.
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
        try:
            user = ctx.message.author
            head, sep, tail = str(user).partition('#')
            uitems = shop.owneditems(ctx.message.author.id)[
                str(ctx.message.author.id)]
            embed = discord.Embed(title=f"{head}'s Items",
                                  description="Owned items",
                                  color=0x8800ff)
            embed.set_thumbnail(url=user.avatar_url)
            for x in uitems:
                embed.add_field(name=x, value=uitems[x], inline=True)
            await ctx.send(embed=embed)
        except:
            await ctx.send("Your inventory is empty")

    @commands.check(doesexist)
    @commands.command(aliases=["price", "p"])
    async def prices(self, ctx):
        global prices
        costs = [x[0] for x in prices][-288:]
        cycles = [x[1]/6 for x in prices][-288:]
        plt.plot(cycles, costs)
        plt.xlabel('Hours since last restart')
        plt.ylabel('Price')
        with BytesIO() as img_bin:
            plt.savefig(img_bin, format='png')
            img_bin.seek(0)
            await ctx.send(file=discord.File(fp=img_bin, filename=f'{ctx.author.name}.png'))

    v = 50

    @tasks.loop(minutes=refresh)
    async def cost(self):
        global cost
        global countdown
        global refresh
        global cycle
        global leaderboard
        global lb
        global idtoname
        global prices
        global upchance, downchance, upordown, v, decay
        print(f"Refresh: {refresh}")
        #
        #
        #
        # =========================================================================== #
        #                            Price maths
        # =========================================================================== #
        cycle = cycle + 1
        countdown = datetime.now() + timedelta(minutes=refresh)
        upordown = random.choices(["up", "down"], (upchance, downchance), k=1)
        if upordown[0] == "up":
            v += random.uniform(1, 1.25)
            upchance -= random.uniform(1, 5)
            downchance += random.uniform(1, 5)
            if upchance < 0:
                upchance = 0
        else:
            v -= random.uniform(1, 1.25)
            upchance += random.uniform(1, 5)
            downchance -= random.uniform(1, 5)
            if downchance < 0:
                downchance = 0
        if v > 100:
            v -= decay
            if v > 100:
                decay = decay * 1.25
            else:
                decay = decay * reducedecay
        if decay < 0:
            decay = 0
        cost = round(v, 2)
        prices.append((v, cycle))
        #
        #
        #
        print(f"\u001b[32mstock price is ${cost}\nCycle is {cycle}\u001b[31m")
        await self.bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, name=f"Stock price at ${cost}")
        )
        for x in sql.getall("id", mode="field"):
            user = await self.bot.fetch_user(x[0])
            idtoname[x[0]] = user.name


def setup(bot: commands.Bot):
    bot.add_cog(money(bot))
