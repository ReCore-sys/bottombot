import os
import asyncio
import math
import random
import time
from googlesearch import search
import async_cse
import discord
from async_timeout import timeout
from discord.ext import commands
import better_profanity
from translate import Translator
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from simpleeval import simple_eval
import operator
import ast
import datetime
import logging

#pip install discord.py asyncio Chatterbot chatterbot_corpus async_cse googlesearch-python better-profanity translate simpleeval
filepath = os.path.abspath(os.path.dirname(__file__))
badsearch = ["cock","jizz","cum","dick","ass","shit","penis","fuck","anal","semen","boob","tit","vag","pussy","isis","ISIS","porn","pedo","hentai","r34","sex","nigger","anus"] #more bad words to limit searches, cos I really don't trust people
f = open(f"{filepath}/config/token.txt")
token = str(f.readline())
f.close()
null = None

#Chatterbot stuff

chatbot = ChatBot('Bottombot')
mathbot = ChatBot('MathBot',
            logic_adapters=[
        'chatterbot.logic.MathematicalEvaluation',
        'chatterbot.logic.UnitConversion'
    ])

trainer = ListTrainer(chatbot)

trainer.export_for_training('./my_export.json')

trainer.train([
    "UwU"
])
#Chatterbot stuff

#Maths

#Maths

client = discord.Client()

client = commands.Bot(command_prefix = "-")

client.remove_command('help')
starttime = null
log = False
@client.command()
async def logging(ctx):
    if log == False:
        logging.basicConfig(level=logging.INFO)
        log = True
        await ctx.send(f"Logging was set to {log}")
    else:
        logging.basicConfig(level=logging.CRITICAL)
        log = False
        await ctx.send(f"Logging was set to {log}")





@client.event
async def on_ready():
    activity = discord.Game(name="bottombot", type=3)
    status = random.choice(["ReCore's GPU melt","ReCore's CPU catch fire","God die","the old gods die","time end","reality crumple","missiles fly","the CCPC commit horrific crimes"])
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status))
    print("\u001b[35mThe bot is up")
    channel = client.get_channel(806378599065190412)
    await channel.send('Bot is up')
    channel = client.get_channel(812145603848568852)
    await channel.send('Bot is up')
    f = open("logs.txt", "a")
    f.write(f"\n---\n{datetime.datetime.now()} Bot started\n---\n")
    f.close()
    print(filepath)

@client.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send('Heyo! I am bottombot, a cancerous mess. You can join my discord server here: https://discord.gg/2WaddNnuHh \nYou can also invite the bot to other servers with this link: https://discord.com/api/oauth2/authorize?client_id=758912539836547132&permissions=3324992&scope=bot \nUse !help to find out what commands I can use!')
        break
    print(f"\u001b[35mJoined an new server! {guild.name} : {guild.id}\u001b[31m")
    #region Setup database
    os.system(f'mkdir ./serversettings/{guild.id}')
    f = open("logs.txt", "a")
    f.write(f"{datetime.datetime.now()}: Joined an new server! {guild.name} : {guild.id}\n")
    f.close()
    os.system(f"touch ./serversettings/{guild.id}/replay.txt")
    os.system(f"touch > ./serversettings/{guild.id}/serverdetails.txt")
    f = open(f"{filepath}/serversettings/{guild.id}/serverdetails.txt", "a")
    f.write(f"Server name: {guild.name}\n")
    f.write(f"Server id: {guild.id}\n")
    f.write(f"Server id: {guild.owner}\n")
    f.write(f"Server id: {guild.description}\n")
    f.write(f"Joined at {datetime.datetime.now()}")
    f.close()
    print(f"\u001b[35mDatabase set up for server {guild.id} ({guild.name})\u001b[31m")
    f = open("logs.txt", "a")
    f.write(f"{datetime.datetime.now()}: Database set up for server {guild.id} ({guild.name})\n")
    f.close()
    #endregion

@client.event
async def on_message(message):
    if '<@!' in message.content:
        os.system(f'IF exist serversettings/{message.guild.id} ELSE mkdir serversettings/{message.guild.id} && echo \u001b[36mserversettings/{message.guild.id} created')
        if message.author != client.user:
            pingC = message.content
            pingU = message.author
            try:
                f = open(f"{filepath}/serversettings/{message.guild.id}/replay.txt", "a")
                f.write(f"\n'{pingC}' was sent by {pingU}")
                f.close()
            except FileNotFoundError:
                os.system(f"touch serversettings/{message.guild.id}/replay.txt")
                f = open(f"{filepath}/serversettings/{message.guild.id}/replay.txt", "a")
                f.write(f"\n'{pingC}' was sent by {pingU}")
                f.close()
    elif message.content == "hello there":
        channel = message.channel
        await channel.send('general kenobi')
    elif message.content == "Hello there":
        channel = message.channel
        await channel.send('general kenobi')
    await client.process_commands(message)

