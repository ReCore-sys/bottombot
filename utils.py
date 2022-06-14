""" A simple set of utility functions
"""
import os
import time

import ujson as json

filepath = os.path.dirname(os.path.realpath(__file__))


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
    except TypeError:
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

    for x in ["B", "KB", "MB", "GB", "TB"]:
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
    gid = ctx.guild.id
    timestring = time.strftime("%Y-%m-%d %H:%M:%S")
    log = f"{timestring} | {guild} ({gid}) | {uname} ({uid}) | #{channel} | {cmd}\n"
    with open(f"{filepath}/logs/{time.strftime('%Y-%m-%d')}.log", "a+") as f:
        f.write(log)


def match_regex(regex, text):
    """match_regex
    \nMatches a regex to the message

    Parameters
    ----------
    regex : str
        The regex to match

    Returns
    -------
    bool
        Whether the regex matched
    """
    return regex.match(text) is not None
