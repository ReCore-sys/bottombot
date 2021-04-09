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

filepath = os.path.abspath(os.path.dirname(__file__))
random.seed(15)
m = TinyDB(f'{filepath}/config/money.json')
r = TinyDB(f'{filepath}/config/ranks.json')
s = TinyDB(f'{filepath}/config/stock.json')
i = Query()


def stockfind(dbid):  # function to find how many stock a person owns
    re = s.search(i.user == dbid)
    try:
        val = re[0]
        return val['stock']
    except:
        print("This user does not exist 1")


def moneyenabled(id):
    if os.path.isfile(f"{filepath}/serversettings/{id}/cashenabled.txt") == True:
        return False
    else:
        return True


def addstock(user, amount):  # Slightly less simple function to add money to a user's balance. Use negative numbers to remove money
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


def canbuy(price, id):  # simple function to check if a user can buy something. Price must be an int.
    bal = balfind(id)
    if bal >= price:
        return True
    else:
        return False


def addmoney(user, amount):  # Slightly less simple function to add money to a user's balance. Use negative numbers to remove money
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

    @commands.command(aliases=["acc", "balance", "bal", "a"])  # shows the user's account
    async def account(self, ctx, *, target: discord.Member = None):
        if settings.check(ctx.message.guild.id, "get", "economy"):
            if (target == None) and (balfind(ctx.message.author.id) == None):
                m.insert({'user': ctx.message.author.id, 'bal': 100})
                r.insert({'user': ctx.message.author.id, 'rank': "Bronze"})
                s.insert({'user': ctx.message.author.id, 'stock': 0})
                await ctx.send("Account created!")  # if the user does not have an account, create one

            elif (target != None) and (balfind(ctx.message.author.id) == None):
                await ctx.send("That user does not have an account set up")  # if the user pings someone who does not have an account, send this
            elif (target != None) and (rankfind(ctx.message.author.id) == None):
                await ctx.send("That user does not have an account set up")  # if the user pings someone who does not have an account, send this

            elif (target == None) and (balfind(ctx.message.author.id) != None):  # show your balance if you don't enter someone else's account name
                user = ctx.message.author
                embed = discord.Embed(title=f"{user}", description="Account info", color=0x8800ff)
                embed.set_thumbnail(url=user.avatar_url)
                embed.add_field(name="ID", value=f"{user.id}", inline=True)
                embed.add_field(name="Balance", value=f"${balfind(user.id)}", inline=False)
                embed.add_field(name="Rank", value=f"{rankup[rankfind(user.id)]}", inline=False)
                embed.add_field(name="Owned stocks", value=f"{stockfind(user.id)}", inline=False)
                await ctx.send(embed=embed)

            elif (target != None) and (balfind(ctx.message.author.id) != None):  # show someone else's account if you do ping someone
                userid = int(botlib.nametoid(target.id))
                username = ctx.guild.get_member(userid)
                embed = discord.Embed(title=f"{target}", description="Account info", color=0x8800ff)
                embed.set_thumbnail(url=target.avatar_url)
                embed.add_field(name="ID", value=f"{userid}", inline=True)
                embed.add_field(name="Balance", value=f"${balfind(userid)}", inline=False)
                embed.add_field(name="Rank", value=f"{rankup[rankfind(userid)]}", inline=False)
                embed.add_field(name="Owned stocks", value=f"{stockfind(userid)}", inline=False)
                await ctx.send(embed=embed)
        else:
            await ctx.send("Sorry, economy is disabled on this server")

    @commands.command()
    async def pay(self, ctx, arg1, target: discord.Member = None):  # paying someone
        if settings.check(ctx.message.guild.id, "get", "economy"):
            urval = int(balfind(ctx.message.author.id))  # finds the balance of the sender
            thrval = int(balfind(int(target.id)))  # finds the bal of the target
            thrid = target.id  # target's ID
            if target == None:
                await ctx.send("Sorry, that person either does not exist or has not set up their account.")  # if that user's balance is None, they don't exist
            elif arg1.isnumeric == False:  # if you try paying someone something that isn't a number
                await ctx.send("You need to give me a number")
            elif thrid == ctx.message.author.id:  # if you try paying yourself
                await ctx.send("You can't pay yourself")
            elif int(arg1) < 1:
                await ctx.send("You can't pay less than $1 to someone")
            elif (int(arg1) >= urval) or (urval - int(arg1) < 0):  # if either you have less than $1 or you try and pay more than you have
                await ctx.send("Sorry, you don't have enough money")
            elif balfind(thrid) + arg1 > rankcap[rankfind(thrid)]:
                await ctx.send("Sorry, that goes over their wallet cap")
            else:  # if you can actually pay them
                urval = urval - int(arg1)  # takes the amount from your bal
                thrval = thrval + int(arg1)  # adds the amount to their bal
                m.update({"bal": urval}, i.user == (ctx.message.author.id))
                m.update({"bal": thrval}, i.user == int(target.id))  # write changes to the db
                await ctx.send(f"${arg1} was transferred to <@!{target.id}>")  # inform the person that they were paid
                await target.send(f"{ctx.message.author} just payed you ${arg1}!\n({ctx.guild.name})")  # send dm to target. Still not working
        else:
            await ctx.send("Sorry, economy has been turned off for this server")

    @commands.command()
    async def add(self, ctx, arg1, target: discord.Member):  # adds money to an account. Only I can use it
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
    async def set(self, ctx, arg1, target: discord.Member):  # adds money to an account. Only I can use it
        if settings.check(ctx.message.guild.id, "get", "economy"):
            if ctx.message.author.id == 451643725475479552:
                m.update({"bal": int(arg1)}, i.user == int(target.id))
                await ctx.send(f"Balance set to ${arg1} for {target}")
            else:
                await ctx.send("Nope")
        else:
            await ctx.send("Sorry, economy is disabled on this server")

    @commands.command()
    async def setstock(self, ctx, arg1, target: discord.Member):  # adds money to an account. Only I can use it
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
                if balfind(ctx.message.author.id) + r <= rankcap[rankfind(ctx.message.author.id)]:
                    addmoney(ctx.message.author.id, r)
                    await ctx.send(f"${r} was added to your account")
                else:
                    await ctx.send("Sorry, that goes over your wallet cap")
            else:
                await ctx.send("You do not have an account. Do -account to make one")
        else:
            await ctx.send("Sorry, economy is disabled on this server")

    @daily.error
    async def daily_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"You can only do daily once a day. Try again in {humanfriendly.format_timespan(error.retry_after)}")

    @commands.command(aliases=["stock", "stonk", "stonks"])
    async def stocks(self, ctx, action = None, count = None):
        if settings.check(ctx.message.guild.id, "get", "economy"):
            global stock
            global cost
            global countdown
            user = int(ctx.message.author.id)
            if stockfind(user) == None:
                await ctx.send("You need to create an account with -account first")
            else:
                if action == "sell":
                    if count == "all":
                        count = stockfind(user)
                elif action == "buy":
                    if count == "all":
                        bal = balfind(user)
                        count = math.floor(bal / cost)

                stockcount = stockfind(user)
                bal = balfind(ctx.message.author.id)
                try:
                    timeto = countdown - datetime.now()
                except:
                    pass
                if action == None:
                    await ctx.send(f"Current price of stocks: **${cost}**\nYou currently own {stockcount} stocks\nTime until stock price change: {humanfriendly.format_timespan(timeto)}")
                else:
                    count = int(count)
                    fcost = int(round((float(count) * cost)))
                    if count <= 0:
                        await ctx.send("You need to enter a number that is over 0")
                    elif action == "buy" and (fcost > bal):
                        await ctx.send("You don't have enough money")
                    elif (action == "sell") and (count > int(stockcount)):
                        await ctx.send("You don't own that many stocks")
                    elif action == "buy":
                        addmoney(user, (0 - fcost))
                        addstock(user, count)
                        await ctx.send(f"{count} stocks bought for ${fcost}")
                    elif action == "sell":
                        if balfind(ctx.message.author.id) + fcost <= rankcap[rankfind(ctx.message.author.id)]:
                            addmoney(user, fcost)
                            addstock(user, (0 - count))
                            await ctx.send(f"{count} stocks sold for ${fcost}")
                        else:
                            await ctx.send("Sorry, that goes over you wallet cap")
                    elif action == "calc":
                        await ctx.send(f"{count} stocks at ${cost} is worth ${round(count * cost)}")
        else:
            await ctx.send("Sorry, economy is disabled on this server")

    @commands.command(aliases=["ranks"])
    async def rank(self, ctx, ag1 = None, rank=None):   # allows someone to buy a rank
        if settings.check(ctx.message.guild.id, "get", "economy"):
            global ranks   # idk if this is needed but it can't hurt to have it
            user = ctx.message.author.id   # "user" is easier to type than "ctx.message.author.id"
            if ag1 != "buy":   # if they don't have "buy" as their first arg, send prices
                embed = discord.Embed(title="Ranks", description="The price of different ranks", color=0x1e00ff)
                embed.set_thumbnail(url="https://lh3.googleusercontent.com/proxy/07h14DsTB_1a1UudwyVJz7OICAz9RSOE0uLEI3ox3vFTdjvM4hJolKhXaAEk0UeSeE2V92Qgv8ScFee0Zm9GoR-VKc6EadFPwYIVw93O6-EiSvI")
                for x in ranks:
                    if x != "bronze":
                        embed.add_field(name=rankup[x], value=f"${ranks[x]}", inline=True)  # loops through all the ranks so I don't have to hardcode it
                embed.set_footer(text='Use "-rank buy [rank name]" to buy a rank')
                await ctx.send(embed=embed)
            else:   # if they do have it, start doing stuff
                crank = rankfind(int(user))
                crankv = ranks[crank.lower()]
                val = ranks[rank.lower()]
                if rank == None:
                    await ctx.send("Please choose a rank to buy")   # if they don't enter a rank to buy
                elif (rank.lower() in ranks) == False:
                    await ctx.send("That was not a valid rank")  # if the rank does not appear in the ranks list (dict)
                elif canbuy(val, user) == False:
                    await ctx.send("You do not have enough money to buy this")  # explains itself
                elif crankv > val:
                    await ctx.send("You can't buy a lower rank")
                elif crankv == int(ranks[rank.lower()]):
                    await ctx.send("You can't buy your current rank")
                else:
                    cost = 0 - val  # turn the value into a negative so you can buy it properly
                    rank2 = rankup[rank.lower()]  # gets the display name of the rank
                    r.update({"rank": rank2}, i.user == int(ctx.message.author.id))  # writes new rank to db
                    addmoney(user, cost)  # takes the money from the account (adds a negative value)
                    await ctx.send(f"Rank {rank} was bought for ${val}")  # let them know
        else:
            await ctx.send("Sorry, economy is disabled on this server")

    @commands.command(aliases=["leaderboard", "leader", "board"])
    async def lb(self, ctx):
        global leaderboard
        global lb
        global idtoname
        global ranks
        leaderboard = []
        lb = None
        lb = discord.Embed(title="Leaderboard", description="Current leaderboard", color=0xFFD700)
        f = open(f'{filepath}/config/money.json')
        loaded = dict(json.load(f))
        v = dict(loaded["_default"])
        for x in v:
            totalval = (v[x]['bal']) + (stockfind((v[x]['user'])) * cost)
            totalval = totalval + ranks[rankfind((v[x]['user']))]
            totalval = round(totalval)
            leaderboard.append(((v[x]['user']), totalval))

        leaderboard = sorted(leaderboard, key=operator.itemgetter(1), reverse=True)
        c = 0
        count = 1
        for x in leaderboard:
            if x[0] == ctx.message.author.id:
                break
            count = count + 1
        for x in leaderboard:
            c = c + 1
            if c <= 5:
                try:
                    lb.add_field(name=idtoname[x[0]], value=f"${x[1]}", inline=False)
                except:
                    lb.add_field(name=await self.bot.fetch_user(x[0]), value=f"${x[1]}", inline=False)
        lb.set_footer(text=f"Your position: {num2words(count, to='ordinal_num')} out of {len(leaderboard)}")
        await ctx.send(embed=lb)

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
                idtoname[v[x]['user']] = await self.bot.fetch_user(v[x]['user'])

        cycle = cycle + 1
        countdown = datetime.now() + timedelta(minutes=refresh)
        rand = random.randint(1, 100)
        if rand > cost:
            cost = cost + random.uniform(1, 5)
        else:
            cost = cost - random.uniform(1, 5)
        cost = round(cost, 2)
        print(f"\u001b[32mstock price is ${cost}\nCycle is {cycle}\u001b[31m")
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"Stock price at ${cost}"))
        f.close()


def setup(bot: commands.Bot):
    bot.add_cog(money(bot))
