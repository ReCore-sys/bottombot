import os
import asyncio
import math
import random
import time
import googlesearch
from googlesearch import search
import async_cse
import discord
from async_timeout import timeout
from discord.ext import commands
from discord.ext import menus
import better_profanity
from translate import Translator
#from chatterbot import ChatBot
#from chatterbot.trainers import ListTrainer
from simpleeval import simple_eval
import operator
import ast
import datetime
import botlib, bottomlib
import urllib.parse

#python3 -m pip install discord.py asyncio async_cse googlesearch-python better-profanity translate simpleeval
filepath = os.path.abspath(os.path.dirname(__file__)) #this gets the directory this script is in. Makes it much easier to transfer between systems.
badsearch = ["isis","taliban","cp","bomb","ied","explosive"] #more bad words to limit searches, cos I really don't trust people. These are mostly just to stop people from getting me on CIA watchlists, as opposed to googling "boobies"
f = open(f"{filepath}/config/token.txt")
token = str(f.readline()) #Gets the token from another text file so I don't have to leave the token in this file where anyone can read it
f.close()
null = None #so I can write "null" instead of "None" and look like hackerman
"""
#Chatterbot stuff

chatbot = ChatBot('Bottombot')

trainer = ListTrainer(chatbot)

trainer.export_for_training(f'{filepath}/my_export.json') #exporting the saved training data

trainer.train([
    "UwU" #It starts with one word. I chose this
])
#Chatterbot stuff
"""

client = discord.Client()

client = commands.Bot(command_prefix = "-")

client.remove_command('help')
starttime = null


@client.event
async def on_ready():
    #os.system(f"start cmd /k java -jar {filepath}/Lavalink.jar")
    activity = discord.Game(name="bottombot", type=3)
    status = random.choice(["ReCore's CPU catch fire","the old gods die","missiles fly","the CCCP commit horrific crimes","bentosalad on twitch","RealArdan on twitch"])
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status))
    print("\u001b[35mThe bot is up\u001b[31m")
    channel = client.get_channel(806378599065190412) #informns two channels that the bot is up
    await channel.send('Bot is up')
    channel = client.get_channel(812145603848568852)
    await channel.send('Bot is up')
    f = open(f"{filepath}/logs.txt", "a")
    f.write(f"\n---\n{datetime.datetime.now()} Bot started\n---\n")
    f.close()
    client.load_extension("music")

@client.event
async def on_guild_join(guild): #this is called when the bot joins a new server
    print(f"\u001b[35mJoined an new server! {guild.name} : {guild.id}\u001b[31m")
    #region Setup database
    os.system(f'mkdir {filepath}/serversettings/{guild.id}') #Makes a folder under "serversettings" named the server's id
    f = open("logs.txt", "a")
    f.write(f"{datetime.datetime.now()}: Joined an new server! {guild.name} : {guild.id}\n") #logging that a new server was joined
    f.close()
    os.system(f"touch {filepath}/serversettings/{guild.id}/replay.txt") #creates a file called replay.txt in the new directory we just nade. This file is used to store @mentions for the -rewind command
    os.system(f"touch {filepath}/serversettings/{guild.id}/serverdetails.txt") #creates a file called serverdetail.txt in the same place as the replay.txt. This file is used to store stuff like the server name, id, owner and description.
    f = open(f"{filepath}/serversettings/{guild.id}/serverdetails.txt", "a")
    f.write(f"Server name: {guild.name}\n")
    f.write(f"Server id: {guild.id}\n")
    f.write(f"Server owner: {guild.owner}\n")
    f.write(f"Server id: {guild.description}\n")
    f.write(f"Joined at {datetime.datetime.now()}") #writes all those details to serverdetail.txt
    f.close()
    print(f"\u001b[35mDatabase set up for server {guild.id} ({guild.name})\u001b[31m")
    f = open(f"{filepath}/logs.txt", "a")
    f.write(f"{datetime.datetime.now()}: Database set up for server {guild.id} ({guild.name})\n") #logging that the database was set up properly
    f.close()
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send('Heyo! I am bottombot, a cancerous mess. You can join my discord server here: https://discord.gg/2WaddNnuHh \nYou can also invite the bot to other servers with this link: https://discord.com/api/oauth2/authorize?client_id=758912539836547132&permissions=3324992&scope=bot \nUse !help to find out what commands I can use!')
        break
    #endregion
