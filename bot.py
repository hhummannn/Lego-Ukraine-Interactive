import os
import random
import requests
from discord import Intents, File
from discord.ext import commands
from dotenv import load_dotenv
from stats import elements
from imageProcessing import card, merge, initInfo

moves = ["🎭 - mask", "🤜 - normal", "☕ - heal"]
valid_moves = ["mask", "normal", "heal", "rest", "give up"]



# bot login
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
bot = commands.Bot(intents=Intents.all(), command_prefix="!",help_command=None)


# player class
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


    async def info(self, channel):
        await channel.send(f"<@{self.member.id}> abilities:\n"
                           f"1. Mask - {self.stats['mask']['name']}: {self.stats['mask']['description']}\n"
                           f"2. Normal attack - {self.stats['normal']['name']}: {self.stats['normal']['description']}\n"
                           f"3. Healing ability - {self.stats['heal']['name']}: {self.stats['heal']['description']}\n"
                           f"4. Resting - {self.stats['rest']['name']}: {self.stats['rest']['description']}\n"
                           )


    # are different because all change different states
    def mask(self, other):
        other.health += self.stats["mask"]["attack"]
        self.energy += self.stats["mask"]["energy"]
        self.health += self.stats["mask"]["health"]
        self.shield += self.stats["mask"]["shield"]
        self.damage += self.stats["mask"]["damage"]


    def attack(self, other):
        other.health += self.stats["normal"]["attack"] + other.shield - self.damage
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




# game class
class Game:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.switch = bool(random.randint(0,1))
        self.switch = 0


    def Switch(self):
        if self.switch == True:
            self.active = self.player1
            self.other = self.player2
        else:
            self.active = self.player2
            self.other = self.player1


    def hit(self, move):
        if move == "mask":
            self.active.mask(self.other)
        elif move == "normal":
            self.active.attack(self.other)
        elif move == "heal":
            self.active.heal(self.other)
        elif move == "rest":
            self.active.rest(self.other)


    async def win(self, channel):
        if self.player1.health == 0:
            await channel.send(f"{self.player2.name} wins!")
            return True
        if self.player2.health == 0:
            await channel.send(f"{self.player1.name} wins!")
            return True
        self.switch = 0 if self.switch == 1 else 1
        return False


    # player move
    async def move(self, channel):
        # for move receive
        def check(reaction, user):
            return str(reaction) in ["🎭", "🤜", "☕", "🧘", "🏳"] and user.name == self.active.name

        self.Switch()

        # player move choice
        await channel.send(f"<@{self.active.member.id}> attacks!")
        availableMoves = [mv for mv in moves if self.active.energy >= abs(self.active.stats[mv[4:]]['energy'])] + ['🧘 - rest', '🏳 - give up']
        choiceMessage = await channel.send(f"Choose from: {', '.join(availableMoves)}")

        for emoji in [mv[0] for mv in availableMoves]:
            await choiceMessage.add_reaction(emoji)

        reaction, user = await bot.wait_for('reaction_add', check = check)

        moves_ = {
            "🎭" : "mask",
            "🤜" : "normal",
            "☕" : "heal",
            "🧘" : "rest",
            "🏳" : "give up"
        }

        move = moves_[str(reaction)]


        # give up
        if move == "give up":
            await channel.send(f"{self.other.name} wins!")
            return True


        # if invalid move
        if move not in [mv[4:] for mv in availableMoves]:
            await channel.send(f"{self.active.name}, you seem to have cheated and tried a move that requires too many energy\n"
                  f"As punishment, you'll skip your move. You'll have 5 energy restored")
            self.active.energy += 5
        # if valid
        else:
            await channel.send(f"{self.active.name} uses {self.active.stats[move]['name']}")
            self.hit(move)

        # zero health check
        if self.player1.health <= 0:
            self.player1.health = 0
        if self.player2.health <= 0:
            self.player2.health = 0

        # make visuals
        card(self.player1)
        card(self.player2)
        merge(self.player1, self.player2)

        # send visuals
        await channel.send(file=File(f'data/cards/{self.player1.name}-{self.player2.name}.jpg'))

        # win check
        return await self.win(channel)

# game switch
async def gameTime(p1, e1, p2, e2, channel):
    first = Player(p1.name, e1, p1)
    await first.info(channel)
    second = Player(p2.name, e2, p2)
    await second.info(channel)
    game = Game(first, second)
    result = False
    while not result:
        result = await game.move(channel)
    return True


