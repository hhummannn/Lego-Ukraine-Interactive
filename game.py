from imageProcessing import card, merge
from stats import elements
import random
from discord import File


moves = ["🎭 - mask", "🤜 - normal", "☕ - heal"]
valid_moves = ["mask", "normal", "heal", "rest", "give up"]


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
        await channel.send(
            f"<@{self.member.id}> abilities:\n"
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
        self.switch = bool(random.randint(0, 1))
        self.switch = 0

    def Switch(self):
        if self.switch:
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
    async def move(self, channel, bot):
        # for move receive
        def check(reaction, user):
            return (
                str(reaction) in ["🎭", "🤜", "☕", "🧘", "🏳"]
                and user.name == self.active.name
            )

        self.Switch()

        # player move choice
        await channel.send(f"<@{self.active.member.id}> attacks!")
        availableMoves = [
            mv
            for mv in moves
            if self.active.energy >= abs(self.active.stats[mv[4:]]["energy"])
        ] + ["🧘 - rest", "🏳 - give up"]
        choiceMessage = await channel.send(f"Choose from: {', '.join(availableMoves)}")

        for emoji in [mv[0] for mv in availableMoves]:
            await choiceMessage.add_reaction(emoji)

        reaction, user = await bot.wait_for("reaction_add", check=check)

        moves_ = {"🎭": "mask", "🤜": "normal", "☕": "heal", "🧘": "rest", "🏳": "give up"}

        move = moves_[str(reaction)]

        # give up
        if move == "give up":
            await channel.send(f"{self.other.name} wins!")
            return True

        # if invalid move
        if move not in [mv[4:] for mv in availableMoves]:
            await channel.send(
                f"{self.active.name}, you seem to have cheated and tried a move that requires too many energy\n"
                f"As punishment, you'll skip your move. You'll have 5 energy restored"
            )
            self.active.energy += 5
        # if valid
        else:
            await channel.send(
                f"{self.active.name} uses {self.active.stats[move]['name']}"
            )
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
        await channel.send(
            file=File(f"data/cards/{self.player1.name}-{self.player2.name}.jpg")
        )

        # win check
        return await self.win(channel)
