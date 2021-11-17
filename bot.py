import os
import threading
import sqlbullshit
import secret_data
import discord
from discord.ext import commands
import platform
import random
import time
import setup
import time
import datetime
import json

print("\u001b[32;1m")
print(
    """

 ______                            ______
|  __  \       _   _              |  __  \       _
| |__)  ) ___ | |_| |_  ___  ____ | |__)  ) ___ | |_
|  __  ( / _ \|  _)  _)/ _ \|    \|  __  ( / _ \|  _)
| |__)  ) |_| | |_| |_| |_| | | | | |__)  ) |_| | |__
|______/ \___/ \___)___)___/|_|_|_|______/ \___/ \___)


""")
print("\u001b[0m")


# this gets the directory this script is in. Makes it much easier to transfer between systems.
filepath = os.path.abspath(os.path.dirname(__file__))

sql = sqlbullshit.sql(filepath + "/data.db", "user")

if os.name != "nt":
    token = secret_data.token
    prefix = "-"
    print("Running linux")
else:
    token = secret_data.test_token
    prefix = "_"
    print("Running windows")
null = None  # so I can write "null" instead of "None" and look like hackerman

intents = discord.Intents.default()
intents.members = True

client = discord.Client()
client = commands.Bot(command_prefix=prefix, intents=intents)
canwelcome = False
client.remove_command('help')
starttime = null


@client.event
async def on_ready():
    if platform.system() == "Windows":
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Testing"))
    else:
        status = random.choice(["ReCore's CPU catch fire", "the old gods die", "missiles fly",
                               "the CCCP commit horrific crimes", "bentosalad on twitch", "RealArdan on twitch"])
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status))

    setup.begin()
    print("The bot is up")
    f = open(f"{filepath}/logs.txt", "a")
    f.write(f"\n---\n{datetime.datetime.now()} Bot started\n---\n")
    f.close()
    modules = ["money", "cross", "modules", "bounty", "shop", "admin", "misc"]
    for x in modules:
        client.load_extension(x)
    # We sleep here so wavelink has time to get set up
    #p = setup.wavelink_start()
    # client.load_extension("music")


@client.event
async def on_guild_join(guild):
    """
    When the bot joins a server, it will send a message to the server's general channel. It also logs the server's name, id, owner and join date to a json file
    """
    f = open(f"{filepath}/logs.txt", "a")
    f.write(f"\n---\n{datetime.datetime.now()} Joined {guild.name}\n---\n")
    f.close()
    print(f"Joined {guild.name}")
    f = open(f"{filepath}/logs.txt", "a")
    f.write(
        f"\n---\n{datetime.datetime.now()} {guild.name} has {len(guild.members)} members\n---\n")
    f.close()
    try:
        f = open(f"{filepath}/json/servers.json", "r")
        data = json.load(f)
        f.close()
    except FileNotFoundError:
        f = open(f"{filepath}/json/servers.json", "w")
        data = {}
        f.close()
    data[guild.id] = {
        "name": guild.name,
        "owner": guild.owner.id,
        "created": guild.created_at,
        "members": len(guild.members)
    }
    f = open(f"{filepath}/json/servers.json", "w")
    json.dump(data, f)
    f.close()
    for channel in guild.text_channels:
        if canwelcome == True:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send('Heyo! I am bottombot, a cancerous mess. You can join my discord server here: https://discord.gg/2WaddNnuHh \nYou can also invite the bot to other servers with this link: https://discord.com/api/oauth2/authorize?client_id=758912539836547132&permissions=8&scope=bot \nUse -help to find out what commands I can use!')
            break


@client.command()
async def init(ctx):
    """
    Do the same as the server join, but for when people need to set up the server's info again. Don't send the welcome message though
    """
    f = open(f"{filepath}/logs.txt", "a")
    f.write(f"\n---\n{datetime.datetime.now()} Joined {ctx.guild.name}\n---\n")
    f.close()
    print(f"Joined {ctx.guild.name}")
    f = open(f"{filepath}/logs.txt", "a")
    f.write(
        f"\n---\n{datetime.datetime.now()} {ctx.guild.name} has {len(ctx.guild.members)} members\n---\n")
    f.close()
    try:
        f = open(f"{filepath}/json/servers.json", "r")
        data = json.load(f)
        f.close()
    except FileNotFoundError:
        f = open(f"{filepath}/json/servers.json", "w")
        data = {}
        f.close()
    data[ctx.guild.id] = {
        "name": ctx.guild.name,
        "owner": ctx.guild.owner.id,
        "created": str(ctx.guild.created_at),
        "members": len(ctx.guild.members)
    }
    f = open(f"{filepath}/json/servers.json", "w")
    json.dump(data, f)
    f.close()
    await ctx.send("Database setup!")


@client.event
async def on_member_join(member):
    role = discord.utils.get(member.server.roles, id=821166866348376116)
    if (member.id == 821161880734793738):
        await client.add_roles(member, role)


@client.event
async def on_message(message):
    if isinstance(message.channel, discord.channel.DMChannel) == False:
        if '<@' in message.content:
            if str(message.guild.id) not in os.listdir(f"{filepath}/serversettings"):
                os.system(f'mkdir serversettings/{message.guild.id}')
                # this makes the relevant folders for any servers that don't already have a serversettings entry.
            if "replay.txt" not in os.listdir(f"serversettings/{message.guild.id}"):
                os.system(
                    f"touch serversettings/{message.guild.id}/replay.txt")
            if message.author != client.user:
                pingC = (message.content).encode("utf-8", "ignore")
                pingC = pingC.decode("utf-8", "ignore")
                pingU = message.author
                f = open(
                    f"{filepath}/serversettings/{message.guild.id}/replay.txt", "a")
                f.write(f"\n'{pingC}' was sent by {pingU}")
                f.close()
        elif message.content == "hello there":
            await message.channel.send("General Kenobi")
        r = random.randint(0, 10)
        u = message.author.id
        if (r == 9) and (message.author.id != 758912539836547132):
            if sql.get(u, "money") != null:
                sql.add(random.randint(1, 10), u, "money")
                print(
                    f"$1 was added to {message.author} in server {message.guild.name}")
        # this breaks everything if removed. I don't advise it.
        await client.process_commands(message)


if __name__ == '__main__':
    client.run(token)
