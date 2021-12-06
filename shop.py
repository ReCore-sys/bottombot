import os
import random
import sys
import time

import discord
import ujson as json
from discord.ext import commands
from disputils import BotEmbedPaginator

import sqlbullshit
import utils

filepath = os.path.dirname(os.path.realpath(__file__))

sql = sqlbullshit.sql(f"{filepath}/data.db", "user")


class User:
    def __init__(self, uid: int):
        self.uid = uid
        i = sql.get(self.uid, "inv")
        if i == None:
            self.inv = {}
            sql.set(json.dumps(self.inv), self.uid, "inv")
        else:
            self.inv = json.loads(i)

    def inventory(self):
        return self.inv

    def additem(self, item: str, amount: int):
        if item in self.inv:
            self.inv[item] += amount
        else:
            self.inv[item] = amount
        sql.set(json.dumps(self.inv), self.uid, "inv")
        return True

    def takeitem(self, item: str, amount: int):
        if item in self.inv:
            if self.inv[item] >= amount:
                self.inv[item] -= amount
                sql.set(json.dumps(self.inv), self.uid, "inv")
                return True
            else:
                return False, "Not enough items"
        else:
            return False, "Item not in inventory"


class Store:
    def __init__(self):
        self.items = self.load()

    def load(self):
        with open(f"{filepath}/json/shop.json", "r") as f:
            return json.load(f)


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def inv(self, ctx):
        # Set up the class for the inventory
        user = User(ctx.author.id)
        # Get the user's inventory as a dict
        inv = user.inventory()
        # Create the embed
        e = discord.Embed(title="Inventory", color=discord.Color.blue())
        # If we have items in our inv, procceed
        if len(inv) > 0:
            # Loop through the items
            for x in inv:
                # Add the item to the embed
                e.add_field(name=x, value=inv[x])
        else:
            # If we don't have any items, tell the user
            e.add_field(name="Oops", value="You have no items")
        # Send the embed
        await ctx.send(embed=e)

    @commands.command()
    async def shop(self, ctx):
        # set up some basic variables here
        e = list()  # A list of the embeds to store
        store = Store()
        items = store.items  # The items in the shop
        chopped = utils.shred(
            items, 5
        )  # The items in the shop, chopped into chunks of 5
        pagenum = 1  # The page number
        # Iterates thru the list of dicts
        # item is the internal name of the item: example-item
        # page[item]["name"] is the display name: Example Item
        # page[item]["price"] is the price: 100
        # page[item]["description"] is the description: This is an example item
        for page in chopped:
            embed = None
            # Compile the page of the Embed
            # Title is page number
            embed = discord.Embed(
                title=f"Page {pagenum}",
                description=f"Page {pagenum} of {len(chopped)}",
                color=discord.Color.blue(),
            )
            pagenum = pagenum + 1
            for item in page:
                # Add the items
                embed.add_field(
                    name=page[item]["name"],
                    value="\n".join(
                        (
                            f"ID: {page[item]['id']}",
                            page[item]["description"],
                            f"${page[item]['price']}",
                        )
                    ),
                    inline=False,
                )
            # Add the page to the list and keep going
            e.append(embed)
            embed = None
        # Pull it all together and create the paged embed
        paginator = BotEmbedPaginator(ctx, e)
        # Send the embed
        await paginator.run()


def setup(bot):
    bot.add_cog(Shop(bot))