@client.command()
async def rewind(ctx, arg1):
    try:
        with open(f"{filepath}/serversettings/{ctx.guild.id}/replay.txt", "r") as f:
            lines = f.read().splitlines()
            last_line = lines[int(arg1) * -1]
            print(f"\u001b[33;1mMention: {last_line} was called\u001b[31m")
            await ctx.send(last_line)
            f.close()
            f = open("logs.txt", "a")
            f.write(f"{datetime.datetime.now()} - {ctx.message.guild.name} | {ctx.message.author} : !rewind was called: result {arg1} was called with the result '{last_line}'\n")
            f.close()
    except FileNotFoundError:
        await ctx.send("No @ mentions have been sent in this server. Please report this if it is an error")

@client.event
async def on_guild_leave(guild):
    os.system(f"rmdir settings/{guild.id}")
    f = open("logs.txt", "a")
    f.write(f"{datetime.datetime.now()}: Left a server! {guild.name} : {guild.id}\n")
    print(f"Left a server! {guild.name} : {guild.id}\u001b[31m")
    f.close()

@client.command()
async def invite(ctx):
    await ctx.send("Server: https://discord.gg/2WaddNnuHh \nBot invite:  https://discord.com/api/oauth2/authorize?client_id=758912539836547132&permissions=3324992&scope=bot")

@client.command()
async def servers(ctx):
    await ctx.send(str(len(client.guilds)) + " servers have been infected!")

@client.command()
async def roll(ctx, arg1):
    if arg1.isnumeric():
        await ctx.send(random.randint(1, int(arg1)))
    else:
        await ctx.send("I need a number dumbass")

@client.command()
async def ru(ctx, *, args):
    if args != "uwu":
        tr1= Translator(to_lang="ru")
        translation = tr1.translate(args)
        print(f"\u001b[33;1m{translation}\u001b[31m")
        await ctx.send(translation)
        f = open("logs.txt", "a")
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

canbb = True
@client.command()
async def bb(ctx, *, args):
    global ttst
    if ctx.message.author.id == 763336086369861672:
        await ctx.send("no, fuck off")
    elif ctx.message.author.id == 456028176557015040:
        await ctx.send("no, fuck off")
    else:
        await ctx.trigger_typing()
        response = chatbot.get_response(args)

        print(f"\u001b[33;1m{ctx.message.guild.name} | {ctx.message.author}: {args} -> {response}\u001b[31m")
        await ctx.send(response, tts=ttst)
        f = open("logs.txt", "a")
        f.write(f"{datetime.datetime.now()} - {ctx.message.guild.name} | {ctx.message.author} : !bb {args} -> {response}\n")
        f.close()

@client.command()
async def maths(ctx, *, args):
    global ttst
    global s
    if ctx.message.author.id == 763336086369861672:
        await ctx.send("no, fuck off")
    elif ctx.message.author.id == 456028176557015040:
        await ctx.send("no, fuck off")
    else:
        await ctx.trigger_typing()
        response = simple_eval(args.replace("^", "**"), functions={"sqrt": lambda x: sqrt(x)})
        print(f"\u001b[33;1m{ctx.message.guild.name} | {ctx.message.author}: {args} -> {response}\u001b[31m")
        await ctx.send(response, tts=ttst)
        f = open("logs.txt", "a")
        f.write(f"{datetime.datetime.now()} - {ctx.message.guild.name} | {ctx.message.author} : !bb {args} -> {response}\n")
        f.close()

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
        exit()
    else:
        await ctx.send("Lol nah")

pingC = None
pingU = None

@client.command()
async def trans(ctx):
    await ctx.send(":transgender_flag: Trans rights are human rights :transgender_flag: ")

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

    elif ctx.message.author.id == 567522840752947210:
        ctx.send("Fuck off")

    else :
            client = async_cse.Search("AIzaSyAIc3NVCXoMDUzvY4sTr7hPyRQREdPUVg4") # create the Search client (uses Google by default!)
            results = await client.search(args, safesearch=True) # returns a list of async_cse.Result objects
            first_result = results[0] # Grab the first result
            if "urbandictionary" in first_result.url:
                await ctx.send("Thanks to <@567522840752947210>, urban dictionary is banned")
            else:
                await ctx.send(f"**{first_result.title}**\n{first_result.url}")
                await client.close()
    f = open("logs.txt", "a")
    f.write(f"{datetime.datetime.now()} - {ctx.message.guild.name} | {ctx.message.author} : !search {args} -> {first_result.url}\n")
    f.close()