@client.command()
async def init(ctx):
    os.system(f'mkdir {filepath}/serversettings/{ctx.guild.id}')
    os.system(f"touch {filepath}/serversettings/{ctx.guild.id}/replay.txt") #creates a file called replay.txt in the new directory we just nade. This file is used to store @mentions for the -rewind command
    os.system(f"touch {filepath}/serversettings/{ctx.guild.id}/serverdetails.txt") #creates a file called serverdetail.txt in the same place as the replay.txt. This file is used to store stuff like the server name, id, owner and description.
    f = open(f"{filepath}/serversettings/{ctx.guild.id}/serverdetails.txt", "w")
    f.write("")
    f.close
    f = open(f"{filepath}/serversettings/{ctx.guild.id}/serverdetails.txt", "a")
    f.write(f"Server name: {ctx.guild.name}\n")
    f.write(f"Server id: {ctx.guild.id}\n")
    f.write(f"Server owner: {ctx.guild.owner}\n")
    f.write(f"Server desc: {ctx.guild.description}\n")
    f.write(f"Init at {datetime.datetime.now()}") #writes all those details to serverdetail.txt
    f.close()

@client.event
async def on_message(message):
    if '<@!' in message.content:
            os.system(f'mkdir serversettings/{message.guild.id}')
            os.system(f"touch serversettings/{message.guild.id}/replay.txt")#this makes the relevant folders for any servers that don't already have a serversettings entry.
            if message.author != client.user:
                    pingC = message.content
                    pingU = message.author
                    f = open(f"{filepath}/serversettings/{message.guild.id}/replay.txt", "a")
                    f.write(f"\n'{pingC}' was sent by {pingU}")
                    f.close()
        
    await client.process_commands(message) #this breaks everything if removed. I don't advise it.

@client.command()
async def rewind(ctx, arg1):
    if arg1.isnumeric():
        try:
            with open(f"{filepath}/serversettings/{ctx.guild.id}/replay.txt", "r") as f:
                lines = f.read().splitlines()
                last_line = lines[int(arg1) * -1]
                print(f"\u001b[33;1mMention: {last_line} was called\u001b[31m")
                await ctx.send(last_line)
                f.close()
                f = open(f"{filepath}/logs.txt", "a")
                f.write(f"{datetime.datetime.now()} - {ctx.message.guild.name} | {ctx.message.author} : !rewind was called: result {arg1} was called with the result '{last_line}'\n")
                f.close()
        except FileNotFoundError:
            await ctx.send("No @ mentions have been sent in this server. Please report this if it is an error")
    else:
        await ctx.send("I need a number stupid")

@client.event
async def on_guild_leave(guild):
    os.system(f"rmdir settings/{guild.id}")
    f = open(f"{filepath}/logs.txt", "a")
    f.write(f"{datetime.datetime.now()}: Left a server! {guild.name} : {guild.id}\n")
    print(f"Left a server! {guild.name} : {guild.id}\u001b[31m")
    f.close() #this removes all the database stuff for when the bot leaves a server, whether it is kicked or the server is deleted.

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
async def ru(ctx, *, args):
    if args != "uwu":
        tr1= Translator(to_lang="ru")
        translation = tr1.translate(args)
        print(f"\u001b[33;1m{translation}\u001b[31m")
        await ctx.send(translation)
        f = open(f"{filepath}/logs.txt", "a")
        f.write(f"{datetime.datetime.now()} - {ctx.message.guild.name} | {ctx.message.author} : !ru {args} -> {translation}\n")
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
"""
canbb = True
@client.command()
async def bb(ctx, *, args):
    global ttst
    if botlib.premium(ctx):
        if botlib.check_banned:
            await ctx.trigger_typing()
            response = chatbot.get_response(args)
            print(f"\u001b[33;1m{ctx.message.guild.name} | {ctx.message.author}: {args} -> {response}\u001b[31m")
            await ctx.send(response, tts=ttst)
            f = open(f"{filepath}/logs.txt", "a")
            f.write(f"{datetime.datetime.now()} - {ctx.message.guild.name} | {ctx.message.author} : !bb {args} -> {response}\n")
            f.close()
        else:
            await ctx.send(botlib.nope)#there are a few people banned from using this command. These are their ids
    else:
        await ctx.send("Sorry, you don't have premium\nContact <@!451643725475479552> in the bot's server to upgrade your server")
"""
@client.command()
async def maths(ctx, *, args):
    global ttst
    global s
    try:
        if botlib.check_banned(ctx):
            await ctx.trigger_typing()
            response = simple_eval(args.replace("^", "**"), functions={"sqrt": lambda x: math.sqrt(x)})
            print(f"\u001b[33;1m{ctx.message.guild.name} | {ctx.message.author}: {args} -> {response}\u001b[31m")
            await ctx.send(response, tts=ttst)
            f = open(f"{filepath}/logs.txt", "a")
            f.write(f"{datetime.datetime.now()} - {ctx.message.guild.name} | {ctx.message.author} : !bb {args} -> {response}\n")
            f.close()
        else:
            await ctx.send(botlib.nope)
    except NumberTooHigh:
        await ctx.send("Result was too high")

