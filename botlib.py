import discord
from discord.ext import commands
import async_cse, asyncio
import os
import random
banned_ids = []
paid_ids = []
filepath = os.path.abspath(os.path.dirname(__file__))
"""SET UP"""

with open(f"{filepath}/config/BannedIDs.txt", "r") as f:
    #For every line in the file
    for line in f:
        ID = int(line)
        banned_ids.append(ID)

"""CHECK FUNCTION"""

def check_banned(ctx):
    if ctx.author.id in banned_ids:
        return False
    return True

def nope():
    return random.choice(["Did you really think that would work?","I'm not stupid, you are banned","Begone","Nope","All aboard the nope train to nahland","Twat","How about no","Haha no","God has forsaken you", "November Oscar Tango Golf Uniform November November Alpha Hotel Alpha Papa Papa Echo November", r"\:/"])


with open(f"{filepath}/config/premium.txt", "r") as f:
    #For every line in the file
    for line in f:
        ID = int(line)
        paid_ids.append(ID)

"""CHECK FUNCTION"""

def premium(ctx):
    if ctx.guild.id in paid_ids:
        return True
    return False

def nametoid(name):
    val = str(name)
    val = val.replace("<@!","")
    val = val.replace(">","")
    print(val)
    return val