import json
from discord.ext import commands
import os
import random
banned_ids = []
paid_ids = []
filepath = os.path.abspath(os.path.dirname(__file__))
"""SET UP"""

with open(f"{filepath}/configs.json", "r") as f:
    j = json.load(f)
    banned_ids = j["banned_ids"]

"""CHECK FUNCTION"""


def check_banned(ctx):
    if ctx.author.id in banned_ids:
        return False
    return True


def nope():
    return random.choice(["Did you really think that would work?", "I'm not stupid, you are banned", "Begone", "Nope", "All aboard the nope train to nahland", "Twat", "How about no", "Haha no", "God has forsaken you", "November Oscar Tango Golf Uniform November November Alpha Hotel Alpha Papa Papa Echo November", r"\:/"])


def nametoid(name):
    val = str(name)
    val = val.replace("<@!", "")
    val = val.replace(">", "")
    print(val)
    return val
