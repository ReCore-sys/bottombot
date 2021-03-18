import os, asyncio, math, random, time, async_cse, discord, discord.ext, botlib
from async_timeout import timeout
from discord.ext import commands, tasks
from tinydb import TinyDB, Query
from yahoo_fin import stock_info as si
filepath = os.path.abspath(os.path.dirname(__file__))

db = TinyDB(f'{filepath}/config/db.json')
s = Query()



def stockfind(dbid): #function to find how many stock a person owns
    re = db.search(s.suser==dbid)
    try:
        val = re[0]
        return val['stock']
    except:
        print("This user does not exist")
        return None
def addstock(user, amount): #Slightly less simple function to add money to a user's balance. Use negative numbers to remove money
    val = stockfind(user)
    try:
        val = val + amount
    except:
        print("User does not exist")
    db.update({"stock": val}, s.suser == user)

def balfind(dbid): #function to find the balance of the id dbid
    re = db.search(s.user==dbid)
    try:
        val = re[0]
        return val['bal']
    except:
        return None

def rankfind(dbid): #same as above but for ranks, not bal
    re = db.search(s.urank==dbid)
    try:
        val = re[0]
        return val['rank']
    except:
        return False
def ranktoid(dbid):
    userrank = rankfind(dbid)
    rankid = rankids[userrank.lower()]
    return rankid #simply gets a user's id and turns it into their rank's id

def canbuy(price, id): #simple function to check if a user can buy something. Price must be an int.
    bal = balfind(id)
    if bal >= price:
       return True
    else:
        return False
def addmoney(user, amount): #Slightly less simple function to add money to a user's balance. Use negative numbers to remove money
    val = balfind(user)
    try:
        val = val + amount
    except:
        print("User does not exist")
    db.update({"bal": val}, s.user == user)
#rank tiering
#Bronze
#Silver
#Gold
#Platinum
#Diamond
#Immortal
#Accendant
ranks = {
    'silver': 500,
    'gold': 700,
    'platinum': 1500,
    'diamond': 5000,
    'immortal': 10000,
    'ascendant': 20000,
    'taxman': 50000 #dict for ranks against price
    }
rankup = {
    'silver': 'Silver',
    'gold': 'Gold',
    'platinum': 'Platinum',
    'diamond': 'Diamond',
    'immortal': 'Immortal',
    'ascendant': 'Ascendant',
    'ascendant': 'Tax Man' #dict for ranks against display name
    }
rankids = {
    'silver': 2,
    'gold': 3,
    'platinum': 4,
    'diamond': 5,
    'immortal': 6,
    'ascendant': 7,
    'taxman': 8 #rank compared to it's id. Usefule for permission levels
}

