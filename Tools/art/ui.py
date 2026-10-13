"""UI art: logo lettering, digitised portraits, panels."""
import math

from PIL import Image, ImageDraw, ImageEnhance, ImageOps

import font
from bg import Art
from px import at, dilate, m_sub, rgb

FIRE = ["#fcf8a0", "#fcd800", "#f8a800", "#f87800", "#e83800", "#b81818"]

# crop centre + width in source pixels (4:5 portrait)
PORTRAITS = [
    ("miranda", "miranda.webp", (490, 185), 290), ("julia", "julia.jpg", (392, 140), 150),
    ("thatcher", "thatcher.jpg", (232, 78), 92), ("witch", "witch.jpg", (1500, 720), 560),
    ("donna", "donna.jpg", (322, 104), 112), ("aloysius", "aloysius.jpg", (812, 235), 330),
]


def _flame(base, top, height, colours=FIRE, edge="#281048", glow="#3050e8"):
    """Colour a lettering mask: fire gradient, dark edge, blue drop."""
    w, h = base.size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    fat = dilate(dilate(base, True), True)
    out.paste(rgb(glow) + (255,), mask=at(fat, -2, -3))
    out.paste(rgb(edge) + (255,), mask=fat)
    n = len(colours)
    for i, c in enumerate(colours):
        y0, y1 = top + height * i // n, top + height * (i + 1) // n
        band = Image.new("L", (w, h), 0)
        band.paste(base.crop((0, y0, w, y1)), (0, y0))
        out.paste(rgb(c) + (255,), mask=band)
    # specular nick on the top-left of every stroke
    out.paste(rgb("#fcfcfc") + (255,), mask=m_sub(m_sub(base, at(base, 0, -1)), at(base, 1, 0)))
    return out


def logo_line(text, scale=5, slant=True, colours=FIRE, edge="#281048", glow="#3050e8"):
    """Chunky italic gradient lettering with a dark edge and a blue drop."""
    m = font.text_mask(text, bold=True, scale=scale, spacing=1)
    pad = 6
    w, h = m.width + pad * 2 + (7 if slant else 0), m.height + pad * 2
    base = Image.new("L", (w, h), 0)
    if slant:
        for row in range(7):                       # shear: one pixel per glyph row
            strip = m.crop((0, row * scale, m.width, (row + 1) * scale))
            base.paste(strip, (pad + (6 - row), pad + row * scale))
    else:
        base.paste(m, (pad, pad))
    return _flame(base, pad, m.height, colours, edge, glow)


def portrait(i, size=(40, 50), colours=20):
    """Digitised-photo portrait, arcade style: tiny + hard palette."""
    _, fn, (cx, cy), w = PORTRAITS[i]
    src = Image.open("Assets/Portraits/" + fn).convert("RGB")
    h = w * size[1] // size[0]
    box = [cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2]
    if box[1] < 0:
        box[3] -= box[1]
        box[1] = 0
    im = ImageOps.autocontrast(src.crop(box).resize(size, Image.LANCZOS), cutoff=1)   # rescue dark stills
    im = ImageEnhance.Contrast(im).enhance(1.2)
    im = ImageEnhance.Color(im).enhance(1.5)
    im = ImageEnhance.Brightness(im).enhance(1.12)
    return im.quantize(colours, method=Image.MEDIANCUT, dither=Image.NONE).convert("RGB")


