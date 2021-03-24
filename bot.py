import os
import asyncio
import math
import random
import time
import better_profanity
import async_cse
import discord
import operator
import ast
import datetime
import urllib.parse
import requests
import wolframalpha
import platform
from async_timeout import timeout
from discord.ext import menus, commands
from translate import Translator
import botlib
import bottomlib
import money
from pprint import pprint
import cleverbotfree.cbfree

# python3 -m pip install discord.py asyncio async_cse googlesearch-python better-profanity translate simpleeval cleverbotfree wavelink
# this gets the directory this script is in. Makes it much easier to transfer between systems.
filepath = os.path.abspath(os.path.dirname(__file__))
# more bad words to limit searches, cos I really don't trust people. These are mostly just to stop people from getting me on CIA watchlists, as opposed to googling "boobies"
badsearch = ["isis", "taliban", "cp", "bomb", "ied", "explosive"]
f = open(f"{filepath}/config/token.txt")
# Gets the token from another text file so I don't have to leave the token in this file where anyone can read it
token = str(f.readline())
f.close()
null = None  # so I can write "null" instead of "None" and look like hackerman


client = discord.Client()
f = open(f"{filepath}/config/prefix.txt")
prefix = str(f.readline())  # Modular prefix
f.close()
client = commands.Bot(command_prefix=prefix)
canwelcome = False
client.remove_command('help')
starttime = null
appid = "APXP5R-JWJV4JW87W"
cb = cleverbotfree.cbfree.Cleverbot()


@client.event
async def on_ready():
    #os.system(f"start cmd /k java -jar {filepath}/Lavalink.jar")
    if platform.system() == "Windows":
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Testing"))
    else:
        activity = discord.Game(name="bottombot", type=3)
        status = random.choice(["ReCore's CPU catch fire", "the old gods die", "missiles fly",
                               "the CCCP commit horrific crimes", "bentosalad on twitch", "RealArdan on twitch"])
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status))
        client.load_extension("music")
    print("\u001b[35mThe bot is up\u001b[31m")
    f = open(f"{filepath}/logs.txt", "a")
    f.write(f"\n---\n{datetime.datetime.now()} Bot started\n---\n")
    f.close()
    client.load_extension("money")
    client.load_extension("cross")


@client.event
async def on_guild_join(guild):  # this is called when the bot joins a new server
    print(
        f"\u001b[35mJoined an new server! {guild.name} : {guild.id}\u001b[31m")
    # region Setup database
    # Makes a folder under "serversettings" named the server's id
    os.system(f'mkdir {filepath}/serversettings/{guild.id}')
    f = open("logs.txt", "a")
    # logging that a new server was joined
    f.write(
        f"{datetime.datetime.now()}: Joined an new server! {guild.name} : {guild.id}\n")
    f.close()
    # creates a file called replay.txt in the new directory we just nade. This file is used to store @mentions for the -rewind command
    os.system(f"touch {filepath}/serversettings/{guild.id}/replay.txt")
    # creates a file called serverdetail.txt in the same place as the replay.txt. This file is used to store stuff like the server name, id, owner and description.
    os.system(f"touch {filepath}/serversettings/{guild.id}/serverdetails.txt")
    f = open(f"{filepath}/serversettings/{guild.id}/serverdetails.txt", "a")
    f.write(f"Server name: {guild.name}\n")
    f.write(f"Server id: {guild.id}\n")
    f.write(f"Server owner: {guild.owner}\n")
    f.write(f"Server id: {guild.description}\n")
    # writes all those details to serverdetail.txt
    f.write(f"Joined at {datetime.datetime.now()}")
    f.close()
    print(
        f"\u001b[35mDatabase set up for server {guild.id} ({guild.name})\u001b[31m")
    f = open(f"{filepath}/logs.txt", "a")
    # logging that the database was set up properly
    f.write(
        f"{datetime.datetime.now()}: Database set up for server {guild.id} ({guild.name})\n")
    f.close()
    for channel in guild.text_channels:
        if canwelcome == True:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send('Heyo! I am bottombot, a cancerous mess. You can join my discord server here: https://discord.gg/2WaddNnuHh \nYou can also invite the bot to other servers with this link: https://discord.com/api/oauth2/authorize?client_id=758912539836547132&permissions=3324992&scope=bot \nUse -help to find out what commands I can use!')
            break
    # endregion


