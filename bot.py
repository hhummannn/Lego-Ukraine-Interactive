import os
import random
import requests
from discord import Intents, File
from discord.ext import commands
from dotenv import load_dotenv
from stats import elements
from imageProcessing import card, merge, initInfo
from game import Game, Player

# bot login
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(intents=Intents.all(), command_prefix="!", help_command=None)


# game switch
async def gameTime(p1, e1, p2, e2, channel):
    first = Player(p1.name, e1, p1)
    await first.info(channel)
    second = Player(p2.name, e2, p2)
    await second.info(channel)
    game = Game(first, second)
    result = False
    while not result:
        result = await game.move(channel, bot)
    return True


async def playerEntry(ctx):
    def check(reaction, user):
        return (
            str(reaction) in ["🔥", "💧", "🌄", "🪨", "🌪", "❄"]
            and user.id != bot.user.id
            and reaction.message.content == choiceMessage.content
        )

    choiceMessage = await ctx.channel.send(
        "Next player, please send your element as confirmation. Please, react with one from:\n"
        f"Fire - 🔥\nWater - 💧\nEarth - 🌄\nStone - 🪨\nAir - 🌪\nIce - ❄"
    )
    for emoji in ["🔥", "💧", "🌄", "🪨", "🌪", "❄"]:
        await choiceMessage.add_reaction(emoji)

    reaction, user = await bot.wait_for("reaction_add", check=check)

    els = {
        "🔥": "fire",
        "💧": "water",
        "🌄": "earth",
        "🪨": "stone",
        "🌪": "air",
        "❄": "ice",
    }
    await ctx.channel.send(f"Player confirmed: {user.name}, {els[str(reaction)]}")
    avatar = user.display_avatar.url
    data = requests.get(avatar).content
    with open(f"data/avatar/{user.name}.jpg", "wb") as handler:
        handler.write(data)
    return user, els[str(reaction)]


# commands start here
@bot.command()
async def help(ctx):
    await ctx.channel.send(
        f"This is Lego Ukraine Interactive bot (LUI), that is created for Lego Ukraine discord server\n"
        f"The bot is in development, so wait for updates!\n\n"
        f"Available commands are:\n\n"
        f"!help - show this message\n"
        f"!test - check if the bot is alive (not guaranteed for now...)\n"
        f"!element - get information about a specific element of Bionicle Game\n"
        f"!gameinfo - get information and rules about Bionicle 1v1 game\n"
        f"!game - start the game"
    )


@bot.command()
async def test(ctx):
    await ctx.channel.send("I live!")


@bot.command()
async def element(ctx):
    def check(reaction, user):
        return str(reaction) in ["🔥", "💧", "🌄", "🪨", "🌪", "❄"] and user == ctx.author

    choiceMessage = await ctx.channel.send(
        "Choose element to get info about:\n"
        f"Fire - 🔥\nWater - 💧\nEarth - 🌄\nStone - 🪨\nAir - 🌪\nIce - ❄"
    )
    for emoji in ["🔥", "💧", "🌄", "🪨", "🌪", "❄"]:
        await choiceMessage.add_reaction(emoji)
    while True:
        reaction, user = await bot.wait_for("reaction_add", check=check)
        break

    els = {
        "🔥": "fire",
        "💧": "water",
        "🌄": "earth",
        "🪨": "stone",
        "🌪": "air",
        "❄": "ice",
    }
    elinfo = els[str(reaction)]
    await ctx.channel.send(
        f"{elinfo[0].upper() + elinfo[1:]} abilities:\n"
        f"1. Mask - {elements[elinfo]['mask']['name']}: {elements[elinfo]['mask']['description']}\n\n"
        f"2. Normal attack - {elements[elinfo]['normal']['name']}: {elements[elinfo]['normal']['description']}\n\n"
        f"3. Healing ability - {elements[elinfo]['heal']['name']}: {elements[elinfo]['heal']['description']}\n\n"
        f"4. Resting - {elements[elinfo]['rest']['name']}: {elements[elinfo]['rest']['description']}\n\n"
    )


@bot.command()
async def gameinfo(ctx):
    await ctx.channel.send(
        f"This is 2-man Bionicle inspired step-by-step game (name to be added)\n\n"
        f"Rules:\n"
        f"1. Two players confirm their participation by stating their element for the game.\n"
        f"2. Players make their move one after another.\n"
        f"Make sure to read what options you have. Trying to make a move that takes more stamina than you have will be punished.\n"
        f"3. Players' stats are updated after each person's move.\n"
        f"4. The game is ended as soon as someone's health reaches zero.\n\n"
        f"Have fun!"
    )


@bot.command()
async def game(ctx):
    initInfo()
    await ctx.channel.send(file=File("data/cards/info.jpg"))

    player1, el1 = await playerEntry(ctx)
    player2, el2 = await playerEntry(ctx)

    await gameTime(player1, el1, player2, el2, ctx.channel)


bot.run(TOKEN)
