import os
import random
import time
import async_cse
import discord
import datetime
import urllib.parse
import requests
from discord.ext import menus, commands
import botlib
import bottomlib
import money
import json
import settings
import helplib
import asyncio
from datetime import datetime, date, timedelta
from PIL import Image, ImageDraw, ImageFont

time = None
answer = None
wrong = None
done = False
winner = None
winnerid = None
filepath = os.path.abspath(os.path.dirname(__file__))
cap = money.cap()


def text_on_img(filename='image.png', text="Hello", size=12):
    fnt = ImageFont.truetype('arial.ttf', size)
    image = Image.new(mode = "RGB", size = (int(size / 2) * len(text), size + 50), color = (54, 57, 63))
    draw = ImageDraw.Draw(image)
    draw.text((10, 10), text, font=fnt, fill=(255, 255, 0))
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
        if message.author.id != 822023355947155457:
            if done == False:
                try:
                    if datetime.now() <= time:
                        if message.content == answer:
                            await message.channel.send("That was right!")
                            done = True
                            winner = message.author
                            winnerid = message.author.id
                            answer = None
                    elif datetime.now() > time:
                        if message.content == answer:
                            print("too late!")
                            answer = None
                except:
                    pass
            elif message.content == answer:
                await message.channel.send("Sorry, it has already been answered")

    @commands.command()
    async def trivia(self, ctx):
        global time
        global answer
        global wrong
        global done
        global winner
        global winnerid
        delay = 20
        list = []
        URL = "https://trivia.willfry.co.uk/api/questions?categories=geography,general_knowledge,history,literature,music,science,society_and_culture&limit=1"
        r = requests.get(url = URL, timeout=2)
        t = r.json()
        wrong = t[0]["incorrectAnswers"]
        answer = t[0]["correctAnswer"].strip()
        question = t[0]["question"]
        time = datetime.now() + timedelta(seconds = delay)
        print(wrong)
        for x in wrong:
            list.append(x.strip())
        list.append(answer)
        print(list)
        random.shuffle(list)
        text_on_img(text=question, size=300)
        img = discord.File("image.png")
        e = discord.Embed()
        embed = discord.Embed(
            title=('\n'.join(list)), description="\u200b")
        file = discord.File("image.png")
        e.set_image(url="attachment://image.png")
        await ctx.send(file = file, embed=e)
        await ctx.send(embed=embed)
        await ctx.send(answer)
        await asyncio.sleep(10)
        if done == True:
            prize = random.randint(20, 30)
            if balfind(winnerid) + prize <= cap[money.rankfind(winnerid)]:
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
