import json
import os

import discord
from discord.ext import commands

import utils

filepath = os.path.abspath(os.path.dirname(__file__))


class bounty(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["bounties"])
    async def bounty(
        self,
        ctx,
        action=None,
        name=None,
        price=None,
        catagory=None,
        *,
        description=None,
    ):
        utils.log(ctx)
        with open(f"{filepath}/config/bounties.json", "r") as f:
            v = json.loads(f.read())

        with open(f"{filepath}/config/bountytakers.json", "r") as f:
            j = json.loads(f.read())

        num = 0
        num = 0
        if action is None:
            embed = discord.Embed(
                title="Bounties",
                description="Current tasks worth money\nDM ReCore if you have any questions",
                color=0x1E00FF,
            )
            for x in v:
                num = num + 1
                embed.add_field(name=x, value=f"${v[x][0]}", inline=False)
            await ctx.send(embed=embed)
        elif action == "add":
            if ctx.message.author.id == 451643725475479552:
                v[name.replace('"', "")] = list(
                    [int(price), catagory, description])
                with open(f"{filepath}/config/bounties.json", "w") as f:
                    f.write(json.dumps(v))

                await ctx.send("Done")
                j[name] = []
                with open(f"{filepath}/config/bountytakers.json", "w") as f:
                    f.write(json.dumps(j))

                channel = self.bot.get_channel(824960645279645718)
                await channel.send(f"New bounty added: {name} for ${v[name][0]}")
        elif action == "remove":
            if ctx.message.author.id == 451643725475479552:
                v.pop(name)
                with open(f"{filepath}/config/bounties.json", "w") as f:
                    f.write(json.dumps(v))

                j.pop(name)
                with open(f"{filepath}/config/bountytakers.json", "w") as f:
                    f.write(json.dumps(j))

                await ctx.send("Done")
                channel = self.bot.get_channel(824960645279645718)
                await channel.send(f"Bounty removed or completed: {name}")
        elif action == "take":
            if name is None:
                await ctx.send("Please enter a bounty to take")
            elif name not in v:
                await ctx.send("That was not a valid bounty")
            if j != "{}":
                if int(ctx.message.author.id) in j[name]:
                    await ctx.send("You are already took this bounty")
                else:
                    j[name].append(int(ctx.message.author.id))
                    with open(f"{filepath}/config/bountytakers.json", "w") as f:
                        f.write(json.dumps(j))

                    channel = self.bot.get_channel(824960645279645718)
                    await channel.send(
                        f"{ctx.message.author} just took the {name} bounty for ${v[name][0]}"
                    )
                    await ctx.send("Ok, added you to the bounty solver list")

        else:
            embed = discord.Embed(
                title=action, description=f"${v[action][0]}", color=0x1E00FF
            )
            embed.add_field(name="Category",
                            value=f"{v[action][1]}", inline=False)
            embed.add_field(name="Description",
                            value=f"{v[action][2]}", inline=False)
            embed.add_field(
                name="Takers", value=f"{len(j[action])}", inline=False)
            await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(bounty(bot))