@client.command()
async def init(ctx):
    os.system(f'mkdir {filepath}/serversettings/{ctx.guild.id}')
    # creates a file called replay.txt in the new directory we just nade. This file is used to store @mentions for the -rewind command
    os.system(f"touch {filepath}/serversettings/{ctx.guild.id}/replay.txt")
    # creates a file called serverdetail.txt in the same place as the replay.txt. This file is used to store stuff like the server name, id, owner and description.
    os.system(
        f"touch {filepath}/serversettings/{ctx.guild.id}/serverdetails.txt")
    f = open(f"{filepath}/serversettings/{ctx.guild.id}/serverdetails.txt", "w")
    f.write("")
    f.close
    f = open(f"{filepath}/serversettings/{ctx.guild.id}/serverdetails.txt", "a")
    f.write(f"Server name: {ctx.guild.name}\n")
    f.write(f"Server id: {ctx.guild.id}\n")
    f.write(f"Server owner: {ctx.guild.owner}\n")
    f.write(f"Server desc: {ctx.guild.description}\n")
    # writes all those details to serverdetail.txt
    f.write(f"Init at {datetime.datetime.now()}")
    f.close()
    await ctx.send("Database setup!")


@client.event
async def on_member_join(member):
    role = discord.utils.get(member.server.roles, id=821166866348376116)
    if (member.id == 821161880734793738):
        await bot.add_roles(member, role)


@client.event
async def on_message(message):
    if '<@!' in message.content:
        try:
            os.system(f'mkdir serversettings/{message.guild.id}')
            # this makes the relevant folders for any servers that don't already have a serversettings entry.
            os.system(f"touch serversettings/{message.guild.id}/replay.txt")
            if message.author != client.user:
                pingC = message.content
                pingU = message.author
                f = open(
                    f"{filepath}/serversettings/{message.guild.id}/replay.txt", "a")
                f.write(f"\n'{pingC}' was sent by {pingU}")
                f.close()
        except:
            pass

    r = random.randint(0, 14)
    u = message.author.id
    if (r == 9) and (message.author.id != 758912539836547132):
        if money.balfind(u) != None:
            money.addmoney(u, random.randint(1, 5))
            print(f"\u001b[32m$1 was added to {message.author}\u001b[31m")
    # this breaks everything if removed. I don't advise it.
    await client.process_commands(message)


@client.command()
async def rewind(ctx, arg1):
    if arg1.isnumeric():
        with open(f"{filepath}/serversettings/{ctx.guild.id}/replay.txt", "r") as f:
            lines = f.read().splitlines()
            last_line = lines[int(arg1) * -1]
            print(f"\u001b[33;1mMention: {last_line} was called\u001b[31m")
            await ctx.send(last_line)
            f.close()
            f = open(f"{filepath}/logs.txt", "a")
            f.write(f"{datetime.datetime.now()} - {ctx.message.guild.name} | {ctx.message.author} : !rewind was called: result {arg1} was called with the result '{last_line}'\n")
            f.close()
    else:
        await ctx.send("I need a number stupid")


@client.event
async def on_guild_leave(guild):
    os.system(f"rmdir settings/{guild.id}")
    f = open(f"{filepath}/logs.txt", "a")
    f.write(f"{datetime.datetime.now()}: Left a server! {guild.name} : {guild.id}\n")
    print(f"Left a server! {guild.name} : {guild.id}\u001b[31m")
    # this removes all the database stuff for when the bot leaves a server, whether it is kicked or the server is deleted.
    f.close()


