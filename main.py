import os
import random
import requests
from discord import Intents, File
from discord.ext import commands
from dotenv import load_dotenv
from stats import elements
from imageProcessing import card, get_concat_v

moves = ["mask", "normal", "heal"]
valid_moves = ["mask", "normal", "heal", "rest"]

class Player:
    def __init__(self, name, element, member):
        self.member = member
        self.name = name
        self.element = element
        self.health = 100
        self.energy = 100
        self.shield = 0
        self.damage = 0
        self.stats = elements[self.element]

    def mask(self, other):
        other.health += self.stats["mask"]["attack"]
        self.energy += self.stats["mask"]["energy"]
        self.health += self.stats["mask"]["health"]
        self.shield += self.stats["mask"]["shield"]
        self.damage += self.stats["mask"]["damage"]
    def attack(self, other):
        other.health += self.stats["normal"]["attack"] + other.shield + self.damage
        other.shield = 0
        self.damage = 0
        self.energy += self.stats["normal"]["energy"]
        self.health += self.stats["normal"]["health"]
        self.shield += self.stats["normal"]["shield"]
        self.damage += self.stats["normal"]["damage"]
    def heal(self, other):
        self.energy += self.stats["heal"]["energy"]
        self.health += self.stats["heal"]["health"]
        self.shield += self.stats["heal"]["shield"]
        self.damage += self.stats["heal"]["damage"]
    def rest(self, other):
        self.energy += self.stats["rest"]["energy"]
        self.health += self.stats["rest"]["health"]
        self.shield += self.stats["rest"]["shield"]
        self.damage += self.stats["rest"]["damage"]



class Game:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.switch = bool(random.randint(0,1))
        self.switch = 0

    async def move(self, channel):
        def check(m):
            if m.channel == channel and m.author == self.active.member:
                return True
            return False

        if self.switch == True:
            self.active = self.player1
            self.other = self.player2
        else:
            self.active = self.player2
            self.other = self.player1

        await channel.send(f"<@{self.active.member.id}> attacks!")
        validMoves = [x for x in moves if self.active.energy >= abs(self.active.stats[x]['energy'])] + ['rest']

        await channel.send(f"Choose from: {', '.join(validMoves)} (without command prefix)")

        move = await bot.wait_for("message", check=check)
        move = move.content.lower()

        if move == "give up":
            await channel.send(f"{self.other.name} wins!")
            return True

        if move not in validMoves:
            await channel.send(f"{self.active.name}, you've input an incorrect command, maybe even cheated and input one that requires too many energy\n"
                  f"As punishment, you'll skip your move for now. Although, you'll have 5 energy restored")
            self.active.energy += 5

        else:
            await channel.send(f"{self.active.name} uses {self.active.stats[move]['name']}")
            if move == "mask":
                self.active.mask(self.other)
            elif move == "normal":
                self.active.attack(self.other)
            elif move == "heal":
                self.active.heal(self.other)
            elif move == "rest":
                self.active.rest(self.other)

        if self.player1.health <= 0:
            self.player1.health = 0
        if self.player2.health <= 0:
            self.player2.health = 0

        card(self.player1)
        card(self.player2)
        get_concat_v(self.player1, self.player2)

        await channel.send(file=File(f'data/cards/{self.player1.name}-{self.player2.name}.jpg'))

        if self.player1.health == 0:
            await channel.send(f"{self.player2.name} wins!")
            return True
        if self.player2.health == 0:
            await channel.send(f"{self.player1.name} wins!")
            return True
        self.switch = 0 if self.switch == 1 else 1
        return False


async def gameTime(p1, e1, p2, e2, channel):
    game = Game(Player(p1.name, e1, p1), Player(p2.name, e2, p2))
    result = False
    while not result:
        result = await game.move(channel)
    return True


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(intents=Intents.all(), command_prefix="!")

@bot.command()
async def test(ctx):
    await ctx.channel.send("I live!")


@bot.command()
async def gameinfo(ctx):
    await ctx.channel.send(f"This is 2-man Bionicle step-by-step game (name is to be added)\n\n"
                           f"Rules:\n"
                           f"1. Two players confirm their participation by stating their element for the game.\n"
                           f"2. Players make their move one after another.\n"
                           f"Make sure to read what options you have. Writing move incorrectly or misspelling it will be punished.\n"
                           f"3. Players' stats are updated after each person's move.\n"
                           f"4. Each player can give up on their move by writing 'give up'.\n"
                           f"5. The game is ended as soon as someone's health reaches zero.\n\n"
                           f"Have fun!")


@bot.command()
async def game(ctx):
    def check(m):
        if m.channel == ctx.channel:
                return True
        return False

    await ctx.channel.send("Player 1, please send your element as confirmation. Please, choose from:\n"
                           f"Fire\nWater\nEarth\nStone\nAir\nIce")
    while True:
        m = await bot.wait_for("message", check=check)
        m.content = m.content.lower()
        if m.content in ["fire", "water", "earth", "stone", "air", "ice"]:
            await m.channel.send(f"Player 1 confirmed: {m.author}, {m.content}")
            avatar = m.author.display_avatar.url
            data = requests.get(avatar).content
            with open(f"data/avatar/{m.author.name}.jpg", 'wb') as handler:
                handler.write(data)
            break
    player1 = m.author
    el1 = m.content.lower()

    await ctx.channel.send(f"Player 2, please send your element as confirmation. Please, choose from:\n"
                           f"Fire\nWater\nEarth\nStone\nAir\nIce")
    while True:
        m = await bot.wait_for("message", check=check)
        m.content = m.content.lower()
        if m.content in ["fire", "water", "earth", "stone", "air", "ice"]:
            await m.channel.send(f"Player 2 confirmed: {m.author}, {m.content}")
            avatar = m.author.display_avatar.url
            data = requests.get(avatar).content
            with open(f"data/avatar/{m.author.name}.jpg", 'wb') as handler:
                handler.write(data)
            break
    player2 = m.author
    el2 = m.content.lower()

    await gameTime(player1, el1, player2, el2, ctx.channel)



bot.run(TOKEN)