@client.command()
async def image(ctx,*,args):
    isbad2 = better_profanity.profanity.contains_profanity(args)

    if ((isbad2 == True) or (args in badsearch)):
            badresponse = random.choice(["This is why your parents don't love you","Really?","You are just an asshole. You know that?","God has abandoned us","Horny bastard"])
            await ctx.send(badresponse)
            print(f"\u001b[33;1m{ctx.message.author} tried to search '{args}'\u001b[31m")



    elif ctx.message.author.id == 567522840752947210:
        ctx.send("Fuck off")
    else:
        client = async_cse.Search("AIzaSyAIc3NVCXoMDUzvY4sTr7hPyRQREdPUVg4") # create the Search client (uses Google by default!)
        results = await client.search(args, safesearch=True) # returns a list of async_cse.Result objects
        first_result = results[0] # Grab the first result
        if "urbandictionary" in first_result.image_url:
            await ctx.send("Thanks to <@567522840752947210>, urban dictionary is banned")
        else:
            await ctx.send(f"{first_result.image_url}")
            await client.close()
    f = open("logs.txt", "a")
    f.write(f"{datetime.datetime.now()} - {ctx.message.guild.name} | {ctx.message.author} : !search {args} -> {first_result.image_url}\n")
    f.close()

@client.command()
async def duck(ctx):
    await ctx.send("https://coorongcountry.com.au/wp-content/uploads/2016/01/Pacific-Black-Duck-53-cm.png")

@client.command()
async def bottomgear(ctx):
            verb1 = random.choice(["fucking ends", "voilently penetrates", "gives a hicky to", "stabs","reinvents","violates","scams","sells ketamine to","buys ketamine from","drives over","has an unusually vigorous orgy with","unhinges his jaw and devours"])
            noun1 = random.choice(["god", "your mother", "pyro from tf2", "the Queen","a 1982 Rolls Royce Silver Wraith", "the 1999 toyota corolla", "Lebron James", "a 100% legitimate nigerian prince","253 primary school students", "the entirety of europe", "the abstract concept of time","a male stripper"])
            verb2 = random.choice(["bash", "assimilate", "make explosive love to", "commit crimes to", "alt-f4", "give heroin to", "start a crack epidemic with","whisper seductively to","bully","drink","start a pyramid scheme with"])
            noun2 = random.choice(["dwane the cock jhonson","5th grade stoners","ben shapiro","Mike Oxlong","you","Jehova","Heavy","[Redacted]", "Ugandan villagers","the middle east","Jimmy Neutron"])
            verb3 = random.choice(["jacks off", "uninstalls", "eviscerates","obliterates","assults", "finds the secret cross-dressing wardrobe of", "speed-dates", "invests in bitcoin with", "falls in love with", "dismantles", "severely irradiates","sensually kisses"])
            noun3 = random.choice(["my dick","Satan","the Syrian schoolhouse","your future kids", "a Tsar Bomba", "the Gustav Railway Gun", "Zimbabwe", "Mark Zuckerberg", "Jeff Bezos", "Uncle Sam", "The Chinese Communist Party", "Great Leader Kim Jong Un, wise and just ruler of The Democratic People's Republic of North Korea, greatest nation of all time", "an A-10 warthog", "the Lockheed-Martin company", "the exhaust pipe of a Western Star cargo truck", "a BMW motorbike", "an electric car", "7 metric tonnes of raw plutonium ore", "2 crates of C4", "an entire keg of beer", "a quaint village bakery in western France", "an elderly gardener", "Donald J Trump", "Bernie Sanders", "Stalin","a duck"])
            consequence = random.choice(["deeply regrets it", "gets a huge boner from it", "is anointed Grand High Emperor", "is promptly arrested", "gets sent to a gulag", "gets stabbed", "is tried for war crimes", "is found innocent", "receives a life sentence", "gets addicted", "is nominated for a Nobel Peace Prize", "is violently and lovingly dismembered", "is turned inside out", "gets to meet the man of his dreams","loses in monopoly"])
            output = f"Tonight on bottomgear James {verb1} {noun1}, I {verb2} {noun2} and Hammond {verb3} {noun3} and {consequence}"
            await ctx.send(output, tts=True)
            print("\u001b[33;1mDone: !bottomgear\u001b[31m")
            f = open("logs.txt", "a")
            f.write(f"{datetime.datetime.now()} - {ctx.message.guild.name} | {ctx.message.author} : !bottomgear {output}\n")
            f.close()


@client.command()
async def help(ctx):
    await ctx.send("""```!bottomgear : Prints out a randomly generated bottomgear meme. Probably NSFW.
                            !search [query] : Does a google search for something
                            !image [image] : Does a google image search for something
                            !cf : does a coin flip
                            !ru [words] : will translate something into russian
                            !info : prints info about the bot
                            !bb [sentence] : calls the AI chatbot to respond to what you said. Is very buggy and slow.
                            !rewind [number of mentions to go back]: Prints the most recent mention of anyone in the server and what was said.
                            !duck : duck
                            !bucketlist : prints a to-do list
                            !trans : prints out the bot's opinion on trans people
                            !ping : works out the bot's ping
                            !invite : gets a link for the server and an invite link for the bot
                            !servers : Shows how many servers the bot is in```""")
client.run(token)