@client.command()
async def invite(ctx):
    await ctx.send("Server: https://discord.gg/2WaddNnuHh \nBot invite:  https://discord.com/api/oauth2/authorize?client_id=758912539836547132&permissions=3324992&scope=bot")


@client.command()
async def code(ctx):
    await ctx.send("Feel free to make commits and stuff.\nhttps://github.com/ReCore-sys/bottombot")


@client.command()
async def servers(ctx):
    await ctx.send(str(len(client.guilds)) + " servers have been infected!")


@client.command()
async def roll(ctx, arg1):
    if arg1.isnumeric():
        await ctx.send(random.randint(1, int(arg1)))
    else:
        await ctx.send("I need a number stupid")


@client.command()
async def moneyenabled(ctx):
    id = ctx.message.guild.id
    print(id)
    print(money.moneyenabled(id))

@client.command()
async def fox(ctx):
    await ctx.send(f"https://randomfox.ca/images/{random.randint(1,122)}.jpg")

@client.command()
async def pussy(ctx):
    while True:
        URL = "https://aws.random.cat/meow"
        r = requests.get(url = URL)
        t = r.json()
        if ".mp4" in t["file"]:
            pass
        else:
            break
    await ctx.send(t["file"])
@client.command()
async def dog(ctx):
    URL = "https://random.dog/woof.json"
    r = requests.get(url = URL)
    t = r.json()
    await ctx.send(t["url"])
@client.command()
async def xkcd(ctx):
    URL = f"https://xkcd.com/{random.randint(1,2400)}/info.0.json"
    r = requests.get(url = URL)
    t = r.json()
    await ctx.send(t["img"])

@client.command()
async def ru(ctx, *, args):
    if args != "uwu":
        tr1 = Translator(to_lang="ru")
        translation = tr1.translate(args)
        print(f"\u001b[33;1m{translation}\u001b[31m")
        await ctx.send(translation)
        f = open(f"{filepath}/logs.txt", "a")
        f.write(
            f"{datetime.datetime.now()} - {ctx.message.guild.name} | {ctx.message.author} : !ru {args} -> {translation}\n")
        f.close()

ttst = False


@client.command()
async def tts(ctx, *, args):
    global ttst
    if args == "on":
        ttst = True
    else:
        ttst = False
    await ctx.send(f"TTS set to {ttst}")


@client.command()
async def upgrade(ctx):
    if ctx.author.id == 451643725475479552:
        f = open(f"{filepath}/config/premium.txt", "a")
        f.write(str(ctx.guild.id))
        f.write("\n")
        f.close()
        await ctx.send("Server upgraded!")
    else:
        await ctx.send("Only ReCore can upgrade servers for now")
canbb = True


@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def bb(ctx, *, args):
    global ttst
    async with ctx.channel.typing():
        if canbb == False:
            await ctx.send("No, fuck off")
        else:
            ctx.message.channel.typing()
            if money.ranktoid(ctx.message.author.id) >= 2:
                if botlib.check_banned:
                    try:
                        cb.browser.get(cb.url)
                    except:
                        print("There was an error so we exited")
                        await ctx.send("Something isn't working right")
                        cb.browser.close()
                    try:
                        cb.get_form()
                    except:
                        print("There was an error so we exited")
                        await ctx.send("Something isn't working right")
                    userInput = args
                    cb.send_input(userInput)
                    bot = cb.get_response()
                    print(
                        f"\u001b[33;1m{datetime.datetime.now()} - {ctx.message.guild.name} | {ctx.message.author} : -bb: {args} -> {bot}\n\u001b[31m")
                    f = open(f"{filepath}/logs.txt", "a")
                    f.write(
                        f"{datetime.datetime.now()} - {ctx.message.guild.name} | {ctx.message.author} : -bb: {args} -> {bot}\n")
                    f.close()
                    await ctx.send(bot)
                else:
                    # there are a few people banned from using this command. These are their ids
                    await ctx.send(botlib.nope)
            else:
                await ctx.send("Sorry, you don't have" + ' a high enough rank. You will need to buy silver. Use "-rank" to see the price')


