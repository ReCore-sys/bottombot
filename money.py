import os
import asyncio
import math
import random
import time
import async_cse
import discord
import discord.ext
import botlib
import humanfriendly
import settings
import json
from async_timeout import timeout
from discord.ext import commands, tasks
from tinydb import TinyDB, Query
from datetime import datetime, date, timedelta
from num2words import num2words
import operator
import itemlist

filepath = os.path.abspath(os.path.dirname(__file__))
random.seed(15)
m = TinyDB(f'{filepath}/config/money.json')
r = TinyDB(f'{filepath}/config/ranks.json')
s = TinyDB(f'{filepath}/config/stock.json')
it = TinyDB(f'{filepath}/config/items.json')
i = Query()


def stockfind(dbid):  # function to find how many stock a person owns
    re = s.search(i.user == dbid)
    try:
        val = re[0]
        return val['stock']
    except:
        print("This user does not exist 1")


def moneyenabled(id):
    if os.path.isfile(
            f"{filepath}/serversettings/{id}/cashenabled.txt") == True:
        return False
    else:
        return True


def addstock(
    user, amount
):  # Slightly less simple function to add money to a user's balance. Use negative numbers to remove money
    val = stockfind(int(user))
    try:
        val = val + amount
    except:
        print("User does not exist 2")
    s.update({"stock": val}, i.user == user)


def balfind(dbid):  # function to find the balance of the id dbid
    re = m.search(i.user == dbid)
    try:
        val = re[0]
        return val['bal']
    except:
        return None


def itemfind(dbid):  # function to find the balance of the id dbid
    re = it.search(i.user == dbid)
    try:
        val = re[0]
        return val['items']
    except:
        return None


def rankfind(dbid):  # same as above but for ranks, not bal
    re = r.search(i.user == dbid)
    try:
        val = re[0]
        return (val['rank']).lower()
    except:
        return None


def ranktoid(dbid):
    userrank = rankfind(dbid)
    rankid = rankids[userrank]
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
    val = balfind(int(user))
    try:
        val = val + amount
    except:
        print("User does not exist 3")
    m.update({"bal": val}, i.user == user)


def cap():
    return rankcap


# rank tiering
# Bronze
# Silver
# Gold
# Platinum
# Diamond
# Immortal
# Accendant

ranks = {
    'bronze': 0,
    'silver': 750,
    'gold': 1500,
    'platinum': 5000,
    'diamond': 10000,
    'demigod': 200000,
    'immortal': 500000,
    'ascendant': 1000000,
    'taxman': 1500000  # dict for ranks against price
}
rankup = {
    'bronze': 'Bronze',
    'silver': 'Silver',
    'gold': 'Gold',
    'platinum': 'Platinum',
    'diamond': 'Diamond',
    'demigod': 'Demigod',
    'immortal': 'Immortal',
    'ascendant': 'Ascendant',
    'taxman': 'Tax Man'  # dict for ranks against display name
}
rankids = {
    'bronze': 1,
    'silver': 2,
    'gold': 3,
    'platinum': 4,
    'diamond': 5,
    'immortal': 6,
    'immortal': 7,
    'ascendant': 8,
    'taxman': 9  # rank compared to it's id. Usefull for permission levels
}
rankcap = {
    'bronze': 1000,
    'silver': 2000,
    'gold': 7500,
    'platinum': 12000,
    'diamond': 25000,
    'demigod': 750000,
    'immortal': 1000000,
    'ascendant': 1750000,
    'taxman': 2000000  # dict for ranks against price
}

cost = 50
countdown = None
refresh = 10
cycle = 0
precost = 50
leaderboard = []
lb = None
idtoname = {}


