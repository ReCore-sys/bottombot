import json
from discord.ext import commands
import os
import random
import sqlbullshit
banned_ids = []
paid_ids = []
filepath = os.path.abspath(os.path.dirname(__file__))
"""SET UP"""
sql = sqlbullshit.sql(f"{filepath}/data.db", "user")

with open(f"{filepath}/json/configs.json", "r") as f:
    banned_json = json.load(f)
    banned_ids = banned_json["banned_ids"]

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


def stockcomment(ctx, price):
    bal = sql.get(ctx.author.id, "money")
    stocks = int(sql.get(ctx.author.id, "stocks"))
    # s = stocks
    # p = price
    # b = bal
    # Stocks
    if stocks == 0:
        s = "n"
    elif stocks < 10:
        s = "l"
    elif stocks < 20:
        s = "m"
    else:
        s = "h"
    # End stocks

    # Price
    if price < 40:
        p = "l"
    elif price < 60:
        p = "m"
    else:
        p = "h"
    # End price

    # Balance
    if bal < 100:
        b = "l"
    elif bal < 1000:
        b = "m"
    else:
        b = "h"
    # End balance
    # Stick all the things together
    comp = s + p + b
    # Load the json file
    with open(f"{filepath}/json/stock_comment.json", "r") as f:
        f = json.load(f)
        # Create a new dict that only has the comments and the keys
        j = {k: v["comment"] for k, v in f.items()}
        del f
        # Check if the key exists. It probably does, but if not, return an empty string
        if comp in j:
            # If the comment is blank, return an empty string
            if j[comp] == []:
                return ""
            # if it does exist, pick a random comment from the list and format it with the user's name, then return it
            string = random.choice(j[comp]).format(
                ctx.author.name)
            return "\n*" + string + "*"
        else:
            return ""