@client.command()
async def maths(ctx, *, args):
    global ttst
    global s
    global appid
    fargs = args.replace('-steps', '')
    if botlib.check_banned(ctx):
        try:
            equation = fargs
            query = urllib.parse.quote_plus(f"solve {equation}")
            query_url = f"https://api.wolframalpha.com/v2/query?" \
                        f"appid={appid}" \
                        f"&input={query}" \
                        f"&scanner=Solve" \
                        f"&podstate=Result__Step-by-step+solution" \
                        "&format=plaintext" \
                        f"&output=json"

            r = requests.get(query_url).json()

            data = r["queryresult"]["pods"][0]["subpods"]
            result = data[0]["plaintext"]
            steps = data[1]["plaintext"]

            await ctx.send(f"**Result of {equation} is '{result}'.**\n")
            if "-steps" in args:
                await ctx.send(f"Possible steps to solution:\n\n{steps}")
        except:
            await ctx.send("That didn't work. Not sure why. Probably some 'Key Error: pods' BS.")
    else:
        await ctx.send(botlib.nope)


@client.command()
async def ping(ctx):
    time_1 = time.perf_counter()
    await ctx.trigger_typing()
    time_2 = time.perf_counter()
    ping = round((time_2 - time_1) * 1000)
    embed = discord.Embed(
        title="Pong!", description=f"Currant Latancy = {ping}. Lol u got slow internet")
    await ctx.send(embed=embed)
    print("\u001b[33;1mDone: ping = " + str(ping))


@client.command()
async def info(ctx):
    embed = discord.Embed(
        title="Bottombot", description="If it works let me know. I'd be pretty suprised.", color=0x8800ff)
    embed.add_field(name="Creator", value="<@451643725475479552>", inline=True)
    embed.add_field(
        name="Reason", value="I was bored and want to make a bot", inline=False)
    embed.add_field(name="Functionality?", value="no", inline=False)
    embed.add_field(
        name="Made with", value="Love, care, ages on stackoverflow.com, bugging <@416101701574197270> and copious amounts of cocaine.", inline=False)
    print("\u001b[33;1mDone: -info\u001b[31m")

    await ctx.send(embed=embed)


@client.command()
async def cease(ctx):
    if ctx.message.author.id == 451643725475479552:
        cb.browser.close()
        exit()
    else:
        # command to turn off the bot. Only I can use it.
        await ctx.send("Lol nah")


@client.command()
async def reboot(ctx):
    if ctx.message.author.id == 451643725475479552:
        print("\u001b[0mRebooting \u001b[0m")
        os.system(f"python {filepath}/bot.py")
        cb.browser.close()
        # os.kill("java.exe")
        # os.kill("cmd.exe")
        exit()
    else:
        # command to reboot the bot. Only I can use it.
        await ctx.send("Lol nah")

pingC = None
pingU = None


@client.command()
async def trans(ctx):
    await ctx.send(":transgender_flag: Trans rights are human rights :transgender_flag: ")


@client.command()
async def game(ctx, args):
    query = urllib.parse.quote(args)
    await ctx.send(f"https://www.g2a.com/search?query={query}")


@client.command()
async def bucketlist(ctx):
    list = random.choice(["willful killing, torture or inhumane treatment, including biological experiments", "willfully causing great suffering or serious injury to body or health", "compelling a protected person to serve in the armed forces of a hostile power",
                         "willfully depriving a protected person of the right to a fair trial if accused of a war crime.", "taking of hostages", "extensive destruction and appropriation of property not justified by military necessity and carried out unlawfully and wantonly", "unlawful deportation, transfer, or confinement."])
    await ctx.send(list)


@client.command()
async def cf(ctx):
    await ctx.send(random.choice(["Heads", "Tails"]))

