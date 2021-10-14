import json
import math
import operator
import os
import random
from datetime import date, datetime, timedelta

import discord
import discord.ext
import humanfriendly
import matplotlib.pyplot as plt
from async_timeout import timeout
from discord.ext import commands, tasks
from num2words import num2words
from tinydb import Query, TinyDB
from io import BytesIO

import botlib
import settings
import shop

null = None
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
        return null


def itemfind(dbid):  # function to find the inventory of the id dbid
    re = it.search(i.user == dbid)
    try:
        val = re[0]
        return val['items']
    except:
        return null


def rankfind(dbid):  # same as above but for ranks, not bal
    re = r.search(i.user == dbid)
    try:
        val = re[0]
        return (val['rank']).lower()
    except:
        return null


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
# region ranks
ranks = {
    'bronze': 0,
    'silver': 750,
    'gold': 1500,
    'platinum': 5000,
    'diamond': 10000,
    'demigod': 20000,
    'immortal': 50000,
    'ascendant': 100000,
    'taxman': 150000  # dict for ranks against price
}
# region rank names but formatted
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
# region rank ids
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
# region rank caps
rankcap = {
    'bronze': 1000,
    'silver': 2000,
    'gold': 7500,
    'platinum': 12000,
    'diamond': 25000,
    'demigod': 75000,
    'immortal': 100000,
    'ascendant': 175000,
    'taxman': 200000  # dict for ranks against price
}

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
    @commands.command(aliases=["acc", "balance", "bal", "a"])
    async def account(self, ctx, *, target: discord.Member = null):
        if settings.check(ctx.message.guild.id, "get", "economy"):
            if (target == null) and (balfind(ctx.message.author.id) == null):

                m.insert({'user': ctx.message.author.id, 'bal': 100})
                r.insert({'user': ctx.message.author.id, 'rank': "Bronze"})
                s.insert({'user': ctx.message.author.id, 'stock': 0})
                it.insert({'user': ctx.message.author.id, 'items': []})
                # if the user does not have an account, create one
                await ctx.send("Account created!")

            elif (target != null) and (balfind(ctx.message.author.id) == null):
                # if the user pings someone who does not have an account, send this
                await ctx.send("That user does not have an account set up")
            elif (target != null) and (rankfind(ctx.message.author.id) == null):
                # if the user pings someone who does not have an account, send this
                await ctx.send("That user does not have an account set up")

            # show your balance if you don't enter someone else's account name
            elif (target == null) and (balfind(ctx.message.author.id) != null):
                user = ctx.message.author
                try:
                    rankfind(ctx.message.author.id)
                except:
                    r.insert({'user': ctx.message.author.id, 'rank': "Bronze"})
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
            elif (target != null) and (balfind(ctx.message.author.id) != null):
                userid = int(botlib.nametoid(target.id))
                try:
                    rankfind(ctx.message.author.id)
                except:
                    r.insert({'user': userid, 'rank': "Bronze"})
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
            elif balfind(thrid) + int(arg1) > int(rankcap[rankfind(thrid)]):
                await ctx.send("Sorry, that goes over their wallet cap")
            else:  # if you can actually pay them
                arg1 = int(arg1)
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
            if balfind != null:
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
                   ag1=null,
                   rank=null):  # allows someone to buy a rank
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
                if rank == null:
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
        lb = null
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

    # IDEA: How do players get materials to sell? If anyone can get the materials easily, there is no point in having shops so it needs an element of randomness. Myabe a lootbox sort of system? That could be interesting. Another option is you do stuff like -mine or -cut to get base materials. The base materials can then be crafted into more advanced stuff. -mine and -cut would have a cooldown. Also doing -mine would yeild stone, a small bit of metal, and very rarely gems. This way you have an element of randomness but can still be player directed. This could be interesting but would need HEAVY balancing.
    # IDEA: the shops could be set up in a way so a new shop database is added and inside is this structure: {top level of dict: {user1id: [{item1: [amount, price]}, {item2: [amount, price]}]}}. This is a bit confusing but it would be a much more compact version of what it could be. Since it is using a database, it means we can use tinyDB's search function so people can search by user, item and price. I would also have a precompiled dict of everyone's id to their username so it doesn't lag heaps when opening the store and it has to find the name of every ID.
    # IDEA: Possible idea is that people can run stores and shops as separate things. When you make a store you can set the tax rate (What percentage of the selling price will go to your account) for people's stalls. Less tax rate on stores would be more popular but you would get a lot more competition. It would be a decent way for people to earn money if they can afford it but don't wanna grind out materials. This needs some heavy refinement and won't be implemented straight away but could be an interesting idea for the future.
    # IDEA: I would also need to divide shops up into pages. So we don't get every shop on 1 embed, it would shop 10 items at once and then you would go to the next page. Maybe bugger about with the menus lib? The method of doing this would probably be to compile the items into a list then devide it into a lot of parts, each made up of 10 items. Then add each one to a dict with the key being a number that increases for each page there is. Then just call that page number and loop throught the value to create an embed field. Might be pretty intense and I can't really precompile it but it would live update. I would also run a function every 10 mins to prune all shops with an item count of 0.

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

    @commands.command()
    async def prices(self, ctx):
        global prices
        print(prices)
        costs = [x[0] for x in prices]
        cycles = [x[1] for x in prices]
        plt.plot(cycles, costs)
        plt.xlabel('Number of price changes')
        plt.ylabel('Price')
        with BytesIO() as img_bin:
            plt.savefig(img_bin, format='png')
            img_bin.seek(0)
            await ctx.send(file=discord.File(fp=img_bin, filename=f'{ctx.author.name}.png'))

    @tasks.loop(seconds=60 * refresh)
    async def cost(self):
        global cost
        global countdown
        global refresh
        global cycle
        global leaderboard
        global lb
        global idtoname
        global prices
        cycle = cycle + 1
        countdown = datetime.now() + timedelta(minutes=refresh)
        rand = random.randint(1, 100)
        if rand > cost:
            cost = cost + random.uniform(1, 1.75)
        else:
            cost = cost - random.uniform(1, 1.75)
        cost = round(cost, 2)
        randomchance = random.randint(1, 1000)
        if randomchance == 1:
            cost += 50
        elif randomchance == 2:
            if (cost - 50) < 10:
                cost = 10
            else:
                cost -= 50
        prices.append((cost, cycle))
        print(f"\u001b[32mstock price is ${cost}\nCycle is {cycle}\u001b[31m")
        await self.bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, name=f"Stock price at ${cost}")
        )

        with open(f'{filepath}/config/money.json') as f:
            loaded = dict(json.load(f))
            v = dict(loaded["_default"])
            c = 0
            for x in v:
                if c <= 5:
                    idtoname[v[x]['user']] = await self.bot.fetch_user(v[x]['user'])


def setup(bot: commands.Bot):
    bot.add_cog(money(bot))