# ---- "MERYL KOMBAT": tall wedge-serif caps, after the Mortal Kombat logo
MK = {
    "M": ["X.......X", "XX.....XX", "XXX...XXX", "XXXX.XXXX", "XX.XXX.XX", "XX..X..XX", "XX.....XX",
          "XX.....XX", "XX.....XX", "XX.....XX", "XXX...XXX"],
    "E": ["XXXXXXX", "XX....X", "XX.....", "XX.....", "XXXXX..", "XX.....", "XX.....", "XX.....", "XX.....",
          "XX....X", "XXXXXXX"],
    "R": ["XXXXXX..", "XX...XX.", "XX...XX.", "XX...XX.", "XXXXXX..", "XX.XX...", "XX..XX..", "XX..XX..",
          "XX...XX.", "XX...XX.", "XXX..XXX"],
    "Y": ["XX.....XX", "XX.....XX", ".XX...XX.", ".XX...XX.", "..XX.XX..", "...XXX...", "...XX....",
          "...XX....", "...XX....", "...XX....", "..XXXX..."],
    "L": ["XXX....", "XX.....", "XX.....", "XX.....", "XX.....", "XX.....", "XX.....", "XX.....", "XX.....",
          "XX....X", "XXXXXXX"],
    "K": ["XXX..XXX", "XX...XX.", "XX..XX..", "XX.XX...", "XXXX....", "XXXX....", "XX.XX...", "XX..XX..",
          "XX..XX..", "XX...XX.", "XXX..XXX"],
    "O": ["..XXXX..", ".XX..XX.", "XX....XX", "XX....XX", "XX....XX", "XX....XX", "XX....XX", "XX....XX",
          "XX....XX", ".XX..XX.", "..XXXX.."],
    "B": ["XXXXXX..", "XX...XX.", "XX...XX.", "XX...XX.", "XXXXXX..", "XX...XX.", "XX....XX", "XX....XX",
          "XX....XX", "XX...XX.", "XXXXXX.."],
    "A": ["....X....", "...XXX...", "...XXX...", "..XX.XX..", "..XX.XX..", ".XX...XX.", ".XXXXXXX.",
          ".XX...XX.", "XX.....XX", "XX.....XX", "XXX...XXX"],
    "T": ["XXXXXXXX", "X..XX..X", "...XX...", "...XX...", "...XX...", "...XX...", "...XX...", "...XX...",
          "...XX...", "...XX...", "..XXXX.."],
}
MK_GOLD = ["#fcf8c0", "#fce868", "#f8c820", "#f0a010", "#d87808", "#b05008", "#803008"]


def kombat_logo(text="MERYL KOMBAT", scale=2):
    """Chiselled gold caps on a black bar with blood-red rules."""
    w = sum(len(MK[c][0]) + 1 if c != " " else 6 for c in text) - 1
    m = Image.new("L", (w, 11), 0)
    p, x = m.load(), 0
    for c in text:
        if c == " ":
            x += 6
            continue
        for yy, row in enumerate(MK[c]):
            for xx, b in enumerate(row):
                if b == "X":
                    p[x + xx, yy] = 255
        x += len(MK[c][0]) + 1
    m = m.resize((w * scale, 11 * scale), Image.NEAREST)
    pad = 5
    W, H = m.width + pad * 2 + 14, m.height + pad * 2
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    a = Art(W, H, mode="RGBA")
    a.im = out
    a.d, a.p = ImageDraw.Draw(out), out.load()
    a.rect(0, 2, W, H - 2, "#0c0810")
    a.rect(0, 0, W, 2, "#b01818")
    a.rect(0, H - 2, W, H, "#b01818")
    a.rect(0, 2, W, 3, "#f8c820")
    a.rect(0, H - 3, W, H - 2, "#f8c820")
    base = Image.new("L", (W, H), 0)
    base.paste(m, (pad + 7, pad))
    out.paste(rgb("#701010") + (255,), mask=at(base, -1, -2))          # blood drop
    out.paste(rgb("#200808") + (255,), mask=m_sub(dilate(base, True), base))
    n = len(MK_GOLD)
    for i, c in enumerate(MK_GOLD):
        y0, y1 = pad + m.height * i // n, pad + m.height * (i + 1) // n
        band = Image.new("L", (W, H), 0)
        band.paste(base.crop((0, y0, W, y1)), (0, y0))
        out.paste(rgb(c) + (255,), mask=band)
    out.paste(rgb("#fffff0") + (255,), mask=m_sub(m_sub(base, at(base, 0, -1)), at(base, -1, 0)))
    return out


def announce(text, scale=4):
    return logo_line(text, scale)


def title_bg():
    a = Art(384, 216)
    a.vgrad(0, 0, 384, 216, ["#080828", "#101050", "#2020a0", "#3048d8"])
    for i in range(0, 384, 2):
        if (i * 37) % 23 == 0:
            a.dot(i, (i * 53) % 110, "#fcfcfc")
    return a.im


