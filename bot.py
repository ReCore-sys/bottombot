import datetime
import json
import os
import platform
import random
import re

import discord
from discord.ext import commands

import botlib
import secretdata
import setup
import sqlbullshit
import utils

filepath = os.path.dirname(os.path.realpath(__file__))

print("\u001b[32;1m")
with open(f"{filepath}/banner.txt", "r", encoding="utf-8") as f:
    print(f.read())
print("\u001b[0m")


def onwindows() -> bool:
    return os.name == "nt"


async def statistics(cid):
    with open(f"{filepath}/json/stats.json", "w") as f:
        f.write("{}")
    reglist = {}
    with open(f"{filepath}/json/stats.json", "r") as f:
        stats = json.load(f)
    channel = await client.fetch_channel(cid)
    print("Fetching messages")
    messages = await channel.history(limit=2000).flatten()
    msgs = dict()
    for message in messages:
        msgs[message.id] = {
            "content": message.content,
            "author": message.author.id,
            "timestamp": message.created_at,
        }

    reglist["stocks sold"] = re.compile(
        r"(\d+) stocks sold for \$([\d|\.]+)", re.DOTALL
    )
    reglist["stocks bought"] = re.compile(
        r"(\d+) stocks bought for \$([\d|\.]+)", re.DOTALL
    )
    for messageraw in msgs:
        message = msgs[messageraw]
        if message["author"] not in stats:
            stats[message["author"]] = {
                "stocks sold": 0,
                "stocks bought": 0,
                "money spent": 0,
                "money earned": 0,
            }
        for expression in reglist:
            reg = reglist[expression]
            if bool(reg.match(message["content"])):
                ind = list(msgs.keys()).index(messageraw)
                if ind == 0:
                    ind = 1
                uid = msgs[list(msgs.keys())[ind - 1]]["author"]
                if expression == "stocks sold":
                    stocksold = int(reg.match(message["content"]).group(1))
                    stats[uid]["stocks sold"] += stocksold
                    moneyearned = float(reg.match(message["content"]).group(2))
                    stats[uid]["money earned"] += moneyearned
                    del moneyearned, stocksold
                elif expression == "stocks bought":
                    stockbought = int(reg.match(message["content"]).group(1))
                    if stockbought > 100:
                        pass
                    stats[uid]["stocks bought"] += stockbought
                    moneyspent = float(reg.match(message["content"]).group(2))
                    stats[uid]["money spent"] += moneyspent
                    del moneyspent, stockbought

    with open(f"{filepath}/json/stats.json", "w") as f:
        json.dump(stats, f)


isbeta = onwindows()

# this gets the directory this script is in. Makes it much easier to transfer between systems.
filepath = os.path.abspath(os.path.dirname(__file__))

sql = sqlbullshit.sql(filepath + "/data.db", "user")

token = secretdata.token
prefix = "-"
null = None  # so I can write "null" instead of "None" and look like hackerman

intents = discord.Intents.default()
intents.members = True

client = discord.Client()
client = commands.Bot(command_prefix=prefix, intents=intents)
canwelcome = botlib.configs('misc', "welcome")
client.remove_command("help")
starttime = null


@client.event
async def on_ready():
    if isbeta == "Windows":
        await client.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="Testing"
            )
        )
    else:
        status = random.choice(
            [
                "ReCore's CPU catch fire",
                "the old gods die",
                "missiles fly",
                "the CCCP commit horrific crimes",
                "bentosalad on twitch",
                "RealArdan on twitch",
            ]
        )
        await client.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name=status)
        )
    # await statistics(822021957527535617)
    await setup.begin()
    print("The bot is up")
    if isbeta is False:
        with open(f"{filepath}/logs.txt", "a") as f:
            f.write(f"\n---\n{datetime.datetime.now()} Bot started\n---\n")
    modules = ["money", "cross", "modules",
               "bounty", "admin", "misc", "shop", "private"]
    for x in modules:
        client.load_extension(x)
    # We sleep here so wavelink has time to get set up
    if isbeta is False:
        client.load_extension("music")


