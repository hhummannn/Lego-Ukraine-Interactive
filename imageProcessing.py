from PIL import Image, ImageDraw, ImageFont
from style import color


def addBars(card, player):
    paint = ImageDraw.Draw(card)
    paint.rectangle([(15, 130), (15 + player.health * 2, 150)], fill="#00A300", outline="green")
    paint.rectangle([(15, 180), (15 + player.energy * 2, 200)], fill="#880ED4", outline="purple")
    paint.rectangle([(15, 230), (15 + player.shield * 2, 250)], fill="#2E2EFF", outline="blue")
    paint.rectangle([(15, 280), (15 + player.damage * 2, 300)], fill="#FF2E2E", outline="red")

def addText(card, player):
    text = ImageDraw.Draw(card)
    font = ImageFont.truetype('data/fonts/nick.ttf', size=30)
    text.text((110, 10), player.name, fill=color[f"{player.element}"], font=font)

    font = ImageFont.truetype('data/fonts/nick.ttf', size=15)
    text.text((15, 110), "Health", fill=color[f"{player.element}"], font=font)
    text.text((15, 160), "Energy", fill=color[f"{player.element}"], font=font)
    text.text((15, 210), "Shield", fill=color[f"{player.element}"], font=font)
    text.text((15, 260), "Damage", fill=color[f"{player.element}"], font=font)
    font = ImageFont.truetype('data/fonts/nick.ttf', size=15)
    text.text((17, 130), f"{player.health}", fill=color[f"{player.element}"], font=font)
    text.text((17, 180), f"{player.energy}", fill=color[f"{player.element}"], font=font)
    text.text((17, 230), f"{player.shield}", fill=color[f"{player.element}"], font=font)
    text.text((17, 280), f"{player.damage}", fill=color[f"{player.element}"], font=font)


def card(player):
    bg = Image.open(f'data/bg/{player.element}-bg.jpg')
    avatar = Image.open(f'data/avatar/{player.name}.jpg')

    card = bg.copy()
    addBars(card, player)
    addText(card, player)

    card.paste(avatar.resize([100, 100]), (0, 0))

    card.save(f'data/cards/{player.name}.jpg', quality=95)


def get_concat_v(p1, p2):
    merge = Image.new('RGB', (541, 680))
    i1 = Image.open(f'data/cards/{p1.name}.jpg')
    i2 = Image.open(f'data/cards/{p2.name}.jpg')
    merge.paste(i1, (0, 0))
    merge.paste(i2, (0, 340))
    merge.save(f'data/cards/{p1.name}-{p2.name}.jpg', quality=95)


