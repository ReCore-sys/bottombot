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
import json
from async_timeout import timeout
from discord.ext import commands, tasks
from tinydb import TinyDB, Query
from datetime import datetime, date, timedelta
from num2words import num2words
import operator
from collections import OrderedDict
from operator import getitem
null = None
filepath = os.path.abspath(os.path.dirname(__file__))
# region Base items
wares = {
    "stone": 10,
    "wood": 15,
    "metal": 20
}

# region Crafting Items
crafts = {
    # Any line that starts with a hash (#) is a comment; what is on that line does not impact the code. It is used to describe the code so feel free to add your own

    # The first part of the craft syntax is the name. In the template below it is is example. The second part is the ingrediants. Each item inside it conatains the item type, the amount needed and whether or not to consume the ingrediant on craft. If True it will bo consumed and if it is False it will not. If you leave the third section blank it will default to consuming the item

    # To add you own crafts is very simple. Just copy the template from below without the hashes of course.

    # "example": [["metal", 3, True], ["wood", 2, True]],

    # just replace the "example" with what you want the name of the new item
    # names are case sensitive so make sure you get it right. Also the commas, brackets and quote marks are vital so make sure you don't leave them out. You also need to add a comma to the end of each item
    # you can also have other crafted items as ingrediants (eg, one item called "oil" and you need 10 oil to make a car). Its pretty easy to do this; just change the ingrediant's name to that of another material
    # example:

    # "oil": [["wood", 10, True], ["metal", 8, True]],
    # "car": [["oil", 10], ["metal", 10]], (Even though this one does not have the consume specifier, it will still consume it)

    # that would be a valid item
    # if you have a github account simply fork the repo (look up how), add the new items then create a pull requests and ping me on discord.
    # if you don't copy the formatting and send your ideas to me over discord.
    # Just some other stuff:
    # 1. make sure all names are lowercase and don't contain spaces
    # 2. no offesive stuff
    # 3. Please don't have people as an option since we will be selling them. Thats not legal anymore
    # 4. Keep it inside the curly brackets

    "steel": [["metal", 4, True], ["stone", 2, True]],
    "fire": [["stone", 2, True], ["wood", 5, True]],
    "furnace": [["stone", 20, True], ["wood", 6, True], ["steel", 2, True], ["fire", 1]],
    "sword": [["steel", 5], ["furnace", 1, False], ["wood", 1]]
}


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


class shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def buy(self, ctx, item=null, itemcount=1):
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
                        print("so that ran")
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
                                print(file1)
                            await ctx.send(f"{itemcount} {item} bought for ${itemcount * wares[item]}")
                        json.dump(file1, open(
                            f'{filepath}/config/items.json', "w"))

    @commands.command()
    async def sell(self, ctx, item=null, price=null, itemcount=1):
        with open(f'{filepath}/config/items.json', "r") as uitems:
            uitems = json.load(uitems)
            try:
                int(uitems[str(ctx.message.author.id)][item])
                if int(uitems[str(ctx.message.author.id)][item]) <= int(itemcount):
                    # Ok I have an actual reason for converting it to a string. Json can't have ints as keys so it completely breaks if I try to do that. I really don't reccomend it.
                    with open(f'{filepath}/config/shops.json', "r") as loc:
                        file1 = dict(json.load(loc))
                        if str(itemcount).isnumeric() == False:
                            await ctx.send("Please enter a number for the number to sell")
                        else:
                            chosen = False, null
                            usedids = []
                            if owneditems(ctx.message.author.id, item) < itemcount:
                                # what to actually run if they can buy the item
                                print("so that ran")
                                with open(f'{filepath}/config/shops.json', "r") as loc2:
                                    file2 = json.load(loc2)
                                    storeid = random.randint(1000000, 999999)
                                    for x in file2:
                                        usedids.append(x)
                                        for z in x:
                                            if file2[x]["item"] == item:
                                                if file2[x]["userid"] == ctx.message.author.id:

                                                    chosen = True, x
                                                    print(chosen)
                                    taken = False
                                    c = 0
                                    while storeid in usedids:
                                        storeid = random.randint(
                                            1000000, 999999)
                                        print("Uh oh")
                                        c = c + 1  # this specific shitscape is to create a unique id for the store. It stores all currently used ids then creates a new one that is not in that list
                                        if c >= 1000000:  # if all 6 digit ids are taken, run this to let people know we got a problem on our hands
                                            print(
                                                "ID cache is full, tf we do from here?")
                                            await ctx.send("Uhhh, this is a problem. All id's are currently used. Contact ReCore to let them know.")
                                            taken = True
                                            continue

                                    # TODO: Create function here to check if the store already exists
                                    if chosen[0] == True:
                                        cid = chosen[1]
                                        print("Got to here")
                                        if price == null:
                                            price = file2[cid]["price"]
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
                                    else:
                                        print("We should not be here")
                                    print("Getting there")
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

    @commands.command()
    async def shop(self, ctx, action1=null, action2=null, action3=1):
        cango = False
        sorted1 = json.load(open(f'{filepath}/config/shops.json', "r"))
        print(sorted1)
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
            embed = discord.Embed(
                title=f"Shop: {action1}", description="Welcome to the shop!", color=0x1e00ff)
            print(sorted1.items())
            sorted1 = dict(OrderedDict(
                sorted(sorted1.items(), key=lambda x: x[1]['username'])))
            print(sorted1)

            for x in sorted1:
                if sorted1[x]["item"] == action1:
                    embed.add_field(name=f"{x} \n${sorted1[x]['price']} ({sorted1[x]['itemcount']} Available)",
                                    value=f"{sorted1[x]['username']}\n", inline=False)
            await ctx.send(embed=embed)

            json.dump(sorted1, open(f'{filepath}/config/shops.json', "w"))

    @commands.command()
    async def craft(self, ctx, action1=null, action2=1):
        # action1: the item's name
        # action2: how many to craft
        with open(f'{filepath}/config/items.json', "r") as loc:
            items = json.load(loc)
            cancraft = True
            cneeded = null
            chave = null
            ctype = null
            var1 = []
            if action1 == null:
                embed = discord.Embed(
                    title=f"Craftable items", description="List of items you can craft", color=0x1e00ff)
                for x in crafts:
                    for y in crafts[x]:
                        var1.append(f"{y[0]}: {y[1]}")
                    embed.add_field(name=f"{x}",
                                    value="\n".join(var1), inline=False)
                    var1 = []
                await ctx.send(embed=embed)
            if str(action2).isnumeric() == False:
                await ctx.send("Sorry, you need to give a number for the amount")
            else:
                if action2 != null:
                    action2 = int(action2)
                try:
                    for y in crafts[action1]:
                        for x in y:
                            for r in crafts[action1]:
                                if owneditems(ctx.message.author.id, r[0]) >= (r[1] * action2):
                                    pass
                                else:
                                    cancraft = False
                                    chave = owneditems(
                                        ctx.message.author.id, r[0])
                                    cneeded = r[1] * action2
                                    ctype = r[0]

                    if cancraft:
                        for y in crafts[action1]:
                            try:
                                if y[2] == True:
                                    items[str(ctx.message.author.id)][y[0]] = (items[str(
                                        ctx.message.author.id)][y[0]] - (y[1] * action2))
                            except:
                                pass

                        with open(f'{filepath}/config/items.json', "r") as uitems:
                            uitems = json.load(uitems)
                            uitems[str(ctx.message.author.id)
                                   ] = items[str(ctx.message.author.id)]
                            try:
                                items[str(ctx.message.author.id)][action1] = (items[str(
                                    ctx.message.author.id)][action1] + action2)
                            except KeyError:
                                items[str(ctx.message.author.id)
                                      ][action1] = action2
                            json.dump(uitems, open(
                                f'{filepath}/config/items.json', "w"))
                            await ctx.send(f"{action2} {action1} crafted!")
                    else:
                        await ctx.send(f"Sorry, you have {chave} {ctype} and you need {cneeded}")
                except:
                    pass


def setup(bot: commands.Bot):
    bot.add_cog(shop(bot))
