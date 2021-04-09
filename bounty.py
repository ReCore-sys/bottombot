import settings, json, discord, os
from discord.ext import commands, menus
filepath = os.path.abspath(os.path.dirname(__file__))
class bounty(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command(aliases=["bounties"])
    async def bounty(self, ctx, action = None, name = None, price = None, catagory = None, *, description = None):
        f = open(f"{filepath}/config/bounties.json", "r")
        v = json.loads(f.read())
        f.close()
        f = open(f"{filepath}/config/bountytakers.json", "r")
        j = json.loads(f.read())
        f.close()
        num = 0
        num = 0
        if action == None:
            embed=discord.Embed(title="Bounties", description="Current tasks worth money\nDM ReCore if you have any questions", color=0x1e00ff)
            for x in v:
                num = num + 1
                embed.add_field(name=x, value=f"${v[x][0]}", inline=False)
            await ctx.send(embed=embed)
        elif action == "add":
            if ctx.message.author.id == 451643725475479552:
                v[name.replace('"', '')] = list([int(price), catagory, description])
                f = open(f"{filepath}/config/bounties.json", "w")
                f.write(json.dumps(v))
                f.close()
                await ctx.send("Done")
                j[name] = []
                f = open(f"{filepath}/config/bountytakers.json", "w")
                f.write(json.dumps(j))
                f.close()
                channel = self.bot.get_channel(824960645279645718)
                await channel.send(f"New bounty added: {name} for ${v[name][0]}")
        elif action == "remove":
            if ctx.message.author.id == 451643725475479552:
                v.pop(name)
                f = open(f"{filepath}/config/bounties.json", "w")
                f.write(json.dumps(v))
                f.close()
                j.pop(name)
                f = open(f"{filepath}/config/bountytakers.json", "w")
                f.write(json.dumps(j))
                f.close()
                await ctx.send("Done")
                channel = self.bot.get_channel(824960645279645718)
                await channel.send(f"Bounty removed or completed: {name}")
        elif action == "take":
            if name == None:
                await ctx.send("Please enter a bounty to take")
            elif name not in v:
                await ctx.send("That was not a valid bounty")
            if j != "{}":
                if int(ctx.message.author.id) in j[name]:
                    await ctx.send("You are already took this bounty")
                else:
                    j[name].append(int(ctx.message.author.id))
                    f = open(f"{filepath}/config/bountytakers.json", "w")
                    f.write(json.dumps(j))
                    f.close()
                    channel = self.bot.get_channel(824960645279645718)
                    await channel.send(f"{ctx.message.author} just took the {name} bounty for ${v[name][0]}")
                    await ctx.send("Ok, added you to the bounty solver list")

        elif action in v:
            embed=discord.Embed(title=action, description=f"${v[action][0]}", color=0x1e00ff)
            embed.add_field(name="Category", value=f"{v[action][1]}", inline=False)
            embed.add_field(name="Description", value=f"{v[action][2]}", inline=False)
            embed.add_field(name="Takers", value=f"{len(j[action])}", inline=False)
            await ctx.send(embed=embed)



def setup(bot: commands.Bot):
    bot.add_cog(bounty(bot))
