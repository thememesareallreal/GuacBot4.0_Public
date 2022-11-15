import discord
from discord.ext import commands, bridge
from cogs.extraclasses.jason import *
from cogs.extraclasses.perms import *

botData = FetchBotData()
serverData = FetchServerData()

class GuacMod(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Guac moderation processes active.")

    @bridge.bridge_command()
    @commands.check(is_it_me)
    async def guacmodtest(self, ctx):
        await ctx.respond('Guac moderation extension cog works!')

    @bridge.bridge_command()
    @commands.check(admin)
    async def guilddata(self, ctx):
        await ctx.respond(serverData[str(ctx.guild.id)])

    @bridge.bridge_command()
    @commands.check(admin)
    async def makeadminrole(self, ctx, role : discord.Role):
        if role.id in serverData[str(ctx.guild.id)]["HQ"]["adminroles"]:
            await ctx.respond(f"{role.name} already a Guac admin role.")
            return
        serverData[str(ctx.guild.id)]["HQ"]["adminroles"].append(role.id)
        UpdateServerData(serverData)
        await ctx.respond(f"{role.name} now a Guac admin role.")
    
    @bridge.bridge_command()
    @commands.check(admin)
    async def removeadminrole(self, ctx, role : discord.Role):
        indexingPurposes = serverData[str(ctx.guild.id)]["HQ"]["adminroles"]
        if role.id not in indexingPurposes:
            await ctx.respond(f"{role.name} already not a Guac admin role.")
            return
        serverData[str(ctx.guild.id)]["HQ"]["adminroles"].pop(indexingPurposes.index(role.id))
        UpdateServerData(serverData)
        await ctx.respond(f"{role.name} no longer a Guac admin role.")

    @bridge.bridge_command(aliases=["reactionban","rblacklist","rban"])
    @commands.check(admin)
    async def reactionblacklist(self, ctx, member : discord.Member):
        if member.id in serverData[str(ctx.guild.id)]["Reactions"]["blacklist"]:
            await ctx.respond(f"{member.display_name} already blacklisted for reactions.")
            return
        serverData[str(ctx.guild.id)]["Reactions"]["blacklist"].append(member.id)
        UpdateServerData(serverData)
        await ctx.respond(f"{member.display_name} blacklisted for reactions.")

    @bridge.bridge_command(aliases=["reactionunban","runblacklist","runban"])
    @commands.check(admin)
    async def reactionunblacklist(self, ctx, member : discord.Member):
        indexingPurposes = serverData[str(ctx.guild.id)]["Reactions"]["blacklist"]
        if member.id not in indexingPurposes:
            await ctx.respond(f"{member.display_name} already not blacklisted for reactions.")
            return
        serverData[str(ctx.guild.id)]["Reactions"]["blacklist"].pop(indexingPurposes.index(member.id))
        UpdateServerData(serverData)
        await ctx.respond(f"{member.display_name} no longer blacklisted for reactions.")

    @bridge.bridge_command()
    @commands.check(admin)
    async def botreactionson(self, ctx):
        duplicationPurposes = serverData[str(ctx.guild.id)]["Reactions"]["reactions"]
        serverData[str(ctx.guild.id)]["Reactions"]["reactions"] = not duplicationPurposes
        UpdateServerData(serverData)
        await ctx.respond(f"Reactions on: {not duplicationPurposes}")

    @bridge.bridge_command()
    @commands.check(admin)
    async def reactionson(self, ctx):
        duplicationPurposes = serverData[str(ctx.guild.id)]["Reactions"]["reactions"]
        serverData[str(ctx.guild.id)]["Reactions"]["reactions"] = not duplicationPurposes
        UpdateServerData(serverData)
        await ctx.respond(f"Reactions on: {not duplicationPurposes}")

    @bridge.bridge_command()
    @commands.check(admin)
    async def economyon(self, ctx):
        duplicationPurposes = serverData[str(ctx.guild.id)]["Economy"]["economy"]
        serverData[str(ctx.guild.id)]["Economy"]["economy"] = not duplicationPurposes
        UpdateServerData(serverData)
        await ctx.respond(f"Economy on: {not duplicationPurposes}")

def setup(bot):
    bot.add_cog(GuacMod(bot))