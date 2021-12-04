import json
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


class BotError(Exception):
    """Custom exception for the bot"""

    pass


def check_banned(ctx):
    if ctx.author.id in banned_ids:
        return False
    return True


def nope():
    return random.choice(
        [
            "Did you really think that would work?",
            "I'm not stupid, you are banned",
            "Begone",
            "Nope",
            "All aboard the nope train to nahland",
            "Twat",
            "How about no",
            "Haha no",
            "God has forsaken you",
            "November Oscar Tango Golf Uniform November November Alpha Hotel Alpha Papa Papa Echo November",
            r"\:/",
        ]
    )


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
            string = random.choice(j[comp]).format(ctx.author.name)
            if "http" in string:
                return ("url", string)
            return "\n*" + string + "*"
        else:
            return ""


pricelist = {}
stocklist = {}


def getaverage(reloadstocks=False):
    """Using the SQL module, find people's average stock price, average money and a ratio between them"""
    # FIXME: You thought you were smart using your premade functions? Well you ain't. This does not work and you need to fix your crap.
    # If we need to fetch the data again
    if reloadstocks is False:
        # Gets a list/array of all the people's money. AT LEAST IT SHOULD
        allmoney = [int(x[0]) for x in sql.getall("money", mode="field")]
        # Same as above, but for stocks. STILL DOESN'T FUCKING WORK
        allstocks = [int(x[0]) for x in sql.getall("stocks", mode="field")]
        # Gets everyone's ids
        allusers = sql.getall("id", mode="field")
        # Stick em in a dict
        for x in range(len(allusers)):
            pricelist[allusers[x]] = allmoney[x]
            stocklist[allusers[x]] = allstocks[x]
    # If we don't need to fetch the data again
    else:
        # Load it from the dictionary
        allmoney = [pricelist[x] for x in pricelist]
        allstocks = [stocklist[x] for x in stocklist]
        allusers = [x for x in pricelist]
    # Find the average of the money
    avmoney = sum(allmoney) / len((allmoney))
    # Find the average of the stocks
    avstocks = sum(allstocks) / len(allstocks)
    # Find the ratio of the two
    avratio = avstocks / avmoney
    return avratio


def findchange(price, reloadstocks, id, mode):
    """Using the SQL thing, find the average of people's stock to money ratio as a 1 to 0 value, then multiply change by that value
    The average of people's stock to money ratio is found with the getaverage function"""
    # Use the function above to make it do shit
    avratio = getaverage(reloadstocks)
    # Divide the price by 8, then multiply by the average ratio
    # This is so the price change is capped at a 12.5% increase per stock bought
    endcost = (price / 8) * avratio
    # If we are not reloading the data, modify the saved data to account for the new price
    if reloadstocks is False:
        if mode == "buy":
            pricelist[id] -= endcost
            stocklist[id] += 1
        elif mode == "sell":
            pricelist[id] += endcost
            stocklist[id] -= 1
    # Return the amount the price will change by
    return endcost
    """
    For example, if we had a stock price of 50 and the average ratio was 0.5, the price would change by 50 + 50/8 * 0.5 = 60.
    This means that if you bought 3 stocks, the first would cost 50, the second would cost 50 + 50/8 * 0.5 = 60, and the third would cost 60 + 60/8 * 0.5 = 72.
    Of course, an average ratio of 50% is pretty hard to get. At the time of writing, it is 11.8%
    """


def configs(section=None, key=None):
    """Loads the configs from the json file"""
    with open(f"{filepath}/json/configs.json", "r") as f:
        configs = json.load(f)
        if section not in configs:
            raise BotError("Section not found in configs")
        if key is None:
            return configs
        else:
            if key not in configs[section]:
                raise BotError("Key not found in configs")
            else:
                return configs[section][key]
