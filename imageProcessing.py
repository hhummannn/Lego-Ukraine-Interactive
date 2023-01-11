from PIL import Image, ImageDraw, ImageFont
from style import color


def addBars(card, player):
    paint = ImageDraw.Draw(card)
    paint.rectangle( [(15, 130), (15 + player.health * 2, 145)], fill="#00A300", outline="green")
    # paint.rectangle( [(15, 130), (15 + 100*2, 145)], fill="#90EE90", outline="green")
    paint.rectangle([(15, 175), (15 + player.energy * 2, 190)], fill="#880ED4", outline="purple")
    # paint.rectangle([(15, 175), (15 + 100 * 2, 190)], fill="#880ED4", outline="purple")
    paint.rectangle([(15, 220), (15 + player.shield * 2, 235)], fill="#2E2EFF", outline="blue")
    # paint.rectangle([(15, 220), (15 + 0 * 2, 235)], fill="#2E2EFF", outline="blue")
    paint.rectangle([(15, 265), (15 + player.damage * 2, 280)], fill="#FF2E2E", outline="red")
    # paint.rectangle([(15, 265), (15 + 0 * 2, 280)], fill="#FF2E2E", outline="red")

def addText(card, player):
    text = ImageDraw.Draw(card)
    font = ImageFont.truetype('data/fonts/nick.ttf', size=30)
    text.text((110, 10), player.name, fill=color[f"{player.element}"], font=font)
    # text.text((110, 10), "Hhummann", fill=color["air"], font=font)

    font = ImageFont.truetype('data/fonts/nick.ttf', size=15)
    text.text((15, 110), "Health", fill=color[f"{player.element}"], font=font)
    text.text((15, 155), "Energy", fill=color[f"{player.element}"], font=font)
    text.text((15, 200), "Shield", fill=color[f"{player.element}"], font=font)
    text.text((15, 245), "Damage", fill=color[f"{player.element}"], font=font)
    font = ImageFont.truetype('data/fonts/nick.ttf', size=11)
    text.text((17, 132), f"{player.health}", fill=color[f"{player.element}"], font=font)
    text.text((17, 177), f"{player.energy}", fill=color[f"{player.element}"], font=font)
    text.text((17, 222), f"{player.shield}", fill=color[f"{player.element}"], font=font)
    text.text((17, 267), f"{player.damage}", fill=color[f"{player.element}"], font=font)


def card(player):
    bg = Image.open(f'data/bg/{player.element}-bg.jpg')
    avatar = Image.open(f'data/avatar/{player.name}.jpg')
    # bg = Image.open(f'data/bg/air-bg.jpg')
    # avatar = Image.open(f'data/avatar/Hhummann.jpg')

    card = bg.copy()
    addBars(card, player)
    addText(card, player)

    card.paste(avatar.resize([100, 100]), (0, 0))

    card.save(f'data/cards/{player.name}.jpg', quality=95)
    # card.save(f'data/cards/Hhummann.jpg', quality=95)


def get_concat_v(p1, p2):
    merge = Image.new('RGB', (541, 680))
    i1 = Image.open(f'data/cards/{p1.name}.jpg')
    i2 = Image.open(f'data/cards/{p2.name}.jpg')
    merge.paste(i1, (0, 0))
    merge.paste(i2, (0, 340))
    merge.save(f'data/cards/battle.jpg', quality=95)