@client.command()
async def ping(ctx):
    time_1 = time.perf_counter()
    await ctx.trigger_typing()
    time_2 = time.perf_counter()
    ping = round((time_2-time_1)*1000)
    embed = discord.Embed(title="Pong!", description=f"Currant Latancy = {ping}. Lol u got slow internet")
    await ctx.send(embed=embed)
    print ("\u001b[33;1mDone: ping = " + ping)

@client.command()
async def info(ctx):
    embed = discord.Embed(title="Bottombot", description="If it works let me know. I'd be pretty suprised.", color=0x8800ff)

    embed.add_field(name="Creator", value="<@451643725475479552>", inline=True)
    embed.add_field(name="Reason", value="I was bored and want to make a bot", inline=False)
    embed.add_field(name="Functionality?", value="no", inline=False)
    embed.add_field(name="Made with", value="Love, care, ages on stackoverflow.com, bugging <@416101701574197270> and copious amounts of cocaine.", inline=False)
    print("\u001b[33;1mDone: !info\u001b[31m")

    await ctx.send(embed=embed)


@client.command()
async def cease(ctx):
    if ctx.message.author.id == 451643725475479552:
        os.kill("java.exe")
        exit()
    else:
        await ctx.send("Lol nah") #command to turn off the bot. Only I can use it.

@client.command()
async def reboot(ctx):
    if ctx.message.author.id == 451643725475479552:
        print("\u001b[0mRebooting \u001b[0m")
        os.system(f"python {filepath}/bot.py")
        #os.kill("java.exe")
        #os.kill("cmd.exe")
        exit()
    else:
        await ctx.send("Lol nah") #command to reboot the bot. Only I can use it.

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
    list = random.choice(["willful killing, torture or inhumane treatment, including biological experiments", "willfully causing great suffering or serious injury to body or health", "compelling a protected person to serve in the armed forces of a hostile power", "willfully depriving a protected person of the right to a fair trial if accused of a war crime.", "taking of hostages", "extensive destruction and appropriation of property not justified by military necessity and carried out unlawfully and wantonly", "unlawful deportation, transfer, or confinement."])
    await ctx.send(list)



@client.command()
async def cf(ctx):
    await ctx.send(random.choice(["Heads","Tails"]))

@client.command()
async def search(ctx, *, args):
    isbad2 = better_profanity.profanity.contains_profanity(args)

    if ((isbad2 == True) or (args in badsearch)):
            badresponse = random.choice(["This is why your parents don't love you","Really?","You are just an asshole. You know that?","God has abandoned us","Horny bastard"])
            await ctx.send(badresponse)
            print(f"\u001b[33;1m{ctx.message.author} tried to search '{args}'\u001b[31m")


    elif (args.find("urbandictionary") == True):
        await ctx.send("Lol no")

    elif "://" in args:
        await ctx.send("You think I'm stupid? Don't answer that.")

    if botlib.check_banned(ctx):
        client = async_cse.Search("AIzaSyAIc3NVCXoMDUzvY4sTr7hPyRQREdPUVg4") # create the Search client (uses Google by default!)
        results = await client.search(args, safesearch=True) # returns a list of async_cse.Result objects
        first_result = results[0] # Grab the first result
        if "urbandictionary" in first_result.url:
            await ctx.send("Thanks to <@567522840752947210>, urban dictionary is banned")
        else:
            await ctx.send(f"**{first_result.title}**\n{first_result.url}")
            await client.close()
            f = open(f"{filepath}/logs.txt", "a")
            f.write(f"{datetime.datetime.now()} - {ctx.message.guild.name} | {ctx.message.author} : !search {args} -> {first_result.url}\n")
            f.close()
    else :
        await ctx.send(botlib.nope)