cost = 50 #default cost of stocks, before applying modifiers
mult = 1
class money(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cost.start()

    @commands.command(aliases=["acc", "balance", "bal", "a"]) #shows the user's account
    async def account(self, ctx, *, target: discord.Member = None):
        if (target == None) and (balfind(ctx.message.author.id) == None):
            db.insert({'user': ctx.message.author.id, 'bal': 100})
            db.insert({'urank': ctx.message.author.id, 'rank': "Bronze"})
            db.insert({'suser': ctx.message.author.id, 'stock': 0})
            await ctx.send("Account created!") #if the user does not have an account, create one

        elif (target != None) and (balfind(ctx.message.author.id) == None):
            await ctx.send("That user does not have an account set up") #if the user pings someone who does not have an account, send this

        elif (target == None) and (balfind(ctx.message.author.id) != None): #show your balance if you don't enter someone else's account name
            user = ctx.message.author
            embed = discord.Embed(title=f"{user}", description="Account info", color=0x8800ff)
            embed.set_thumbnail(url=user.avatar_url)
            embed.add_field(name="ID", value=f"{user.id}", inline=True)
            embed.add_field(name="Balance", value=f"${balfind(user.id)}", inline=False)
            embed.add_field(name="Rank", value=f"{rankfind(user.id)}", inline=False)
            embed.add_field(name="Owned stocks", value=f"{stockfind(user.id)}", inline=False)
            await ctx.send(embed=embed)

        elif (target != None) and (balfind(ctx.message.author.id) != None): #show someone else's account if you do ping someone
            userid = int(botlib.nametoid(target.id))
            username = ctx.guild.get_member(userid)
            embed = discord.Embed(title=f"{target}", description="Account info", color=0x8800ff)
            embed.set_thumbnail(url=target.avatar_url)
            embed.add_field(name="ID", value=f"{userid}", inline=True)
            embed.add_field(name="Balance", value=f"${balfind(userid)}", inline=False)
            embed.add_field(name="Rank", value=f"{rankfind(userid)}", inline=False)
            embed.add_field(name="Owned stocks", value=f"{stockfind(userid)}", inline=False)
            await ctx.send(embed=embed)


    @commands.command()
    async def pay(self, ctx, arg1, target: discord.Member = None): #paying someone
        urval = int(balfind(ctx.message.author.id)) #finds the balance of the sender
        thrval = int(balfind(int(target.id))) #finds the bal of the target
        thrid = target.id #target's ID
        if target == None:
            await ctx.send("Sorry, that person either does not exist or has not set up their account.") #if that user's balance is None, they don't exist
        elif arg1.isnumeric == False: #if you try paying someone something that isn't a number
            await ctx.send("You need to give me a number")
        elif thrid == ctx.message.author.id: #if you try paying yourself
            await ctx.send("You can't pay yourself")
        elif (int(arg1) >= urval) or (urval - int(arg1) < 0): #if either you have less than $1 or you try and pay more than you have
            await ctx.send("Sorry, you don't have enough money")
        else: #if you can actually pay them
            urval = urval - int(arg1) #takes the amount from your bal
            thrval = thrval + int(arg1) #adds the amount to their bal
            db.update({"bal": urval}, s.user == (ctx.message.author.id))
            db.update({"bal": thrval}, s.user == int(target.id)) #write changes to the db
            await ctx.send(f"${arg1} was transferred to <@!{target.id}>") #inform the person that they were paid
            await target.send(f"{ctx.message.author} just payed you ${arg1}!\n({ctx.guild.name})") #send dm to target. Still not working

    @commands.command()
    async def add(self, ctx, arg1, target: discord.Member): #adds money to an account. Only I can use it
        if ctx.message.author.id == 451643725475479552:
            val = int(balfind(int(target.id)))
            val = val + int(arg1)
            db.update({"bal": val}, s.user == int(target.id))
            await ctx.send(f"${arg1} added")
        else:
            await ctx.send("Nope")

    @commands.command(pass_context=True)
    @commands.cooldown(1, 60*60*24, commands.BucketType.user)
    async def daily(self, ctx):
        if balfind != None:
            r = random.randint(20,50)
            addmoney(ctx.message.author.id, r)
            await ctx.send(f"${r} was added to your account")
        else:
            await ctx.send("You do not have an account. Do -account to make one")

    @commands.command(aliases=["stock","stonk","stonks"])
    async def stocks(self, ctx, action = None, count = None):
        global stock
        global cost

        user = ctx.message.author.id
        if stockfind(user) == None:
            await ctx.send("You need to create an account with -account first")
        else:

            stockcount = stockfind(user)
            bal = balfind(ctx.message.author.id)
            if action == None:
                await ctx.send(f"Current price of stocks: **${cost}**\nYou currently own {stockcount} stocks")
            else:
                count = int(count)
                fcost = int(round((float(count) * cost)))
                if count <= 0:
                    await ctx.send("You need to enter a number that is over 0")
                elif action == "buy" and (fcost > bal):
                    await ctx.send("You don't have enough money")
                elif (action == "sell") and (count > stockcount):
                    await ctx.send("You don't own that many stocks")
                elif action == "buy":
                    addmoney(user, (0 - fcost))
                    addstock(user, count)
                    await ctx.send(f"{count} stocks bought for ${fcost}")
                elif action == "sell":
                    addmoney(user, fcost)
                    addstock(user, (0 - count))
                    await ctx.send(f"{count} stocks sold for ${fcost}")
                elif action == "calc":
                    await ctx.send(f"{count} stocks at ${cost} is worth ${round(count * cost)}")




    @commands.command(aliases=["ranks"])
    async def rank(self, ctx, ag1 = None, rank=None): #allows someone to buy a rank
        global ranks #idk if this is needed but it can't hurt to have it
        user = ctx.message.author.id #"user" is easier to type than "ctx.message.author.id"
        if ag1 != "buy": #if they don't have "buy" as their first arg, send prices
            embed=discord.Embed(title="Ranks", description="The price of different ranks", color=0x1e00ff)
            embed.set_thumbnail(url="https://lh3.googleusercontent.com/proxy/07h14DsTB_1a1UudwyVJz7OICAz9RSOE0uLEI3ox3vFTdjvM4hJolKhXaAEk0UeSeE2V92Qgv8ScFee0Zm9GoR-VKc6EadFPwYIVw93O6-EiSvI")
            embed.add_field(name="Silver", value="$500", inline=True)
            embed.add_field(name="Gold", value="$700", inline=True)
            embed.add_field(name="Platinum", value="$1500", inline=True)
            embed.add_field(name="Diamond", value="$5000", inline=True)
            embed.add_field(name="Immortal", value="$10000", inline=True)
            embed.add_field(name="Ascendant", value="$200000", inline=True)
            embed.add_field(name="Taxman", value="$50000", inline=True)
            embed.set_footer(text='Use "-rank buy [rank name]" to buy a rank')
            await ctx.send(embed=embed)
        else: #if they do have it, start doing stuff
            # crank = rankfind(int(user))
            # crankv = ranks[crank.lower()]
            val = ranks[rank.lower()]
            if rank == None:
                await ctx.send("Please choose a rank to buy") #if they don't enter a rank to buy
            elif (rank.lower() in ranks) == False:
                await ctx.send("That was not a valid rank") #if the rank does not appear in the ranks list (dict)
            elif canbuy(val, user) == False:
                await ctx.send("You do not have enough money to buy this") #explains itself
            # elif crankv > val:
                # await ctx.send("You can't buy a lower rank")
            # elif crankv == int(ranks[rank.lower()]):
                # await ctx.send("You can't buy your current rank")
            else:
                cost =  0 - val  #turn the value into a negative so you can buy it properly
                rank2 = rankup[rank.lower()] #gets the display name of the rank
                db.update({"rank": rank2}, s.urank == int(ctx.message.author.id)) #writes new rank to db
                addmoney(user, cost) #takes the money from the account (adds a negative value)
                await ctx.send(f"Rank {rank} was bought for ${val}") #let them know

    @tasks.loop(seconds=60*10)
    async def cost(self):
        global cost
        stp = si.get_live_price("nktr")
        sdiff = stp - 20
        precost = round((sdiff * random.uniform(19.0, 21.0)), 2)
        if precost < 1:
            cost = 1
        elif precost > 100:
            cost = 100
        else:
            cost = precost
        print(f"\u001b[35mstock price is ${cost}\u001b[31m")

def setup(bot: commands.Bot):
    bot.add_cog(money(bot))
