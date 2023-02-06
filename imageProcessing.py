from PIL import Image, ImageDraw, ImageFont
from style import color
from stats import elements


def infoPrint(card, element):
    e = elements
    text = ImageDraw.Draw(card)

    font = ImageFont.truetype('data/fonts/nick.ttf', size=35)
    text.text((15, 10), element.upper(), fill=color[f"{element}"], font=font)

    font = ImageFont.truetype('data/fonts/nick.ttf', size=15)
    for y, t in zip([110, 160, 210, 260, 310], ["Shield:", "Charge damage:", "Attack:", "Energy:", "Health:"]):
        text.text((15, y), t, fill=color[f"{element}"], font=font)

    for x, t in zip([170, 270, 370, 470], ["Mask", "Normal", "Heal", "Rest"]):
        text.text((x, 70), t, fill=color[f"{element}"], font=font)

    font = ImageFont.truetype('data/fonts/nick.ttf', size=18)
    for x, n in zip([170, 270, 370, 470], ["mask", "normal", "heal", "rest"]):
        for y, t in zip([110, 160, 210, 260, 310], [e[element][n]['shield'],
                                                   e[element][n]['damage'],
                                                   e[element][n]['attack'],
                                                   e[element][n]['energy'],
                                                   e[element][n]['health']]):
            text.text((x, y), f"{t}", fill=color[f"{element}"], font=font)

def infoCard(element):
    card = Image.open(f'data/bg/{element}-bg.jpg')

    card = card.copy()
    infoPrint(card, element)

    card.save(f'data/cards/{element}.jpg', quality=95)


def initInfo():
    for element in ["fire", "water", "earth", "stone", "air", "ice"]:
        infoCard(element)

    mergeInfo()


def mergeInfo():
    merge = Image.new('RGB', (1082, 1080))
    array = []
    for element in ["fire", "water", "earth", "stone", "air", "ice"]:
        array.append(Image.open(f"data/cards/{element}.jpg"))
    for i in range(6):
        merge.paste( array[i], ( (i%2)*541, (i%3)*360) )

    merge.save("data/cards/info.jpg")


def addBars(card, player):
    paint = ImageDraw.Draw(card)
    for y, l, t, c, o in zip([130, 180, 230, 280],
                       [150, 200, 250, 300],
                       [player.health, player.energy, player.shield, player.damage],
                       ["#00A300", "#880ED4", "#2E2EFF", "#FF2E2E"],
                       ["green", "purple", "blue", "red"]):
        paint.rectangle([(15, y), (15 + t * 2, l)], fill=c, outline=o)

def addText(card, player):
    text = ImageDraw.Draw(card)
    font = ImageFont.truetype('data/fonts/nick.ttf', size=30)
    text.text((110, 10), player.name, fill=color[f"{player.element}"], font=font)

    font = ImageFont.truetype('data/fonts/nick.ttf', size=15)
    for y, t in zip([110, 160, 210, 260], ["Health", "Energy", "Shield", "Damage"]):
        text.text((15, y), t, fill=color[f"{player.element}"], font=font)

    for y, s in zip([130, 180, 230, 280], [player.health, player.energy, player.shield, player.damage]):
        text.text((17, y), f"{s}", fill=color[f"{player.element}"], font=font)


def card(player):
    bg = Image.open(f'data/bg/{player.element}-bg.jpg')
    avatar = Image.open(f'data/avatar/{player.name}.jpg')

    card = bg.copy()
    addBars(card, player)
    addText(card, player)

    card.paste(avatar.resize([100, 100]), (0, 0))

    card.save(f'data/cards/{player.name}.jpg', quality=95)


def merge(p1, p2):
    merge = Image.new('RGB', (541, 720))
    i1 = Image.open(f'data/cards/{p1.name}.jpg')
    i2 = Image.open(f'data/cards/{p2.name}.jpg')
    merge.paste(i1, (0, 0))
    merge.paste(i2, (0, 360))
    merge.save(f'data/cards/{p1.name}-{p2.name}.jpg', quality=95)
