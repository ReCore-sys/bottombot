import time

from discord.ext import commands


times = dict()


class admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, ctx):
        roles = ctx.guild.roles
        bequiet = list()
        slowdown = list()
        global times
        for x in roles:
            if (x.name).lower() == "stfu":
                for y in x.members:
                    bequiet.append(y.id)
            elif (x.name).lower() == "slowdown":
                for y in x.members:
                    slowdown.append(y.id)
        if ctx.author.id in bequiet:
            await ctx.delete()
        ctime = time.time()
        if ctx.author.id in slowdown:
            if ctx.author.id in times:
                if times[ctx.author.id] > ctime:
                    await ctx.delete()
                else:
                    times.pop(ctx.author.id)
            else:
                times[ctx.author.id] = ctime + 5
                times


def setup(bot):
    bot.add_cog(admin(bot))