async def playerEntry(ctx):
    def check(reaction, user):
        return str(reaction) in ["🔥", "💧", "🌄", "🪨", "🌪", "❄"] \
               and user.id != bot.user.id \
               and reaction.message.content == choiceMessage.content

    choiceMessage = await ctx.channel.send("Next player, please send your element as confirmation. Please, react with one from:\n"
                           f"Fire - 🔥\nWater - 💧\nEarth - 🌄\nStone - 🪨\nAir - 🌪\nIce - ❄")
    for emoji in ["🔥", "💧", "🌄", "🪨", "🌪", "❄"]:
        await choiceMessage.add_reaction(emoji)

    reaction, user = await bot.wait_for('reaction_add', timeout = 1.0, check = check)

    els = {
        "🔥" : "fire",
        "💧": "water",
        "🌄": "earth",
        "🪨": "stone",
        "🌪": "air",
        "❄": "ice",
    }
    await ctx.channel.send(f"Player confirmed: {user.name}, {els[str(reaction)]}")
    avatar = user.display_avatar.url
    data = requests.get(avatar).content
    with open(f"data/avatar/{user.name}.jpg", 'wb') as handler:
        handler.write(data)
    return user, els[str(reaction)]






# commands start here
@bot.command()
async def help(ctx):
    await ctx.channel.send(f"This is Lego Ukraine Interactive bot (LUI), that is created for Lego Ukraine discord server\n"
                           f"The bot is in development, so wait for updates!\n\n"
                           f"Available commands are:\n\n"
                           f"!help - show this message\n"
                           f"!test - check if the bot is alive (not guaranteed for now...)\n"
                           f"!element - get information about a specific element of Bionicle Game\n"
                           f"!gameinfo - get information and rules about Bionicle 1v1 game\n"
                           f"!game - start the game")


@bot.command()
async def test(ctx):
    await ctx.channel.send("I live!")


@bot.command()
async def element(ctx):
    def check(reaction, user):
        return str(reaction) in ["🔥", "💧", "🌄", "🪨", "🌪", "❄"] and user == ctx.author

    choiceMessage = await ctx.channel.send("Choose element to get info about:\n"
                           f"Fire - 🔥\nWater - 💧\nEarth - 🌄\nStone - 🪨\nAir - 🌪\nIce - ❄")
    for emoji in ["🔥", "💧", "🌄", "🪨", "🌪", "❄"]:
        await choiceMessage.add_reaction(emoji)
    while True:
        reaction, user = await bot.wait_for("reaction_add", check=check)
        break

    els = {
        "🔥" : "fire",
        "💧": "water",
        "🌄": "earth",
        "🪨": "stone",
        "🌪": "air",
        "❄": "ice",
    }
    elinfo = els[str(reaction)]
    await ctx.channel.send(f"{elinfo[0].upper() + elinfo[1:]} abilities:\n"
                       f"1. Mask - {elements[elinfo]['mask']['name']}: {elements[elinfo]['mask']['description']}\n\n"
                       f"2. Normal attack - {elements[elinfo]['normal']['name']}: {elements[elinfo]['normal']['description']}\n\n"
                       f"3. Healing ability - {elements[elinfo]['heal']['name']}: {elements[elinfo]['heal']['description']}\n\n"
                       f"4. Resting - {elements[elinfo]['rest']['name']}: {elements[elinfo]['rest']['description']}\n\n"
                       )


@bot.command()
async def gameinfo(ctx):
    await ctx.channel.send(f"This is 2-man Bionicle inspired step-by-step game (name to be added)\n\n"
                           f"Rules:\n"
                           f"1. Two players confirm their participation by stating their element for the game.\n"
                           f"2. Players make their move one after another.\n"
                           f"Make sure to read what options you have. Trying to make a move that takes more stamina than you have will be punished.\n"
                           f"3. Players' stats are updated after each person's move.\n"
                           f"4. The game is ended as soon as someone's health reaches zero.\n\n"
                           f"Have fun!")




@bot.command()
async def game(ctx):
    initInfo()
    await ctx.channel.send(file=File("data/cards/info.jpg"))

    player1, el1 = await playerEntry(ctx)
    player2, el2 = await playerEntry(ctx)

    await gameTime(player1, el1, player2, el2, ctx.channel)



bot.run(TOKEN)
