import os
import asyncio
import math
import random
import time
import async_cse
import discord
import botlib
import money
import settings
import crafts
import json
from async_timeout import timeout
from discord.ext import commands, tasks
from tinydb import TinyDB, Query
from datetime import datetime, date, timedelta
from num2words import num2words
import operator
from itertools import islice
from collections import OrderedDict
from operator import getitem
from disputils import BotEmbedPaginator, BotConfirmation, BotMultipleChoice
import copy
null = None
filepath = os.path.abspath(os.path.dirname(__file__))
# region Base items


wares = {
    "stone": 10,
    "organics": 15,
    "iron-ore": 30,
    "water": 5
}


crafts = crafts.recipes()


def owneditems(id, item=null):
    '''Gets the user's owned items

    :param id: the userid
    :type id: int
    :param item: The item to be looking for. Defaults to null.
    :type item: string
    :return: If and item is given return how many that user has. If the user own's null, return 0. If null given return a dict of all owned items.

    '''
    with open(f'{filepath}/config/items.json', "r") as uitems:
        uitems = json.load(uitems)
        if item != null:
            print(uitems[str(id)][item])
            try:
                items = int(uitems[str(id)][item])
                return items
            except KeyError:
                return 0
        else:
            return uitems


def additem(id, type, n):
    with open(f'{filepath}/config/items.json', "r") as uitems:
        uitems = json.load(uitems)
        try:
            items = uitems[str(id)]
        except KeyError:
            uitems[str(id)] = {}
            items = uitems[str(id)]
        try:
            items[type] = items[type] + n
        except KeyError:
            items[type] = n
        uitems[str(id)] = items
        json.dump(uitems, open(f"{filepath}/config/items.json", "w"))


def shred(d, n=2):
    c = 0
    y = []
    g = {}
    for x in d:
        g[x] = d[x]
        c = c + 1
        if c == n:
            y.append(g)
            g = {}
            c = 0
    if g != {}:
        y.append(g)
    return y


def validint(n):
    if n <= 0:
        return False
    else:
        try:
            int(n)
            return True
        except:
            return False


waiting = {}


class shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.crafter.start()

    @commands.command()
    async def buy(self, ctx, item=null, itemcount=1):
        if validint(itemcount) == False:
            await ctx.send("That is not a valid input")
        else:
            # Ok I have an actual reason for converting it to a string. Json can't have ints as keys so it completely breaks if I try to do that. I really don't reccomend it.
            id = str(ctx.message.author.id)
            if item == null:
                embed = discord.Embed(
                    title=f"Item prices", description="Price for base materials", color=0x1e00ff)
                for x in wares:
                    embed.add_field(name=x,
                                    value=f"${wares[x]}", inline=False)
                await ctx.send(embed=embed)
            else:
                with open(f'{filepath}/config/items.json', "r") as loc:
                    file1 = dict(json.load(loc))
                    if item not in wares:
                        await ctx.send("That was not a valid item.")
                    elif str(itemcount).isnumeric() == False:
                        await ctx.send("Please enter a number")
                    else:
                        if money.balfind(ctx.message.author.id) < wares[item] * itemcount:
                            await ctx.send("Sorry you can't afford that")
                        else:
                            # what to actually run if they can buy the item
                            with open(f'{filepath}/config/items.json', "r") as loc:
                                file1 = json.load(loc)
                                try:
                                    file1[id]
                                except:
                                    file1[id] = {}
                                    file1[id][item] = 0
                                if item not in file1[str(id)]:
                                    file1[id][item] = itemcount
                                else:
                                    file1[id][item] = file1[str(
                                        id)][item] + itemcount
                                await ctx.send(f"{itemcount} {item} bought for ${itemcount * wares[item]}")
                                money.addmoney(
                                    ctx.message.author.id, (0 - (itemcount * wares[item])))
                            json.dump(file1, open(
                                f'{filepath}/config/items.json', "w"))

    @ commands.command()
    async def sell(self, ctx, item=null, price=1, itemcount=1):
        if validint(price) == False:
            await ctx.send("That is not a valid input")
        elif validint(itemcount) == False:
            await ctx.send("That is not a valid input")
        else:
            with open(f'{filepath}/config/items.json', "r") as uitems:
                uitems = json.load(uitems)
                try:
                    int(uitems[str(ctx.message.author.id)][item])
                    if int(itemcount) <= int(uitems[str(ctx.message.author.id)][item]):
                        # Ok I have an actual reason for converting it to a string. Json can't have ints as keys so it completely breaks if I try to do that. I really don't reccomend it.
                        with open(f'{filepath}/config/shops.json', "r") as loc:
                            file1 = dict(json.load(loc))
                            if str(itemcount).isnumeric() == False:
                                await ctx.send("Please enter a number for the number to sell")
                            else:
                                chosen = False, null
                                usedids = []
                                if owneditems(ctx.message.author.id, item) >= itemcount:
                                    # what to actually run if they can buy the item
                                    with open(f'{filepath}/config/shops.json', "r") as loc2:
                                        file2 = json.load(loc2)
                                        storeid = random.randint(
                                            100000, 999999)
                                        for x in file2:
                                            usedids.append(x)

                                            for z in x:
                                                if file2[x]["item"] == item:
                                                    if file2[x]["userid"] == ctx.message.author.id:

                                                        chosen = True, x
                                        taken = False
                                        c = 0
                                        while storeid in usedids:
                                            storeid = random.randint(
                                                100000, 999999)
                                            c = c + 1  # this specific shitscape is to create a unique id for the store. It stores all currently used ids then creates a new one that is not in that list
                                        # TODO: Create function here to check if the store already exists
                                        if chosen[0] == True:
                                            cid = chosen[1]
                                            file2[cid] = {"item": item,
                                                          # if the user is already selling an item, just add it on to the current number
                                                          "itemcount": file2[cid]["itemcount"] + itemcount,
                                                          "price": price,  # but do change the price
                                                          "username": (str(await self.bot.fetch_user(ctx.message.author.id)).split("#")[0]),
                                                          "userid": ctx.message.author.id}
                                            await ctx.send(f"OK, shop {cid} edited")
                                        elif taken == False:
                                            if str(price).isnumeric() == False:
                                                await ctx.send("Please enter a number for the price")
                                            else:
                                                print(
                                                    f"Creating store with ID {storeid}")
                                                file2[storeid] = {"item": item,
                                                                  "itemcount": itemcount,
                                                                  "price": price,
                                                                  "username": (str(await self.bot.fetch_user(ctx.message.author.id)).split("#")[0]),
                                                                  "userid": ctx.message.author.id}
                                                await ctx.send(f"OK, shop created with the ID {storeid}")
                                        json.dump(file2, open(
                                            f'{filepath}/config/shops.json', "w"))

                                        # Holy shit we finished the cesspit of if-thens. Now we take them items from the user. We do this at then end so even if the thing breaks, they don't lose their stuff. And lets be honest, it probably will break.
                                        uitems[str(ctx.message.author.id)][item] = uitems[str(
                                            ctx.message.author.id)][item] - itemcount
                                        json.dump(uitems, open(
                                            f'{filepath}/config/items.json', "w"))
                                else:
                                    # So far this has never been called but eh, can't hurt to have it here
                                    await ctx.send(f"Sorry you don't have enough {item} to sell that many")
                    else:  # if they don't have enough items to sell.
                        await ctx.send("Sorry, you don't have that many items")
                except:
                    await ctx.send("You don't own any of those")
    # TODO: Add both crafting and buying. For crafting probably just do a big ass dict with each items having the following format {item: [[material1: amountneeded], [material2: amountneeded]]}. Then just check if they have the stuff

    @ commands.command()
    async def shop(self, ctx, action1=null, action2=null, action3=1):
        cango = False
        if validint(action3) == False:
            await ctx.send("That is not a valid input")
        else:
            sorted1 = json.load(open(f'{filepath}/config/shops.json', "r"))
            if action1 == null:
                await ctx.send("Please enter an item to search for")
            if action1 == "buy":
                if str(action2).isnumeric() == False:
                    await ctx.send("Please enter a numeric ID")
                elif int((int(sorted1[str(action2)]["price"]) * action3)) > int(money.balfind(ctx.message.author.id)):
                    await ctx.send("Sorry, you can't afford that")
                else:
                    try:
                        sorted1[str(action2)]
                        cango = True
                    except KeyError:
                        await ctx.send("Please enter a valid id")

                    if cango == True:
                        if (sorted1[str(action2)]["itemcount"] - action3) < 0:
                            await ctx.send(f"Sorry, they don't own that much {sorted1[str(action2)]['item']}")
                        else:
                            sorted1[str(action2)]["itemcount"] = sorted1[str(
                                action2)]["itemcount"] - action3
                            await ctx.send(f'{action3} {sorted1[str(action2)]["item"]} was bought for ${(int(sorted1[str(action2)]["price"]) * action3)}')
                            money.addmoney(
                                (sorted1[str(action2)]["userid"]), int((int(sorted1[str(action2)]["price"]) * action3)))
                            money.addmoney(ctx.message.author.id,
                                           (0 - int((int(sorted1[str(action2)]["price"]) * action3))))
                            json.dump(sorted1, open(
                                f'{filepath}/config/shops.json', "w"))
                            additem(ctx.message.author.id,
                                    sorted1[str(action2)]["item"], action3)
                if sorted1[str(action2)]["itemcount"] == 0:
                    del sorted1[str(action2)]
                    print(f"{action2} removed cos it had 0 left")
                    json.dump(sorted1, open(
                        f'{filepath}/config/shops.json', "w"))

            else:
                sorted1 = dict(OrderedDict(
                    sorted(sorted1.items(), key=lambda x: x[1]['username'])))
                n = 5
                v = 1
                e = []
                tosend = {}
                for x in sorted1:
                    if sorted1[x]["item"] == action1:
                        tosend[x] = [sorted1[x]['price'], sorted1[x]
                                     ['itemcount'], sorted1[x]['username']]
                try:
                    chopped = shred(tosend, 2)
                    for v in chopped:
                        embed = discord.Embed(
                            title=f"Shop: {action1}", description="Welcome to the shop!", color=0x1e00ff)
                        for r in v:
                            print(f"r = {r}")
                            embed.add_field(name=f"{r} \n${v[r][0]} ({v[r][1]} Available)",
                                            value=f"{v[r][2]}\n", inline=False)
                        e.append(embed)
                        embed = None

                    paginator = BotEmbedPaginator(ctx, e)
                    await paginator.run()
                except:
                    await ctx.send("Sorry, there are no stores selling that")

                json.dump(sorted1, open(f'{filepath}/config/shops.json', "w"))

    @ commands.command()
    async def craft(self, ctx, action1=null, action2=1):
        if validint(action2) == False:
            await ctx.send("That is not a valid input")
        else:
            # action1: the item's name
            # action2: how many to craft
            global waiting
            with open(f'{filepath}/config/items.json', "r") as loc:
                items = json.load(loc)
                cancraft = True
                cneeded = null
                chave = null
                ctype = null
                var1 = []
                if action1 == null:
                    n = 5
                    v = 1
                    tosend = []
                    pre = []
                    e = []
                    chopped = shred(crafts, 5)
                    for y in chopped:
                        formed = []
                        embed = None
                        embed = discord.Embed(
                            title=f'Page {v}', description=f'Page {v} of {len(chopped)}')
                        v = v + 1
                        for x in y:
                            for p in y[x]:
                                if type(p) is list:
                                    for r in p:
                                        formed.append(f"{r[0]}: {r[1]}")
                            embed.add_field(
                                name=x, value="\n".join(formed), inline=False)
                            formed = []
                        e.append(embed)
                        embed = None

                    paginator = BotEmbedPaginator(ctx, e)
                    await paginator.run()
                    embed = None
                if str(action2).isnumeric() == False:
                    await ctx.send("Sorry, you need to give a number for the amount")
                else:
                    if action2 != null:
                        action2 = int(action2)
                    # try:
                    for r in crafts[action1][0]:
                        if owneditems(ctx.message.author.id, r[0]) >= (r[1] * action2):
                            pass
                        else:
                            print(f"r = {r}")
                            cancraft = False
                            chave = owneditems(
                                ctx.message.author.id, r[0])
                            cneeded = r[1] * action2
                            ctype = r[0]

                    if cancraft:
                        try:
                            print(f"crafts = {crafts[action1]}")
                            amount = crafts[action1][2] * action2
                        except:
                            amount = 1

                        time = crafts[action1][1]

                        for y in crafts[action1][0]:
                            take = True
                            print(f"y = {y}")
                            print(
                                f"conf = {items[str(ctx.message.author.id)][y[0]]}")
                            try:
                                if y[2] == False:
                                    take = False
                            except:
                                pass
                            if take == True:
                                items[str(ctx.message.author.id)][y[0]] = (items[str(
                                    ctx.message.author.id)][y[0]] - (y[1] * int(action2)))
                                json.dump(items, open(
                                    f'{filepath}/config/items.json', "w"))

                        with open(f'{filepath}/config/items.json', "r") as uitems:
                            uitems = json.load(uitems)
                            uitems[str(ctx.message.author.id)
                                   ] = items[str(ctx.message.author.id)]

                            try:
                                mat = (
                                    items[str(ctx.message.author.id)][action1][2])
                            except:
                                mat = action1
                            print("good to go2")
                            waiting[random.randint(0, 1000)] = [
                                ((datetime.now() + timedelta(seconds=time))), ctx.message.author.id, mat, amount]
                            """for x in crafts[action1][0]:
                                count = x[1]
                                print(f"x = {x}")
                                items[str(ctx.message.author.id)][x[0]] = owneditems(ctx.message.author.id, x[0]) - (count * amount)"""

                            json.dump(uitems, open(
                                f'{filepath}/config/items.json', "w"))
                            if amount != 1:
                                await ctx.send(f"{action2} {mat} ({action2 * amount}) crafted! Will finish in {time} seconds.")
                            else:
                                await ctx.send(f"{action2} {mat} crafted! Will finish in {time} seconds.")
                    else:
                        await ctx.send(f"Sorry, you have {chave} {ctype} and you need {cneeded}")
                    # except:
                    #    print("uhhhhh")

#    @tasks.loop(seconds=3)  # I would have it as 1 second, but that causes a fair bit of lag so every 3.
#    async def crafter(self):
#        global waiting
#        if waiting != {}:
#            print(f"waiting = {waiting}")
#        v = []
#        with open(f'{filepath}/config/items.json', "r") as loc:
#            items = json.load(loc)
#            for x in waiting:
#                if datetime.now() >= waiting[x][0]:
#                    try:
#                        items[str(waiting[x][1])][waiting[x][2]] = owneditems(waiting[x][1], waiting[x][2]) + waiting[x][3]
#                    except KeyError:
#                        items[str(waiting[x][1])][waiting[x]
#                                                  [2]] = waiting[x][3]
#                    v.append(x)
#                    user = await self.bot.fetch_user(waiting[x][1])
#                    await user.send(f"Your {waiting[x][3]} {waiting[x][2]} has finished crafting")
#            for x in v:
#                waiting.pop(x)
#            json.dump(items, open(f'{filepath}/config/items.json', "w"))


def setup(bot: commands.Bot):
    bot.add_cog(shop(bot))
