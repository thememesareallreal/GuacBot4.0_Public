import discord, time, os, subprocess, random
from discord.ext import bridge, commands, tasks
from cogs.extraclasses.timer import *
from cogs.extraclasses.jason import *
from cogs.extraclasses.avocado import *
from cogs.extraclasses.perms import *
from itertools import cycle

#Version 4.0 experimental
intents = discord.Intents.all()
bot = discord.ext.bridge.Bot(command_prefix = '$', intents=intents, case_insensitive=True, activity=discord.Game("Only legends see this."))
bot.add_check(not_blacklisted)

@bot.event
async def on_ready():
    print("Main bot processes active.")
    RefreshServerData(bot)
    change_status.start()
    animation.start()

@bot.event
async def on_guild_join():
    RefreshServerData(bot)

@bot.event
async def on_guild_remove():
    RefreshServerData(bot)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.respond("That isn't a command, buddy.")
        return
    if isinstance(error, commands.CommandInvokeError):
        if isinstance(error.original, discord.Forbidden):
            await ctx.respond("I don't have the permissions to do that here...", ephemeral=True)
            return
        else:
            await ctx.respond_help(ctx.command)
    if isinstance(error, commands.CheckFailure):
        if (not await not_blacklisted(ctx)):
            await ctx.respond("Sorry, you're blacklisted...")
        elif (not await is_it_me(ctx)):
            await ctx.respond("Sorry, that command is only for dad.")
        elif (not await admin(ctx)):
            await ctx.respond("Sorry, that command is only for admins.")
        elif (not await sophie(ctx)):
            await ctx.respond("Sorry, that command is only for Sophie...")
        else:
            await ctx.respond("Sorry, you don't have permission to do that...")
        return
    channel = await ctx.bot.fetch_channel(1037298707705634917)
    await channel.send(f"Error {type(error)} on command ${ctx.command}: {error}")

@bot.bridge_command()
@commands.check(is_it_me)
async def refreshserverdata(ctx):
    RefreshServerData(bot)
    await ctx.respond("Refreshing server data!")

@bot.bridge_command()
@commands.check(is_it_me)
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')
    await ctx.respond(f'Extension "{extension}" loaded!')

@load.error
async def load_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.respond('Please choose what cog to load.')
    else:
        channel = await ctx.bot.fetch_channel(1037298707705634917)
        await channel.send(f"Error while loading cog: {error}")

@bot.bridge_command()
@commands.check(is_it_me)
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    await ctx.respond(f'Extension "{extension}" unloaded!')

@unload.error
async def unload_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.respond('Please choose what cog to unload.')
    else:
        channel = await ctx.bot.fetch_channel(1037298707705634917)
        await channel.send(f"Error while unloading cog: {error}")

@bot.bridge_command()
@commands.check(is_it_me)
async def reload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    bot.load_extension(f'cogs.{extension}')
    await ctx.respond(f'Extension "{extension}" reloaded!')

@reload.error
async def reload_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.respond('Please choose what cog to reload.')
    else:
        channel = await ctx.bot.fetch_channel(1037298707705634917)
        await channel.send(f"Error while reloading cog: {error}")

@bot.bridge_command()
@commands.check(is_it_me)
async def die(ctx):
    await ctx.respond("Goodbye, father.")
    await bot.change_presence(activity=discord.Game("Goodbye."))
    quit()

@die.error
async def die_error(ctx, error):
    channel = await ctx.bot.fetch_channel(1037298707705634917)
    await channel.send(f"Error while dying: {error}")

@bot.bridge_command()
@commands.check(is_it_me)
async def restart(ctx):
    await ctx.respond("Restarting!")
    os.startfile(__file__)
    os._exit(1)

@restart.error
async def restart_error(ctx, error):
    channel = await ctx.bot.fetch_channel(1037298707705634917)
    await channel.send(f"Error while restarting: {error}")

@bot.bridge_command(description="Displays my uptime and when it was last checked!")
async def uptime(ctx):
    time_elapsed = time.time() - botData["HQ"]["start_time"]
    time_checked = time.time() - botData["HQ"]["time_checked"]
    botData["HQ"]["time_checked"] = time.time()
    UpdateBotData(botData)
    await ctx.respond("Uptime: " + time_convert(time_elapsed) + "\nLast Checked: " + time_convert(time_checked) + " ago.")

@uptime.error
async def uptime_error(ctx, error):
    await ctx.respond(f"Error while checking uptime: {error}")

@bot.bridge_command(description="Guac will send you his link and a link to the support server!")
async def invite(ctx):
    await ctx.respond("Link to bot: https://discord.com/api/oauth2/authorize?client_id=582337819532460063&permissions=8&scope=bot\nLink to support server: https://discord.gg/2kgZazXN68")

#Load cogs
for filename in os.listdir('./cogs'):
    if filename.endswith('.py') and not filename.startswith("_"):
        bot.load_extension(f'cogs.{filename[:-3]}')

#Load JSON file
botData = InitBotData()

#Status loop
possiblestatuses = botData["HQ"]["possible_statuses"]

def NewOrder(iterable):
    order = []
    indices = list(random.sample(range(len(iterable)), len(iterable)))
    for i in indices:
        order.append(iterable[i])
    return order

status = cycle(NewOrder(possiblestatuses))
@tasks.loop(seconds=300)
async def change_status():
    newStatus = next(status)
    activityType = newStatus["type"]
    activityText = newStatus["status"]
    if activityType == "game":
        await bot.change_presence(activity=discord.Game(activityText))
    elif activityType == "stream":
        await bot.change_presence(activity=discord.Streaming(name=activityText, url="https://www.twitch.tv/thememesareallreal"))
    elif activityType == "watch":
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=activityText))
    elif activityType == "listen":
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=activityText))

# Animation system
animationStates=cycle(["[          ]", "[#         ]", "[##        ]", "[###       ]", "[####      ]",
                        "[#####     ]", "[######    ]", "[#######   ]", "[########  ]", "[######### ]", "[##########]"])
@tasks.loop(seconds=1)
async def animation():
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    os.system('cls')
    print(f"{next(animationStates)}\nGuacBot is active.\nThe time is: {current_time}")

#Start bot with token in json file
if Avocado():
    bot.run(botData["HQ"]["token"])