"""@client.command()
async def updates(ctx, remove = False):
    if remove == False:
        channel = ctx.message.channel.id
        f = open(f"{filepath}/config/updaters.txt", "r")
        servers = list(f.read())
        f.close()
        servers.append[channel]
        f = open(f"{filepath}/config/updaters.txt", "w")
        f.write(servers)
        f.close()
        await ctx.send("Ok, added you to the list of servers to recieve updates")
    elif remove == "remove":
        channel = ctx.message.channel.id
        f = open(f"{filepath}/config/updaters.txt", "r")
        servers = f.read()
        f.close()
        servers.remove[channel]
        f = open(f"{filepath}/config/updaters.txt", "w")
        f.write(servers)
        f.close()
        await ctx.send("Ok, removed you from the list of servers to recieve updates")

@client.command()
async def update(ctx, *, args):
    if ctx.message.author.id == 451643725475479552:
        f = open(f"{filepath}/config/updaters.txt", "r")
        servers = f.read()
        f.close()
        for x in servers:
            address = client.get_channel(int(x))
            await address.send(args)"""

@client.command()
async def search(ctx, *, args):
    isbad2 = better_profanity.profanity.contains_profanity(args)
    if money.ranktoid(ctx.message.author.id) >= 3:

        if ((isbad2 == True) or (args in badsearch)):
            badresponse = random.choice(["This is why your parents don't love you", "Really?",
                                        "You are just an asshole. You know that?", "God has abandoned us", "Horny bastard"])
            await ctx.send(badresponse)
            print(
                f"\u001b[33;1m{ctx.message.author} tried to search '{args}'\u001b[31m")

        elif (args.find("urbandictionary") == True):
            await ctx.send("Lol no")

        elif "://" in args:
            await ctx.send("You think I'm stupid? Don't answer that.")

        if botlib.check_banned(ctx):
            # create the Search client (uses Google by default-)
            client = async_cse.Search(
                "AIzaSyAIc3NVCXoMDUzvY4sTr7hPyRQREdPUVg4")
            # returns a list of async_cse.Result objects
            results = await client.search(args, safesearch=True)
            first_result = results[0]  # Grab the first result
            if "urbandictionary" in first_result.url:
                await ctx.send("Thanks to <@567522840752947210>, urban dictionary is banned")
            else:
                await ctx.send(f"**{first_result.title}**\n{first_result.url}")
                await client.close()
                f = open(f"{filepath}/logs.txt", "a")
                f.write(
                    f"{datetime.datetime.now()} - {ctx.message.guild.name} | {ctx.message.author} : !search {args} -> {first_result.url}\n")
                f.close()
        else:
            await ctx.send(botlib.nope)
    else:
        await ctx.send("You don't have a high enough rank for this")


@client.command()
async def image(ctx, *, args):
    isbad2 = better_profanity.profanity.contains_profanity(args)
    if money.ranktoid(ctx.message.author.id) >= 3:

        if ((isbad2 == True) or (args in badsearch)):
            badresponse = random.choice(["This is why your parents don't love you", "Really?",
                                        "You are just an asshole. You know that?", "God has abandoned us", "Horny bastard"])
            await ctx.send(badresponse)
            print(
                f"\u001b[33;1m{ctx.message.author} tried to search '{args}'\u001b[31m")

        elif botlib.check_banned(ctx):
            # create the Search client (uses Google by default-)
            client = async_cse.Search(
                "AIzaSyAIc3NVCXoMDUzvY4sTr7hPyRQREdPUVg4")
            # returns a list of async_cse.Result objects
            results = await client.search(args, safesearch=True)
            first_result = results[0]  # Grab the first result
            if "urbandictionary" in first_result.image_url:
                await ctx.send("Thanks to <@567522840752947210>, urban dictionary is banned")
            else:
                await ctx.send(f"{first_result.image_url}")
                await client.close()
                f = open(f"{filepath}/logs.txt", "a")
                f.write(
                    f"{datetime.datetime.now()} - {ctx.message.guild.name} | {ctx.message.author} : -search {args} -> {first_result.image_url}\n")
                f.close()

        else:
            await ctx.send(botlib.nope)
    else:
        await ctx.send("You don't have a high enough rank for this")


