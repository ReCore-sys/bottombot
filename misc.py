import datetime
import json
import os
import platform
import random
import time

import cpuinfo
import discord
import humanfriendly
import openai
import psutil
import requests
from discord.ext import commands

import botlib
import bottomlib
import secret_data
import settings
import sqlbullshit
import utils

filepath = os.path.abspath(os.path.dirname(__file__))

sql = sqlbullshit.sql(filepath + "/data.db", "user")
openai.api_key = secret_data.openaikey

starttime = time.time()


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def rewind(self, ctx, val=1):
        if str(val).isnumeric():
            with open(f"{filepath}/serversettings/{ctx.guild.id}/replay.txt", "r") as f:
                lines = f.read().splitlines()
                last_line = lines[int(val) * -1]
                print(f"Mention: {last_line} was called")
                await ctx.send(last_line)
                f.close()
                f = open(f"{filepath}/logs.txt", "a")
                f.write(f"{datetime.datetime.now()} - {ctx.message.guild.name} | {ctx.message.author} : !rewind was called: result {val} was called with the result '{last_line}'\n")
                f.close()
        else:
            await ctx.send("I need a number stupid")

    @commands.Cog.listener()
    async def on_guild_leave(self, guild):
        os.system(f"rmdir settings/{guild.id}")
        f = open(f"{filepath}/logs.txt", "a")
        f.write(
            f"{datetime.datetime.now()}: Left a server! {guild.name} : {guild.id}\n")
        print(f"Left a server! {guild.name} : {guild.id}")
        # this removes all the database stuff for when the bot leaves a server, whether it is kicked or the server is deleted.
        f.close()

    @commands.command()
    async def invite(self, ctx):
        await ctx.send("Server: https://discord.gg/2WaddNnuHh \nBot invite:  https://discord.com/api/oauth2/authorize?commands_id=758912539836547132&permissions=8&scope=bot")

    @commands.command()
    async def code(self, ctx):
        await ctx.send("Feel free to make commits and stuff.\nhttps://github.com/ReCore-sys/bottombot")

    @commands.command()
    async def servers(self, ctx):
        await ctx.send(len(commands.guilds) + " servers have been infected!")

    @commands.command()
    async def roll(self, ctx, arg1):
        if arg1.isnumeric():
            await ctx.send(random.randint(1, int(arg1)))
        else:
            await ctx.send("I need a number stupid")

    @commands.command()
    async def fox(self, ctx):
        await ctx.send(f"https://randomfox.ca/images/{random.randint(1,122)}.jpg")

    @commands.command()
    async def pussy(self, ctx):
        while True:
            URL = "https://aws.random.cat/meow"
            r = requests.get(url=URL)
            t = r.json()
            if ".mp4" in t["file"]:
                pass
            else:
                break
        await ctx.send(t["file"])

    @commands.command()
    async def dog(self, ctx):
        URL = "https://random.dog/woof.json"
        r = requests.get(url=URL)
        t = r.json()
        await ctx.send(t["url"])

    @commands.command()
    async def xkcd(self, ctx):
        URL = f"https://xkcd.com/{random.randint(1,2400)}/info.0.json"
        r = requests.get(url=URL)
        t = r.json()
        await ctx.send(t["img"])

    ttst = False

    @commands.command()
    async def tts(self, ctx, val=None):
        global ttst
        if val != None:
            if val == "on":
                ttst = True
            else:
                ttst = False
            await ctx.send(f"TTS set to {ttst}")
        else:
            await ctx.send("You need to give me input")

    @commands.command()
    @commands.cooldown(5, 25, commands.BucketType.guild)
    async def bb(self, ctx, *, args):
        if settings.check(ctx.message.guild.id, "get", "bb"):

            if botlib.check_banned(ctx):
                async with ctx.channel.typing():
                    tokens = len(args) / 4
                    if tokens >= 75:
                        await ctx.send("Sorry, that input was too big. Please try something smaller")
                        return
                    if sql.doesexist(ctx.author.id) == False:
                        await ctx.send("You don't have an economy account yet. Please make one with -bal")
                        return
                    if sql.get(ctx.author.id, "money") < 3:
                        await ctx.send("Sorry, you need more money to use the bot")
                    else:
                        sql.take(3, ctx.author.id, "money")
                        ctx.message.channel.typing()
                        with open(filepath + "/convfile.txt") as f:
                            response = openai.Completion.create(
                                engine="curie",
                                prompt=(f.read()).format(
                                    args),
                                temperature=0.9,
                                max_tokens=100,
                                top_p=1,
                                frequency_penalty=0,
                                presence_penalty=0.6,
                                stop=[" Human:", " AI:", "\n"]

                            )
                        bot = response.choices[0].text
                        print(
                            f"{datetime.datetime.now()} - {ctx.message.guild.name} | {ctx.message.author} : -bb: {args} -> {bot}\n")
                        f = open(f"{filepath}/logs.txt", "a")
                        f.write(
                            f"{datetime.datetime.now()} - {ctx.message.guild.name} | {ctx.message.author} : -bb: {args} -> {bot}\n")
                        f.close()
                        await ctx.reply(bot)
            else:
                # there are a few people banned from using this command. These are their ids
                await ctx.reply(botlib.nope())
        else:
            await ctx.send("Sorry, the chatbot is disabled for this server")

    @bb.error
    async def bb(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"AI is on a cooldown. Try again in {round(error.retry_after, 1)} seconds"
            )

    @ commands.command()
    async def ping(self, ctx):
        time_1 = time.perf_counter()
        await ctx.trigger_typing()
        time_2 = time.perf_counter()
        ping = round((time_2 - time_1) * 1000)
        embed = discord.Embed(
            title="Pong!", description=f"Currant Latancy = {ping}. Lol u got slow internet")
        await ctx.send(embed=embed)
        print("Done: ping = " + str(ping))

    @ commands.command()
    async def info(self, ctx):
        embed = discord.Embed(
            title="Bottombot", description="If it works let me know. I'd be pretty suprised.", color=0x8800ff)
        embed.add_field(name="Creator",
                        value="<@451643725475479552>", inline=True)
        embed.add_field(
            name="Reason", value="I was bored and want to make a bot", inline=False)
        embed.add_field(name="Functionality?", value="no", inline=False)
        embed.add_field(
            name="Made with", value="Love, care, ages on stackoverflow.com, bugging <@416101701574197270> and copious amounts of cocaine.", inline=False)
        print("")

        await ctx.send(embed=embed)

    @ commands.command()
    async def cease(self, ctx):
        if ctx.message.author.id == 451643725475479552:
            exit()
        else:
            # command to turn off the bot. Only I can use it.
            await ctx.send("Lol nah")

    @ commands.command()
    async def reboot(self, ctx):
        if ctx.message.author.id == 451643725475479552:
            print("Rebooting ")
            os.system(f"python {filepath}/bot.py")
            # os.kill("java.exe")
            # os.kill("cmd.exe")
            exit()
        else:
            # command to reboot the bot. Only I can use it.
            await ctx.send("Lol nah")

    pingC = None
    pingU = None

    @ commands.command()
    async def trans(self, ctx):
        await ctx.send(":transgender_flag: Trans rights are human rights :transgender_flag: ")

    @ commands.command()
    async def cf(self, ctx):
        await ctx.send(random.choice(["Heads", "Tails"]))

    @commands.command()
    async def updates(self, ctx, remove=False):
        channel = ctx.message.channel.id
        with open(filepath + "/json/configs.json", "r") as f:
            j = json.load(f)
            channels = j["updates"]
            if channel in channels:
                await ctx.send("Ok, removed this channel from the list to recieve updates")
                channels.remove(channel)
            else:
                await ctx.send("Ok, added this channel to the list to recieve updates")
                channels.append(channel)
            j["updates"] = channels
        with open(filepath + "/json/configs.json", "w") as f:
            json.dump(j, f)

    @commands.command()
    async def update(self, ctx, *, args):
        if ctx.message.author.id == 451643725475479552:
            with open(filepath + "/json/configs.json", "r") as f:
                servers = json.load(f)
                for x in servers["updates"]:
                    address = commands.get_channel(int(x))
                    await address.send("**ANNOUNCMENT**")
                    await address.send(args)
                    time.sleep(0.5)

    @ commands.command()
    async def duck(self, ctx):
        await ctx.send("https://coorongcountry.com.au/wp-content/uploads/2016/01/Pacific-Black-Duck-53-cm.png")

    @ commands.command()
    async def bottomgear(self, ctx):
        global ttst
        output = bottomlib.bottomchoice()
        await ctx.send(output, tts=ttst)
        print("Done: -bottomgear")
        f = open(f"{filepath}/logs.txt", "a")
        f.write(
            f"{datetime.datetime.now()} - {ctx.message.guild.name} | {ctx.message.author} : -bottomgear {output}\n")
        f.close()

    @ commands.command()
    async def help(self, ctx, menu=None):
        result = json.load(open(f"{filepath}/json/help.json"))
        result2 = {}
        for x in result:
            list = []
            for v in result[x]:
                result2[v] = result[x][v]
        if menu not in result2:
            embed = discord.Embed(
                title="Help", description="Welcome to the help menu. Do -help <command> to see what an individual command does", color=0x1e00ff)
            for x in result:
                list = []
                for v in result[x]:
                    list.append(v)
                nicelist = (', '.join(list))
                embed.add_field(name=x, value=f"`{nicelist}`", inline=True)

            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title=menu, description=result2[menu], color=0x1e00ff)
            await ctx.send(embed=embed)

    @commands.command()
    async def stats(self, ctx):
        uname = platform.uname()
        cputype = cpuinfo.get_cpu_info()['brand_raw']
        osversion = uname.version
        ostype = uname.system
        uptime = time.time() - starttime
        cores = psutil.cpu_count(logical=True)
        cpuuse = psutil.cpu_percent()
        svmem = psutil.virtual_memory()
        mem = utils.convert_bytes(svmem.total)
        used = utils.convert_bytes(svmem.used)
        percent = svmem.percent
        partition = psutil.disk_partitions()[0]
        partition_usage = psutil.disk_usage(partition.mountpoint)
        disk_total = utils.convert_bytes(partition_usage.total)
        disk_used = utils.convert_bytes(partition_usage.used)
        disk_percent = partition_usage.percent
        embed = discord.Embed(
            title="Stats", description="System stats", color=0x1e00ff)
        embed.add_field(
            name="Uptime", value=f"{humanfriendly.format_timespan(uptime)}", inline=False)
        embed.add_field(name="CPU", value=f"{cputype}", inline=False)
        embed.add_field(name="CPU Usage", value=f"{cpuuse}%", inline=False)
        embed.add_field(
            name="OS", value=f"{ostype} ({osversion})", inline=False)
        embed.add_field(name="Memory", value=f"{mem}", inline=False)
        embed.add_field(
            name="Used", value=f"{used} ({percent}%)", inline=False)
        embed.add_field(name="Disk Total", value=f"{disk_total}", inline=False)
        embed.add_field(name="Disk Used",
                        value=f"{disk_used} ({disk_percent}%)", inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Misc(bot))