def title_logo():
    l1, l2 = logo_line("STREEP", 6), logo_line("FIGHTER", 6)
    w = max(l1.width, l2.width) + 20
    out = Image.new("RGBA", (w, 96), (0, 0, 0, 0))
    out.alpha_composite(l1, ((w - l1.width) // 2 - 10, 0))
    out.alpha_composite(l2, ((w - l2.width) // 2 + 10, 50))
    return out


def select_bg():
    a = Art(384, 216)
    a.vgrad(0, 0, 384, 216, ["#101050", "#182088", "#2838c0"])
    for y in range(40, 216, 12):
        a.rect(0, y, 384, y + 1, "#1c2ca0")
    return a.im


def panel(w, h, edge="#fcfcfc", fill="#181028"):
    a = Art(w, h, mode="RGBA")
    a.rect(0, 0, w, h, edge)
    a.rect(1, 1, w - 1, h - 1, fill)
    return a.im


def round_marker(won):
    a = Art(9, 9, mode="RGBA")
    a.ellipse(0, 0, 9, 9, "#181028")
    a.ellipse(1, 1, 8, 8, "#f8b800" if won else "#484468")
    if won:
        a.rect(2, 2, 4, 4, "#fcf8a0")
    return a.im


STAR = ["....X....", "....X....", "...XXX...", "XXXXXXXXX", ".XXXXXXX.", "..XXXXX..", "..XXXXX..",
        ".XXX.XXX.", ".X.....X."]


def star(lit):
    """Difficulty star for the title screen's CPU LEVEL row (SF2's level stars)."""
    m = Image.new("L", (11, 11), 0)
    p = m.load()
    for y, row in enumerate(STAR):
        for x, ch in enumerate(row):
            if ch == "X":
                p[x + 1, y + 1] = 255
    out = Image.new("RGBA", (11, 11), (0, 0, 0, 0))
    out.paste(rgb("#181028") + (255,), mask=dilate(m))
    rows = ["#fcf8a0", "#fcf8a0", "#fcd800", "#fcd800", "#f8a800", "#f8a800", "#f87800", "#f87800", "#e83800"] \
        if lit else ["#585478"] * 9
    for y, c in enumerate(rows):
        band = Image.new("L", (11, 11), 0)
        band.paste(m.crop((0, y + 1, 11, y + 2)), (0, y + 1))
        out.paste(rgb(c) + (255,), mask=band)
    return out


# ---- app icon: the title lettering cut down to a monogram
ICON_SF = [
    ".XXXXXX.XXXXXXX",
    "XXXXXXX.XXXXXXX",
    "XX......XX.....",
    "XXXXXX..XX.....",
    ".XXXXXX.XXXXXX.",
    ".....XX.XXXXXX.",
    ".....XX.XX.....",
    "XXXXXXX.XX.....",
    "XXXXXX..XX.....",
]


def app_icon():
    """64x64 icon tile: fiery italic "SF" on a blue sunburst."""
    n, scale, pad = 64, 3, 6
    a = Art(n, n)
    for y in range(n):
        for x in range(n):
            t = math.atan2(y - 35, x - 32) / (2 * math.pi) * 16
            a.p[x, y] = a.c("#141460" if int(math.floor(t)) & 1 else "#0c0c38")
    a.dither(0, 0, n, 18, "#080828", 0.5)
    for i in range(0, 400, 3):
        if (i * 37) % 23 == 0:
            a.dot((i * 29) % n, (i * 53) % 16, "#fcfcfc")
    rows, cols = len(ICON_SF), len(ICON_SF[0])
    m = Image.new("L", (cols, rows), 0)
    p = m.load()
    for yy, row in enumerate(ICON_SF):
        for xx, b in enumerate(row):
            if b == "X":
                p[xx, yy] = 255
    m = m.resize((cols * scale, rows * scale), Image.NEAREST)
    slant = (m.height - 1) // 5
    base = Image.new("L", (m.width + slant + pad * 2, m.height + pad * 2), 0)
    for y in range(m.height):                          # shear: one pixel every five rows
        base.paste(m.crop((0, y, m.width, y + 1)), (pad + slant - y // 5, pad + y))
    letters = _flame(base, pad, m.height)
    a.paste(letters, ((n - letters.width) // 2 + 1, (n - letters.height) // 2))
    return a.im


def mac_icon(tile, size=1024):
    """macOS wants its own shape: a rounded square inside a transparent margin."""
    inner = size * 824 // 1024
    art = tile.convert("RGBA").resize((inner, inner), Image.NEAREST)
    m = Image.new("L", (inner * 2, inner * 2), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, inner * 2 - 1, inner * 2 - 1], radius=int(inner * 2 * 0.225), fill=255)
    art.putalpha(m.resize((inner, inner), Image.LANCZOS))
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.alpha_composite(art, ((size - inner) // 2,) * 2)
    return out


def ko_badge():
    a = Art(40, 14, mode="RGBA")
    a.rect(0, 0, 40, 14, "#fcfcfc")
    a.rect(1, 1, 39, 13, "#181028")
    a.text((20, 3), "KO", "#f83800", bold=True, spacing=2, align="center",
           gradient=["#fcd800", "#f87800", "#d82800"])
    return a.im


def roster_card(i, sprite, name):
    """README roster card: framed portrait beside the fighter's idle sprite."""
    w, h = 176, 126
    a = Art(w, h)
    a.vgrad(0, 0, w, h, ["#101050", "#182088", "#2838c0"])
    for y in range(10, h, 12):
        a.rect(0, y, w, y + 1, "#1c2ca0")
    a.rect(6, 6, 90, 110, "#fcfcfc")
    a.rect(7, 7, 89, 109, "#181028")
    a.paste(portrait(i, (80, 100), 28), (8, 8))
    # sprite stands on a mesh shadow, feet on a common baseline
    import fx
    import rig
    base_y, cx = 110, 134
    sh = fx.shadow()
    a.paste(sh, (cx - sh.width // 2, base_y - 3))
    a.paste(sprite, (cx - rig.ORG[0], base_y - rig.ORG[1]))
    a.text((w // 2, 114), name, "#fcd800", bold=True, align="center", outline="#181028")
    return a.im


def title_screen():
    """Mockup composite (the game assembles the same pieces itself)."""
    a = Art(384, 216)
    a.paste(title_bg(), (0, 0))
    logo, kom = title_logo(), kombat_logo()
    a.paste(logo, ((384 - logo.width) // 2, 14))
    a.paste(kom, ((384 - kom.width) // 2, 116))
    a.text((192, 160), "VS PLAYER", "#fcd800", bold=True, align="center", outline="#181028")
    a.text((192, 174), "VS CPU", "#fcfcfc", bold=True, align="center", outline="#181028")
    a.text((150, 160), ">", "#f83800", bold=True, outline="#181028")
    a.text((192, 200), "PUSH START", "#fcfcfc", align="center", shadow="#181028")
    return a.im
def select_screen(sprites):
    a = Art(384, 216)
    a.vgrad(0, 0, 384, 216, ["#101050", "#182088", "#2838c0"])
    for y in range(40, 216, 12):                   # floor grid
        a.rect(0, y, 384, y + 1, "#1c2ca0")
    a.text((192, 8), "PLAYER SELECT", "#fcfcfc", bold=True, scale=2, align="center", outline="#181028",
           gradient=["#fcf8a0", "#fcd800", "#f87800"])
    names = ["MIRANDA", "JULIA", "THATCHER", "THE WITCH", "DONNA", "ALOYSIUS"]
    gx, gy = 192 - 66, 104
    for i in range(6):
        x, y = gx + (i % 3) * 44, gy + (i // 3) * 54
        a.rect(x - 2, y - 2, x + 42, y + 52, "#181028")
        a.paste(portrait(i), (x, y))
    for sel, col, tag in ((0, "#3880f8", "1P"), (2, "#f83828", "2P")):
        x, y = gx + (sel % 3) * 44, gy + (sel // 3) * 54
        a.frame(x - 3, y - 3, x + 43, y + 53, col, 2)
        a.frame(x - 4, y - 4, x + 44, y + 54, "#fcfcfc", 1)
        a.rect(x - 4, y - 12, x + 12, y - 3, col)
        a.text((x - 2, y - 11), tag, "#fcfcfc", bold=True)
    for sel, x, flip in ((0, 8, False), (2, 384 - 8 - 80, True)):
        big = portrait(sel, (80, 100), 28)
        if flip:
            big = big.transpose(Image.FLIP_LEFT_RIGHT)
        a.rect(x - 2, 38, x + 82, 142, "#fcfcfc")
        a.rect(x - 1, 39, x + 81, 141, "#181028")
        a.paste(big, (x, 40))
        a.text((x + 40, 148), names[sel], "#fcd800", bold=True, align="center", outline="#181028")
    for (img, x, flip) in sprites:
        if flip:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        a.paste(img, (x, 216 - 128 + 4))
    return a.im