@client.event
async def on_guild_join(guild):
    """
    When the bot joins a server, it will send a message to the server's general channel. It also logs the server's name, id, owner and join date to a json file
    """
    with open(f"{filepath}/logs.txt", "a") as f:
        f.write(f"\n---\n{datetime.datetime.now()} Joined {guild.name}\n---\n")
    print(f"Joined {guild.name}")
    with open(f"{filepath}/logs.txt", "a") as f:
        f.write(
            f"\n---\n{datetime.datetime.now()} {guild.name} has {len(guild.members)} members\n---\n"
        )
    try:
        with open(f"{filepath}/json/servers.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        with open(f"{filepath}/json/servers.json", "w") as f:
            data = {}
    data[guild.id] = {
        "name": guild.name,
        "owner": guild.owner.id,
        "created": guild.created_at,
        "members": len(guild.members),
    }
    with open(f"{filepath}/json/servers.json", "w"):
        json.dump(data, f)

    if canwelcome:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(
                    "Heyo! I am bottombot, a cancerous mess. You can join my discord server here: https://discord.gg/2WaddNnuHh \nYou can also invite the bot to other servers with this link: https://discord.com/api/oauth2/authorize?client_id=758912539836547132&permissions=8&scope=bot \nUse -help to find out what commands I can use!"
                )
            break


@client.command()
async def init(ctx):
    utils.log(ctx)
    """
    Do the same as the server join, but for when people need to set up the server's info again. Don't send the welcome message though
    """
    with open(f"{filepath}/logs.txt", "a") as f:
        f.write(
            f"\n---\n{datetime.datetime.now()} Joined {ctx.guild.name}\n---\n")

    print(f"Joined {ctx.guild.name}")
    with open(f"{filepath}/logs.txt", "a") as f:
        f.write(
            f"\n---\n{datetime.datetime.now()} {ctx.guild.name} has {len(ctx.guild.members)} members\n---\n"
        )

    try:
        with open(f"{filepath}/json/servers.json", "r") as f:
            data = json.load(f)

    except FileNotFoundError:
        with open(f"{filepath}/json/servers.json", "w") as f:
            data = {}

    data[ctx.guild.id] = {
        "name": ctx.guild.name,
        "owner": ctx.guild.owner.id,
        "created": str(ctx.guild.created_at),
        "members": len(ctx.guild.members),
    }
    with open(f"{filepath}/json/servers.json", "w") as f:
        json.dump(data, f)

    await ctx.send("Database setup!")


@client.event
async def on_member_join(member):
    role = discord.utils.get(member.server.roles, id=821166866348376116)
    if member.id == 821161880734793738:
        await client.add_roles(member, role)

ranks = dict()

with open(f"{filepath}/json/ranks.json", "r") as f:
    d = json.load(f)
    for x in d:
        ranks[int(x)] = d[x]


namestorank = dict()

for x in ranks:
    f = ranks[x]["name"]
    namestorank[(f.lower()).replace(" ", "")] = x


@client.event
async def on_message(message):
    if isinstance(message.channel, discord.channel.DMChannel) is False:
        if "<@" in message.content:
            if str(message.guild.id) not in os.listdir(f"{filepath}/serversettings"):
                os.system(f"mkdir serversettings/{message.guild.id}")
                # this makes the relevant folders for any servers that don't already have a serversettings entry.
            if "replay.txt" not in os.listdir(f"serversettings/{message.guild.id}"):
                os.system(
                    f"touch serversettings/{message.guild.id}/replay.txt")
            if message.author != client.user:
                pingC = (message.content).encode("utf-8", "ignore")
                pingC = pingC.decode("utf-8", "ignore")
                pingU = message.author
                f = open(
                    f"{filepath}/serversettings/{message.guild.id}/replay.txt", "a"
                )
                f.write(f"\n'{pingC}' was sent by {pingU}")

        elif message.content == "hello there":
            await message.channel.send("General Kenobi")
        r = random.randint(0, 10)
        u = message.author.id
        if (r == 9) and (message.author.id != 758912539836547132):
            if sql.doesexist(u):
                addition = random.randint(1, 10)
                if sql.get(u, "money") + addition <= ranks[sql.get(message.author.id, "rank")]["cap"]:
                    sql.add(addition, u, "money")
                print(
                    f"$1 was added to {message.author} in server {message.guild.name}"
                )
        # this breaks everything if removed. I don't advise it.
        await client.process_commands(message)


if __name__ == "__main__":
    client.run(token)