@client.command()
async def image(ctx,*,args):
    isbad2 = better_profanity.profanity.contains_profanity(args)

    if ((isbad2 == True) or (args in badsearch)):
            badresponse = random.choice(["This is why your parents don't love you","Really?","You are just an asshole. You know that?","God has abandoned us","Horny bastard"])
            await ctx.send(badresponse)
            print(f"\u001b[33;1m{ctx.message.author} tried to search '{args}'\u001b[31m")

    elif botlib.check_banned(ctx):
        client = async_cse.Search("AIzaSyAIc3NVCXoMDUzvY4sTr7hPyRQREdPUVg4") # create the Search client (uses Google by default!)
        results = await client.search(args, safesearch=True) # returns a list of async_cse.Result objects
        first_result = results[0] # Grab the first result
        if "urbandictionary" in first_result.image_url:
            await ctx.send("Thanks to <@567522840752947210>, urban dictionary is banned")
        else:
            await ctx.send(f"{first_result.image_url}")
            await client.close()
            f = open(f"{filepath}/logs.txt", "a")
            f.write(f"{datetime.datetime.now()} - {ctx.message.guild.name} | {ctx.message.author} : !search {args} -> {first_result.image_url}\n")
            f.close()

    else:
        await ctx.send(botlib.nope)

@client.command()
async def duck(ctx):
    await ctx.send("https://coorongcountry.com.au/wp-content/uploads/2016/01/Pacific-Black-Duck-53-cm.png")

@client.command()
async def bottomgear(ctx):
    output = bottomlib.bottomchoice()
    await ctx.send(output, tts=True)
    print("\u001b[33;1mDone: !bottomgear\u001b[31m")
    f = open(f"{filepath}/logs.txt", "a")
    f.write(f"{datetime.datetime.now()} - {ctx.message.guild.name} | {ctx.message.author} : !bottomgear {output}\n")
    f.close()


@client.command()
async def help(ctx):
    await ctx.send("""```-bottomgear : Prints out a randomly generated bottomgear meme. Probably NSFW.
-search [query] : Does a google search for something
-image [image] : Does a google image search for something
-cf : does a coin flip
-ru [words] : will translate something into russian
-info : prints info about the bot
-bb [sentence] : calls the AI chatbot to respond to what you said. Is very buggy and slow. **Currently not working**. I am looking into it.
-rewind [number of mentions to go back]: Prints the most recent mention of anyone in the server and what was said.
-duck : duck
-bucketlist : prints a to-do list
-trans : prints out the bot's opinion on trans people
-ping : works out the bot's ping
-invite : gets a link for the server and an invite link for the bot
-servers : Shows how many servers the bot is in
-code : gets the link for the github so you can see what goes on under the hood
-musichelp : Shows the help page for Music
-init : Sets up the database for the server. It's a good idea to run this whenever the owner or name changes. Also run this if you have not seen this command before.```""")

@client.command()
async def musichelp(ctx):
    await ctx.send("""```-connect : Connect to a voice channel.
-play : Play or queue a song with the given query.
-pause : Pause the currently playing song.
-resume : Resume the currently paused song.
-skip : Skip the currently playing song.
-stop : Stop and reset the music player.
-volume / -vol / -v : Change the music player's volume, between 1 and 100.
-shuffle / -mix : Shuffle the music player's queue.
-queue / -que / -q : Display's the music player's queued songs.
-nowplaying / now_playing / current / np : Show the currently playing song.
-swap_dj / -swap : Swap the current DJ to another member in the voice channel.
-equaliser : music filters that are still under dev```""")





client.run(token)

#To do
#Editable prefixes
#Maybe premium commands you need to pay for?
