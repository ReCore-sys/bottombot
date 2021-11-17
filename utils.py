""" A simple set of utility functions
"""
import time
import ujson as json
import os
import sqlbullshit as sqlbullshit
filepath = os.path.dirname(os.path.realpath(__file__))


debuffs = dict()


def is_jsonable(x):
    """is_jsonable 
    \nFinds out whether a variable can be saved to a json file through the glory of try/except

    Parameters
    ----------
    x : str, probably
        The object to test

    Returns
    -------
    bool
        Whether it can be saved
    """
    try:
        json.dumps(x)
        return True
    except:
        return False


def convert_bytes(num):
    """convert_bytes
    \n
    Turns a bytecount into a nicely readable string

    Parameters
    ----------
    num : int
        Number of bytes to evaluate

    Returns
    -------
    str
        Human readable string
    """

    step_unit = 1024

    for x in ['B', 'KB', 'MB', 'GB', 'TB']:
        if num < step_unit:
            return f"{round(num)} {x}"
        num /= step_unit


def shred(d, n=2):
    """shred\n
    Cuts a dict into a list of n sized dicts

    Parameters
    ----------
    d : dict
        The dict to cut
    n : int, optional
        Size of each chunk, by default 2

    Returns
    -------
    list
        List of dicts
    """
    c = 0
    y = list()
    g = dict()
    for x in d:
        g[x] = d[x]
        c = c + 1
        if c == n:
            y.append(g)
            g = dict()
            c = 0
    if g != dict():
        y.append(g)
    return y

# TODO redo this thing cos it is shit


def milliontopercent(num):
    return (num/1000000) * 100


def log(ctx):
    """log
    \nWrites a log to a html from a context object

    Parameters
    ----------
    ctx : IDFK
        Discord's context object
    """
    cmd = ctx.message.clean_content
    guild = ctx.guild.name
    uname = ctx.author.display_name + "#" + ctx.author.discriminator
    uid = ctx.author.id
    channel = ctx.channel.name
    cog = ctx.cog.qualified_name
    gid = ctx.guild.id
    cname = ctx.command.name
    css = """
    <style>
    a {
        font-family: "Apple Chancery", cursive;
        color: white;
    }
    p {
        font-family: "Impact", fantasy;
        color: red;
    }
    div {
        margin: 5vh;
    }
    body {
        background: linear-gradient(
        90deg,
        rgba(2, 0, 36, 1) 0%,
        rgba(9, 9, 121, 1) 50%,
        rgba(2, 0, 66, 1) 100%
        );
        overflow: auto;
    }

    a:hover span.name {
        display: none;
    }
    span.id {
        display: none;
    }
    a:hover span.id {
        display: inline-block;
    }
    a:hover span.sname {
        display: none;
    }
    span.sid {
        display: none;
    }
    a:hover span.sid {
        display: inline-block;
    }
    </style>
    """
    if len(open(f"{filepath}/logs.html", "rb").read()) == 0:
        with open(f"{filepath}/logs.html", "w") as f:
            f.write(css + "\n")
    with open(f"{filepath}/logs.html", "a") as f:
        f.write(
            f"<div><p>{time.ctime()}: <a><span class='name'><strong>{uname}</strong></span> <span class='sid'>({uid})</span> invoked <strong>'{cmd}'</strong> ({cname} command) in <span class='sname'><strong>{guild}</strong></span><span class='sid'>({gid})</span>'s <strong>{channel}</strong> channel on the <strong>{cog}</strong> cog</a></p></div>\n")


# ==========================================================================
#                              Levels
#   Ok so this bit is rather spicy
#   The loop below creates a dict with all the levels and their
#   coresponding required xp. The function then does some weird maths
#   to find out some info.
#   xp under the minimum level and over the max are
#   handled weird. Min just does the same maths but uses 0 and the min as
#   bounds. Max does a lot of the same stuff but not go up to the next level
#   when reached. Instead it just keeps going and has a needed of -1.
# ==========================================================================
levels = dict()
pre = 100

for x in range(1, 51):
    levels[x] = pre
    # Since levels don't technically exist, we have to add 1.25x to the amount required for the last level
    # It's annoying but i don't feel like storing levels alongside xp so nyeh
    # Also the whole multiplying and dividing by 5 thing is so the result is always a multiple of 5
    pre = 5 * round((round(pre * 1.25) + pre)/5)


def level(inp: int):
    """level
    \nGets information about the user's level from their xp

    Parameters
    ----------
    inp : int
        the total xp the user has

    Returns
    -------
    dict
        A dictionary of information
    """
    # c: counter
    c = 1
    # l: list
    l = list(levels.keys())
    # info: dict to hold the info
    info = dict()
    # mininum: min was taken
    minimum = levels[min(l)]
    # First check if it is under the minimum
    if inp <= minimum:
        # Level is 0
        info["level"] = 0
        # Total xp you need for the level is the min
        info["total"] = minimum
        # Needed is min take amount you have
        info["needed"] = minimum - inp
        # Since lower bound is 0, its just ur xp
        info["over"] = inp
        info["thislevel"] = minimum
        print(info)
        return info
    # Now we loop through the rest
    while True:
        # First check if we have reached the max
        if c == max(l):
            # Level is just the max
            info["level"] = max(l)
            # Total needed is max again
            info["total"] = levels[c]
            # Amount left is -1 cos fuck you thats why
            info["needed"] = -1
            # Amount over is max - ur xp
            info["over"] = inp - levels[c]
            info["thislevel"] = levels[c] - levels[c-1]
            print(info)
            return info
        # Most cases fall into this
        elif inp >= levels[c] and inp < levels[c + 1]:
            # Level is what the counter is currently at
            info["level"] = c
            # Find out how much is needed in total for the next level
            info["total"] = levels[c + 1]
            # Total needed take ur xp
            info["needed"] = levels[c + 1] - inp
            # The amount needed to get to your current level take how much xp you have
            info["over"] = inp - levels[c]
            info["thislevel"] = levels[c+1] - (levels[c])
            print(info)
            return info
        # If it wasn't any of these, up the counter and try again
        c += 1
