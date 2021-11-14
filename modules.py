import settings
import json
import discord
import os
from discord.ext import commands
filepath = os.path.abspath(os.path.dirname(__file__))


class modules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["modules", "mod"])
    async def module(self, ctx, module=None, type=None):
        global valids
        serverid = ctx.message.guild.id
        if (ctx.message.author.guild_permissions.administrator) or (ctx.message.author.id == 451643725475479552):
            if os.path.isdir(filepath + "/settings/" + str(serverid)) == False:
                os.mkdir(filepath + "/settings/" + str(serverid))
            if os.path.isfile(filepath + "/settings/" + str(serverid) + ".json") == False:
                with open(filepath + "/settings/" + str(serverid) + ".json", "w") as f:
                    json.dump({"economy": True}, f)
            f = open(f"{filepath}/settings/{serverid}.json", "r")
            v = json.loads(f.read())
            f.close()
            if module == None:
                embed = discord.Embed(
                    title="Modules", description="Use -modules <module id> <on/off> to enable and disable parts of the bot")
                embed.add_field(
                    name="Economy (economy)", value=f'{settings.check(ctx.message.guild.id, "get", "economy")}', inline=True)
                embed.add_field(name="Cross server chat (cross)",
                                value=f'{settings.check(ctx.message.guild.id, "get", "cross")}', inline=True)
                embed.add_field(
                    name="Search (search)", value=f'{settings.check(ctx.message.guild.id, "get", "search")}', inline=True)
                embed.add_field(name="Image Search (image)",
                                value=f'{settings.check(ctx.message.guild.id, "get", "image")}', inline=True)
                embed.add_field(
                    name="Chatbot (bb)", value=f'{settings.check(ctx.message.guild.id, "get", "bb")}', inline=True)
                embed.add_field(
                    name="Store (store)", value=f'{settings.check(ctx.message.guild.id, "get", "store")}', inline=True)
                embed.add_field(
                    name="Bounties (bounty)", value=f'{settings.check(ctx.message.guild.id, "get", "bounty")}', inline=True)
                await ctx.send(embed=embed)
            elif module != None and type == None:
                await ctx.send("Please enter on or off")
            elif module not in ["economy", "search", "image", "bb", "store", "bounty"]:
                await ctx.send("That is not a valid module id")
            else:
                if type == "on":
                    settings.check(ctx.message.guild.id, "set", module, True)
                    await ctx.send(f"Ok, {module} was set to {type}")
                elif type == "off":
                    settings.check(ctx.message.guild.id, "set", module, False)
                    await ctx.send(f"Ok, {module} was set to {type}")
                else:
                    await ctx.send("Please enter on or off")
        else:
            await ctx.send("Sorry, only admins can change settings")


def setup(bot: commands.Bot):
    bot.add_cog(modules(bot))