@client.command()
async def duck(ctx):
    await ctx.send("https://coorongcountry.com.au/wp-content/uploads/2016/01/Pacific-Black-Duck-53-cm.png")


@client.command()
async def bottomgear(ctx):
    global ttst
    output = bottomlib.bottomchoice()
    await ctx.send(output, tts=ttst)
    print("\u001b[33;1mDone: -bottomgear\u001b[31m")
    f = open(f"{filepath}/logs.txt", "a")
    f.write(f"{datetime.datetime.now()} - {ctx.message.guild.name} | {ctx.message.author} : -bottomgear {output}\n")
    f.close()


@client.command()
async def help(ctx, menu=None):
    if menu == "music":
        await ctx.send("""```-connect : Connect to a voice channel.
-play <song name> : Play or queue a song with the given query.
-pause : Pause the currently playing song.
-resume : Resume the currently paused song.
-skip : Skip the currently playing song.
-stop : Stop and reset the music player.
-volume / -vol / -v <1-100> : Change the music player's volume, between 1 and 100.
-shuffle / -mix : Shuffle the music player's queue.
-queue / -que / -q : Display's the music player's queued songs.
-nowplaying / now_playing / current / np : Show the currently playing song.
-swap_dj / -swap <user> : Swap the current DJ to another member in the voice channel.
-equaliser : music filters that are still under dev```""")
    elif menu == "cross":
        await ctx.send("```-join : Adds you to the waiting list of servers wanting to chat. Also sets the current channel as the conversation channel.\n-leave : If you are in the waiting list, it will remove you from it. If you are currently connected to another server it will disconnect you.```\nOnce you are connected to another server any message in the set channel that does not contain - or _ will be sent to the other server. You can still use commands without transmitting the results. Usernames are sent across but not the server name.")
    elif menu == "money":
        await ctx.send("```-account / -a / -bal / -balance [user]: Shows the bank account of the pinged user. If none pinged will show your own. \n-pay <amount> <user> : pays <amount> from your bank account into <user>. \n-rank [buy] <rank> : used to buy ranks. If none selected will show the price of the ranks. \n-daily : earns you between $20 and $50. Has a 24 hour cooldown.\n-stocks / -stock / -stonks [buy/sell] <number to buy/sell or 'all'> : running without args shows the current stock price. Selling or buying's cost is dependant on the current price of stocks\neconomy <on/off> : Turns the economy functions off for the server. No data is lost so you can turn it back on later without losing anyhting. Admin only.```\n**You will need to run -account to set up your account before doing anything else**")
    else:
        await ctx.send("""**For all listed commands, [] means optional, <> means required.**\n```-bottomgear : Prints out a randomly generated bottomgear meme. Probably NSFW.
-search <query> : Does a google search for something. Needs rank Gold or above to use.
-image <image> : Does a google image search for something. Needs rank Gold or above to use.
-cf : does a coin flip
-ru <words> : will translate something into russian
-info : prints info about the bot
-bb <sentence> : calls the AI chatbot to respond to what you said. Is very buggy and slow. Please don't spam it. If it is too slow, feel free to donate $5 to speed it up. You also need rank silver or above for it.
-rewind <number of mentions to go back>: Prints the most recent mention of anyone in the server and what was said.
-duck : duck
-bucketlist : prints a to-do list
-trans : prints out the bot's opinion on trans people
-ping : works out the bot's ping
-invite : gets a link for the server and an invite link for the bot
-servers : Shows how many servers the bot is in
-code : gets the link for the github so you can see what goes on under the hood
-init : Sets up the database for the server. It's a good idea to run this whenever the owner or name changes. Also run this if you have not seen this command before.
-pussy: gets an image of some sweet pussy
-fox : Foxes are hella cute
-dog : Dog
```
Do -help music for help with music commands
Do -help cross for help with cross server chat
Do -help money for help with economy commands (Still in Beta)""")


client.run(token)

# To do
# Editable prefixes
# Maybe premium commands you need to pay for?