class money(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cost.start()

    # shows the user's account
    @commands.command(aliases=["acc", "balance", "bal", "a"])
    async def account(self, ctx, *, target: discord.Member = None):
        if settings.check(ctx.message.guild.id, "get", "economy"):
            if (target == None) and (balfind(ctx.message.author.id) == None):
                m.insert({'user': ctx.message.author.id, 'bal': 100})
                r.insert({'user': ctx.message.author.id, 'rank': "Bronze"})
                s.insert({'user': ctx.message.author.id, 'stock': 0})
                it.insert({'user': ctx.message.author.id, 'items': []})
                # if the user does not have an account, create one
                await ctx.send("Account created!")

            elif (target != None) and (balfind(ctx.message.author.id) == None):
                # if the user pings someone who does not have an account, send this
                await ctx.send("That user does not have an account set up")
            elif (target != None) and (rankfind(ctx.message.author.id) == None):
                # if the user pings someone who does not have an account, send this
                await ctx.send("That user does not have an account set up")

            # show your balance if you don't enter someone else's account name
            elif (target == None) and (balfind(ctx.message.author.id) != None):
                user = ctx.message.author
                embed = discord.Embed(title=f"{user}",
                                      description="Account info",
                                      color=0x8800ff)
                embed.set_thumbnail(url=user.avatar_url)
                embed.add_field(name="ID", value=f"{user.id}", inline=True)
                embed.add_field(name="Balance",
                                value=f"${balfind(user.id)}",
                                inline=False)
                embed.add_field(
                    name="Wallet cap",
                    value=f"${rankcap[rankfind(user.id)]} ({round((balfind(user.id) / rankcap[rankfind(user.id)] * 100))}% used)",
                    inline=False)
                embed.add_field(name="Rank",
                                value=f"{rankup[rankfind(user.id)]}",
                                inline=False)
                embed.add_field(name="Owned stocks",
                                value=f"{stockfind(user.id)}",
                                inline=False)
                await ctx.send(embed=embed)

            # show someone else's account if you do ping someone
            elif (target != None) and (balfind(ctx.message.author.id) != None):
                userid = int(botlib.nametoid(target.id))
                username = ctx.guild.get_member(userid)
                embed = discord.Embed(title=f"{target}",
                                      description="Account info",
                                      color=0x8800ff)
                embed.set_thumbnail(url=target.avatar_url)
                embed.add_field(name="ID", value=f"{userid}", inline=True)
                embed.add_field(name="Balance",
                                value=f"${balfind(userid)}",
                                inline=False)
                embed.add_field(name="Rank",
                                value=f"{rankup[rankfind(userid)]}",
                                inline=False)
                embed.add_field(name="Owned stocks",
                                value=f"{stockfind(userid)}",
                                inline=False)
                await ctx.send(embed=embed)
        else:
            await ctx.send("Sorry, economy is disabled on this server")

    @commands.command()
    async def pay(self,
                  ctx,
                  arg1,
                  target: discord.Member = None):  # paying someone
        if settings.check(ctx.message.guild.id, "get", "economy"):
            # finds the balance of the sender
            urval = int(balfind(ctx.message.author.id))
            # finds the bal of the target
            thrval = int(balfind(int(target.id)))
            thrid = target.id  # target's ID
            if target == None:
                # if that user's balance is None, they don't exist
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
            elif balfind(thrid) + arg1 > rankcap[rankfind(thrid)]:
                await ctx.send("Sorry, that goes over their wallet cap")
            else:  # if you can actually pay them
                urval = urval - int(arg1)  # takes the amount from your bal
                thrval = thrval + int(arg1)  # adds the amount to their bal
                m.update({"bal": urval}, i.user == (ctx.message.author.id))
                m.update({"bal": thrval},
                         i.user == int(target.id))  # write changes to the db
                # inform the person that they were paid
                await ctx.send(f"${arg1} was transferred to <@!{target.id}>")
                # send dm to target. Still not working
                await target.send(
                    f"{ctx.message.author} just payed you ${arg1}!\n({ctx.guild.name})"
                )
        else:
            await ctx.send("Sorry, economy has been turned off for this server"
                           )

    @commands.command()
    # adds money to an account. Only I can use it
    async def add(self, ctx, arg1, target: discord.Member):
        if settings.check(ctx.message.guild.id, "get", "economy"):
            if ctx.message.author.id == 451643725475479552:
                val = int(balfind(int(target.id)))
                val = val + int(arg1)
                m.update({"bal": int(val)}, i.user == int(target.id))
                await ctx.send(f"${arg1} added")
            else:
                await ctx.send("Nope")
        else:
            await ctx.send("Sorry, economy is disabled on this server")

    @commands.command()
    # adds money to an account. Only I can use it
    async def set(self, ctx, arg1, target: discord.Member):
        if settings.check(ctx.message.guild.id, "get", "economy"):
            if ctx.message.author.id == 451643725475479552:
                m.update({"bal": int(arg1)}, i.user == int(target.id))
                await ctx.send(f"Balance set to ${arg1} for {target}")
            else:
                await ctx.send("Nope")
        else:
            await ctx.send("Sorry, economy is disabled on this server")

    @commands.command()
    # adds money to an account. Only I can use it
    async def setstock(self, ctx, arg1, target: discord.Member):
        if settings.check(ctx.message.guild.id, "get", "economy"):
            if ctx.message.author.id == 451643725475479552:
                s.update({"stock": int(arg1)}, i.user == int(target.id))
                await ctx.send(f"Stocks set to {arg1} for {target}")
            else:
                await ctx.send("Nope")
        else:
            await ctx.send("Sorry, economy is disabled on this server")

    @commands.command(pass_context=True)
    @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    async def daily(self, ctx):
        if settings.check(ctx.message.guild.id, "get", "economy"):
            if balfind != None:
                r = random.randint(20, 50)
                if balfind(ctx.message.author.id) + r <= rankcap[rankfind(
                        ctx.message.author.id)]:
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
            await ctx.send(
                f"You can only do daily once a day. Try again in {humanfriendly.format_timespan(error.retry_after)}"
            )

    @commands.command(aliases=["stock", "stonk", "stonks"])
    async def stocks(self, ctx, action=None, count=None):
        if settings.check(ctx.message.guild.id, "get", "economy"):
            global stock
            global cost
            global countdown
            user = int(ctx.message.author.id)
            if stockfind(user) == None:
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
                if action == None:
                    await ctx.send(
                        f"Current price of stocks: **${cost}**\nYou currently own {stockcount} stocks\nTime until stock price change: {humanfriendly.format_timespan(timeto)}"
                    )  # if no options are specified, show current price and hw many the user owns.
                else:
                    count = int(count)
                    fcost = int(round((float(count) * cost)))
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
                        if balfind(ctx.message.author.id) + fcost <= rankcap[
                                rankfind(ctx.message.author.id)]:  # Makes sure that the sold stocks won't exceed the wallet cap of their rank.
                            addmoney(user, fcost)
                            addstock(user, (0 - count))
                            await ctx.send(f"{count} stocks sold for ${fcost}")
                        else:
                            await ctx.send(
                                "Sorry, that goes over your wallet cap")
                    elif action == "calc":
                        await ctx.send(
                            # simply calculates how much the specified stocks would cost.
                            f"{count} stocks at ${cost} is worth ${round(count * cost)}"
                        )
        else:
            await ctx.send("Sorry, economy is disabled on this server")

    @commands.command(aliases=["ranks"])
    async def rank(self,
                   ctx,
                   ag1=None,
                   rank=None):  # allows someone to buy a rank
        if settings.check(ctx.message.guild.id, "get", "economy"):
            global ranks  # idk if this is needed but it can't hurt to have it
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
                for x in ranks:
                    if x != "bronze":
                        # loops through all the ranks so I don't have to hardcode it
                        embed.add_field(name=rankup[x],
                                        value=f"${ranks[x]}",
                                        inline=True)
                embed.set_footer(
                    text='Use "-rank buy [rank name]" to buy a rank')
                await ctx.send(embed=embed)
            else:  # if they do have it, start doing stuff
                crank = rankfind(int(user))
                crankv = ranks[crank.lower()]
                val = ranks[rank.lower()]
                if rank == None:
                    # if they don't enter a rank to buy
                    await ctx.send("Please choose a rank to buy")
                elif (rank.lower() in ranks) == False:
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
                    # gets the display name of the rank
                    rank2 = rankup[rank.lower()]
                    r.update({"rank": rank2}, i.user == int(
                        ctx.message.author.id))  # writes new rank to db
                    # takes the money from the account (adds a negative value)
                    addmoney(user, cost)
                    # let them know
                    await ctx.send(f"Rank {rank} was bought for ${val}")
        else:
            await ctx.send("Sorry, economy is disabled on this server")

    @commands.command(aliases=["leaderboard", "leader", "board"])
    # command to create a leaderboard of the 5 richest users.
    async def lb(self, ctx):
        # since turning the user ids to usernames is pretty slow, it is recompiled every 10 mins
        global leaderboard
        global lb
        global idtoname
        global ranks
        leaderboard = []
        lb = None
        lb = discord.Embed(title="Leaderboard",
                           description="Current leaderboard",
                           color=0xFFD700)
        f = open(f'{filepath}/config/money.json')
        loaded = dict(json.load(f))
        v = dict(loaded["_default"])
        for x in v:  # compiles the price of stocks, balance and their rank to work out their net worth.
            totalval = (v[x]['bal']) + (stockfind((v[x]['user'])) * cost)
            totalval = totalval + ranks[rankfind((v[x]['user']))]
            totalval = round(totalval)
            leaderboard.append(((v[x]['user']), totalval))

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

    @commands.command(aliases=["store", "shops"])
    async def shop(self, ctx, *, action=None):
        # returns a list of items and their prices from a list in an external lib
        items = itemlist.items()
        uitems = itemfind(ctx.message.author.id)
        if action == None:  # if no options are enterd, show prices
            embed = discord.Embed(title="Shop",
                                  description="Current items in the store",
                                  color=0xFFD700)
            items = dict(sorted(items.items(), key=lambda item: item[1]))
            for x in items:
                embed.add_field(name=x, value=f"${items[x]}", inline=True)
            await ctx.send(embed=embed)
        else:
            if action not in items:
                await ctx.send("That is not a valid item")
            elif action in uitems:
                await ctx.send("You already own that")
            elif items[action] > balfind(ctx.message.author.id):
                await ctx.send("You don't have enough money")
            else:
                addmoney(ctx.message.author.id, 0 - items[action])
                uitems.append(action)
                it.update({"items": uitems},
                          i.user == int(ctx.message.author.id))
                # adds the item to the player's inventory.
                await ctx.send(f"{action} bought for ${items[action]}")
                # TODO Allow players to run their own shops with crafting items

    @commands.command(aliases=["inventory", "i"])
    async def inv(self, ctx):
        user = ctx.message.author
        head, sep, tail = str(user).partition('#')
        uitems = itemfind(ctx.message.author.id)
        embed = discord.Embed(title=f"{head}'s Items",
                              description="Owned items",
                              color=0x8800ff)
        embed.set_thumbnail(url=user.avatar_url)
        for x in uitems:
            embed.add_field(name=x, value="\u200b", inline=True)
        await ctx.send(embed=embed)

    @tasks.loop(seconds=60 * refresh)
    async def cost(self):
        global cost
        global countdown
        global refresh
        global cycle
        global leaderboard
        global lb
        global idtoname
        f = open(f'{filepath}/config/money.json')
        loaded = dict(json.load(f))
        v = dict(loaded["_default"])
        c = 0
        for x in v:
            if c <= 5:
                idtoname[v[x]['user']] = await self.bot.fetch_user(v[x]['user']
                                                                   )
        cycle = cycle + 1
        countdown = datetime.now() + timedelta(minutes=refresh)
        rand = random.randint(1, 100)
        if rand > cost:
            cost = cost + random.uniform(1, 5)
        else:
            cost = cost - random.uniform(1, 5)
        cost = round(cost, 2)
        print(f"\u001b[32mstock price is ${cost}\nCycle is {cycle}\u001b[31m")
        await self.bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, name=f"Stock price at ${cost}")
        )
        f.close()


def setup(bot: commands.Bot):
    bot.add_cog(money(bot))
