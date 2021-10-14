import asyncio
import datetime
import json
import os
import random
import time
import urllib.parse
from datetime import date, datetime, timedelta

import async_cse
import botlib
import bottomlib
import discord
import helplib
import money
import requests
import settings
from discord.ext import commands, menus
from PIL import Image, ImageDraw, ImageFont

time = None
answer = None
wrong = None
done = False
winner = None
winnerid = None
filepath = os.path.abspath(os.path.dirname(__file__))
cap = money.cap()
used = []


def text_on_img(filename='image.png', text="Hello", size=12):
    try:
        font = ImageFont.truetype("/Library/fonts/Arial.ttf", size)
    except:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/freefont/FreeMono.ttf", size)
    image = Image.new(mode="RGB", size=(
        int(size) * len(text), size + 50), color=(54, 57, 63))
    draw = ImageDraw.Draw(image)
    draw.text((10, 10), text, font=font, fill=(255, 255, 0))
    image.save(filename)


class trivia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        global time
        global answer
        global wrong
        global done
        global winner
        global winnerid
        global used
        whole = wrong
        whole.append(answer)
        if message.author.id != 822023355947155457:
            if done == False:
                try:
                    if datetime.now() <= time:
                        if message.content == answer:
                            if message.author.id not in used:
                                await message.channel.send("That was right!")
                                done = True
                                winner = message.author
                                winnerid = message.author.id
                                answer = None
                    elif datetime.now() > time:
                        if message.content == answer:
                            print("Too late!")
                            answer = None
                except:
                    pass
            elif message.content == answer:
                await message.channel.send("Sorry, it has already been answered")
        if message.content in whole:
            used.append(message.author.id)

    @commands.command()
    async def trivia(self, ctx):
        global time
        global answer
        global wrong
        global done
        global winner
        global winnerid
        global used
        used = []
        delay = 20
        list = []
        URL = "https://trivia.willfry.co.uk/api/questions?categories=geography,general_knowledge,history,literature,music,science,society_and_culture&limit=1"
        r = requests.get(url=URL)
        t = r.json()
        wrong = t[0]["incorrectAnswers"]
        answer = t[0]["correctAnswer"].strip()
        question = t[0]["question"]
        time = datetime.now() + timedelta(seconds=delay)
        print(wrong)
        for x in wrong:
            list.append(x.strip())
        list.append(answer)
        print(list)
        random.shuffle(list)
        embed = discord.Embed(
            title=question, description="\u200b")
        for x in list:
            embed.add_field(name=x, value="\u200b")
        await ctx.send(embed=embed)
        await asyncio.sleep(delay)
        if done == True:
            prize = random.randint(20, 30)
            if money.balfind(winnerid) + prize <= cap[money.rankfind(winnerid)]:
                await ctx.send(f"The question has been answered! The winner was {winner} and they won ${prize}")
                money.addmoney(winnerid, prize)
            else:
                await ctx.send("Sorry, that goes over your wallet cap")
            winner = None
            winnerid = None
            done = False
        else:
            await ctx.send(f"The question was not answered...")
            winner = None
            winnerid = None
            done = False


def setup(bot: commands.Bot):
    bot.add_cog(trivia(bot))
