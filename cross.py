# this will be a file to manage the hellhole that will be cross server chat. Dear god. Help me please.
import os
import asyncio
import math
import random
import time
import async_cse
import discord
import datetime
import urllib.parse
from async_timeout import timeout
from discord.ext import menus, commands, tasks
import botlib
import bottomlib
import money
import settings

# init stuff
filepath = os.path.abspath(os.path.dirname(__file__))
# init stuff


waiting = None
messages = []
servers = {}


class cross(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.checker.start()  # starts the loop that relays messages

    @commands.command()
    # command to set up connecting servers. It's all in variables, so resetting will wipe all connections
    async def join(self, ctx):
        if settings.check(ctx.message.guild.id, "get", "cross"):
            # ok cos I can't really be bothered, whenever I refer to a server's id in this bit, I mean the channel, not server
            global waiting
            global servers
            if waiting == None:  # if no one is in the list, join it
                await ctx.send("Ok, added you to the waiting list")
                waiting = ctx.message.channel.id  # sets the waitlist to your server id
            elif waiting == ctx.message.channel.id:  # if the waitlist is your server id, don't do anything
                await ctx.send("You are the only one in the list right now. Do -leave to take youself out of the list")
            elif ctx.message.channel.id in servers:
                await ctx.send("You are currently in a conversation")
            else:  # ok this is the funky bit. If someone else is in the list, we start a conversation with them
                # gets the other server and stores it into a variable for safekeeping
                otherchannel = waiting
                # creates a dict entry with the key being the other server's id and the value as this server's id
                servers[otherchannel] = ctx.message.channel.id
                # same as above but the other way around
                servers[ctx.message.channel.id] = otherchannel
                waiting = None
                try:
                    waiting.remove[ctx.message.channel.id]
                except:
                    pass  # empties the wait list so other servers can join
                await ctx.send("Ok, connected you to another server")
                address = self.bot.get_channel(int(otherchannel))
                await address.send("Ok, you are connected to another server now")
        else:
            await ctx.send("Sorry, cross server chat is disabled for this server")

    @commands.Cog.listener()
    async def on_message(self, message):
        global waiting
        global servers
        global messages
        if ("-" not in message.content) and ("_" not in message.content):
            if (message.author.id != 822023355947155457) and (message.author.id != 758912539836547132):
                if message.channel.id in servers:  # if your id is in the list of servers, write your message and server id to the list of pending messages
                    message1 = message.content
                    unicode = u"\uFF20"
                    message1 = message1.replace('@', unicode)
                    # msg = [address, "sender : message"]
                    msg = [int(servers[message.channel.id]),
                           f"{message.author} : {message1}"]
                    messages.append(msg)

    @commands.command()
    async def leave(self, ctx):
        global waiting
        global servers
        if settings.check(ctx.message.guild.id, "get", "cross"):
            if ctx.message.channel.id not in servers:
                # if you are not connected to any servers but you are in the waitlist, remove you from that
                if waiting == ctx.message.channel.id:
                    await ctx.send("Removed you from the waiting list")
                    waiting = None
                else:
                    # if you are not in either, do nothing
                    await ctx.send("You are not in the waiting list")
            else:
                # gets the other server's id
                otherserver = servers[ctx.message.channel.id]
                # remove the dict entires for both servers
                servers.pop(ctx.message.channel.id)
                servers.pop(otherserver)
                # get the other channel's id so you can inform them that you left
                address = self.bot.get_channel(int(otherserver))
                await ctx.send("You have disconnected")
                await address.send("You have disconnected")
        else:
            await ctx.send("Sorry, cross server chat is disabled for this server")

    @tasks.loop(seconds=1)
    async def checker(self):
        global messages
        global servers
        for x in messages:  # for every entry in the messages list, pull the message and the address, send it off, then remove it from the list. I would have used a string instead of a list, but this means we can have more than one message pending at once
            address = x[0]
            message = x[1]
            address = self.bot.get_channel(int(address))
            await address.send(message)
            messages.remove(x)


def setup(bot: commands.Bot):
    bot.add_cog(cross(bot))
