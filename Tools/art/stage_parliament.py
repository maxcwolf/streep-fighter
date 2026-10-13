"""HOUSE OF COMMONS - London, England.  Margaret Thatcher's stage.

The chamber seen from the floor, looking up its length at the Speaker's
chair.  Everything on the side walls is built in one-point perspective
from "chamber units" (1 unit = 1px on the back wall):

    X  lateral distance from the centre line
    Y  height above the carpet
    s  depth scale: 1.0 on the back wall, ~2.25 on the fight line

One half is painted (benches, MPs, galleries, wall) and mirrored with a
different crowd seed; the centre pieces (Speaker, Table, mace) go on top.
"""
import random

from PIL import Image, ImageDraw

from bg import BAYER, Art
from stages import FAR_W, STAGE_H, STAGE_W

VX, VY, H0 = 256, 110, 40          # vanishing point; floor is H0 below it at s=1
D0 = 170.0                         # camera distance from the back wall (units)
HALF = STAGE_W // 2

# ---- palette (main layer) -------------------------------------------------
DEEP = "#201834"
OAK_SH, OAK_DK, OAK_MID, OAK, OAK_HI = "#3c2440", "#5c3434", "#804c30", "#a46c38", "#cc9450"
GOLD_DK, GOLD, GOLD_HI = "#a86420", "#e8a830", "#fce078"
STN_DK, STN, STN_HI = "#7c5850", "#b88c64", "#e8c88c"
LEA_SH, LEA_DK, LEA, LEA_HI = "#183844", "#1c5040", "#2c6c48", "#3c8c58"
CAR1 = "#4c9c5c"
RED, RED_DK = "#c8383c", "#882444"
BLUE = "#4868b8"
CREAM, WIG, WIG_SH = "#f0e8c8", "#c8c4dc", "#8c88ac"
SK1, SK2, SK3, SK_SH = "#ecb48c", "#cc8c64", "#905c44", "#a86854"
NAVY, CHAR, PLUM, GREY = "#2c2c58", "#3c3854", "#4c3050", "#5c5c78"
TEAL = "#2c7c80"
BLONDE = "#d0a45c"

SUITS = [NAVY, NAVY, CHAR, CHAR, PLUM, GREY]
JACKETS = [RED_DK, TEAL, PLUM, GREY]
SKINS = [SK1, SK1, SK1, SK2, SK2, SK3]
HAIRS = [OAK_DK, OAK_DK, WIG_SH, WIG, DEEP, BLONDE, OAK_MID]
TIES = [RED, RED, BLUE, GOLD, RED_DK, TEAL]
DARK = {NAVY: DEEP, CHAR: DEEP, PLUM: DEEP, GREY: OAK_SH, RED_DK: OAK_SH, TEAL: LEA_SH, BLUE: NAVY,
        SK1: SK3, SK2: SK3, SK3: OAK_DK, SK_SH: OAK_DK, CREAM: WIG_SH, WIG: WIG_SH, WIG_SH: CHAR,
        BLONDE: OAK_MID, OAK_MID: OAK_DK, OAK_DK: OAK_SH, RED: RED_DK, GOLD: GOLD_DK}


def L(X, Y, s):
    """Chamber coords -> pixel in the LEFT half."""
    return (VX - X * s, VY + (H0 - Y) * s)


def depth(i, off=6.0, pitch=12.0):
    """Scale of the i-th seat along a bench (seats are `pitch` units apart)."""
    return D0 / (D0 - off - pitch * i)


def wedge(a, X, Y0, Y1, col, s0=1.0, s1=4.0):
    """Vertical surface at lateral X, between heights Y0..Y1, running toward the camera."""
    a.poly([L(X, Y0, s0), L(X, Y1, s0), L(X, Y1, s1), L(X, Y0, s1)], col)


def hwedge(a, X0, X1, Y, col, s0=1.0, s1=4.0):
    a.poly([L(X0, Y, s0), L(X1, Y, s0), L(X1, Y, s1), L(X0, Y, s1)], col)


def dither_poly(a, pts, col, level):
    m = Image.new("L", (a.w, a.h), 0)
    ImageDraw.Draw(m).polygon([(int(x), int(y)) for x, y in pts], fill=255)
    box = m.getbbox()
    if not box:
        return
    mp, col = m.load(), a.c(col)
    for y in range(box[1], box[3]):
        for x in range(box[0], box[2]):
            if mp[x, y] and level * 16 > BAYER[y & 3][x & 3] + 0.5:
                a.p[x, y] = col


# ---- people ---------------------------------------------------------------
def person(a, R, cx, by, s, w, dirn, dark=False, wave=False, th_u=14.0, ext=0, jeer=0.6):
    """Flat-pixel seated figure.  (cx, by) = centre / bottom of the visible bust,
    s = scale, w = shoulder width in px, dirn = +1 when facing right."""
    m = (lambda c: DARK.get(c, c)) if dark else (lambda c: c)
    woman = R.random() < 0.14
    suit = R.choice(JACKETS if woman else SUITS)
    skin, hair, tie = R.choice(SKINS), R.choice(HAIRS), R.choice(TIES)
    bald = (not woman) and R.random() < 0.22
    mouth = R.random() < jeer
    cx, by = int(round(cx)), int(round(by))
    hw, hh = max(5, int(round(5.2 * s))), max(6, int(round(6.2 * s)))
    th = max(4, int(round(th_u * s)))
    sy, x0 = by - th, cx - w // 2
    # torso
    big = w >= 12
    r = 2 if big else 1
    a.rect(x0 + r, sy, x0 + w - r, sy + 1, m(suit))
    a.rect(x0 + r - 1, sy + 1, x0 + w - r + 1, sy + 2, m(suit))
    a.rect(x0, sy + 2, x0 + w, by + ext, m(suit))
    sw = max(1, w // 7)
    bx = x0 if dirn > 0 else x0 + w - sw
    a.rect(bx, sy + 2, bx + sw, by + ext, m(DEEP))
    if big:                                     # sleeve seam on the near arm
        ax_ = x0 + w - 1 - w // 5 if dirn > 0 else x0 + w // 5
        a.rect(ax_, sy + int(4 * s), ax_ + 1, by + ext, m(DEEP))
    # collar + tie
    cw, chh = max(2, int(round(2.4 * s))), max(2, int(round(3.2 * s)))
    sx = cx - cw // 2 + dirn * int(round(0.8 * s))
    a.rect(sx, sy, sx + cw, sy + chh, m(CREAM))
    if not woman:
        tx = sx + (cw - 1) // 2
        a.rect(tx, sy + 1, tx + max(1, cw // 3), sy + chh + max(1, int(s)), m(tie))
    # raised arm + order paper (on the shoulder away from the face)
    hx = cx - hw // 2 + dirn * max(1, int(round(0.9 * s)))
    hy = sy - hh + 1
    if wave:
        aw = max(2, int(round(2.2 * s)))
        ax = x0 if dirn > 0 else x0 + w - aw
        top = hy - int(round(2 * s)) - R.randint(0, 2)
        pw, ph = max(4, int(round(4.4 * s))), max(5, int(round(6 * s)))
        px0, py0 = ax - (pw - aw) // 2, top - ph - aw + 2
        a.rect(px0, py0, px0 + pw, py0 + ph, CREAM)
        for ly in range(py0 + 1, py0 + ph - 1, 2):
            a.rect(px0 + 1, ly, px0 + pw - 1, ly + 1, WIG)
        a.rect(ax, top, ax + aw, sy + 3, m(suit))
        a.rect(ax, top, ax + aw, top + 1, m(CREAM))
        a.rect(ax, top - aw, ax + aw, top, m(skin))
    # head
    jaw = m(OAK_DK if skin == SK3 else SK_SH)
    if hw >= 8:
        a.rect(hx + 2, hy, hx + hw - 2, hy + hh, m(skin))
        a.rect(hx + 1, hy + 1, hx + hw - 1, hy + hh - 1, m(skin))
        a.rect(hx, hy + 2, hx + hw, hy + hh - 3, m(skin))
        a.rect(hx + 2, hy + hh - 1, hx + hw - 2, hy + hh, jaw)
        a.rect(cx - 1 + dirn, hy + hh, cx + 2 + dirn, sy + 1, jaw)       # neck
    else:
        a.rect(hx + 1, hy, hx + hw - 1, hy + hh, m(skin))
        a.rect(hx, hy + 1, hx + hw, hy + hh - 1, m(skin))
        a.rect(hx + 1, hy + hh - 1, hx + hw - 1, hy + hh, jaw)
    t, bw = max(1, int(round(1.5 * s))), max(1, int(round(1.4 * s)))
    hbx = hx if dirn > 0 else hx + hw - bw
    if bald:
        a.rect(hbx, hy + t, hbx + bw, hy + hh - 2, m(hair))
    else:
        e = 2 if hw >= 8 else 1
        a.rect(hx + e, hy, hx + hw - e, hy + 1, m(hair))
        a.rect(hx + e - 1, hy + 1, hx + hw - e + 1, hy + 2, m(hair))
        if t > 2:
            a.rect(hx, hy + 2, hx + hw, hy + t, m(hair))
        elif e == 1 and t == 2:
            a.rect(hx, hy + 1, hx + hw, hy + 2, m(hair))
        a.rect(hbx, hy + 1, hbx + bw, hy + hh - (1 if woman else 2), m(hair))
        if woman:
            fxh = hx + hw - 1 if dirn > 0 else hx
            a.rect(fxh, hy + 1, fxh + 1, hy + t + 1, m(hair))
    fx = hx + hw - 1 if dirn > 0 else hx
    ey = hy + t + max(1, int(round(0.9 * s)))
    a.dot(fx - dirn, ey, m(DEEP))
    if hw >= 7:
        a.dot(fx - dirn * (2 + hw // 4), ey, m(DEEP))
    if hw >= 7:
        a.dot(fx + dirn, ey + 1, m(skin))        # nose
    if mouth:
        my = hy + hh - (3 if hh >= 9 else 2)
        a.dot(fx - dirn, my, m(RED_DK))
        if hw >= 7:
            a.dot(fx - 2 * dirn, my, m(RED_DK))
    return m(suit)


# ---- architecture ---------------------------------------------------------
def arch_top(x, x0, x1, apex, rise):
    hw = (x1 - x0) / 2.0
    dx = min(abs(x + 0.5 - (x0 + x1) / 2.0), hw)
    return apex + int(round(rise * (dx / hw) ** 1.5))


def gothic_window(a, x0, x1, apex, bot, rise=18):
    """Three-light perpendicular window: stone frame, transparent glass."""
    for x in range(x0 - 3, x1 + 3):
        a.rect(x, arch_top(x, x0 - 3, x1 + 3, apex - 3, rise + 2), x + 1, bot, OAK_SH)
    for x in range(x0 - 2, x1 + 2):
        a.rect(x, arch_top(x, x0 - 2, x1 + 2, apex - 2, rise + 1), x + 1, bot, STN)
    for x in range(x0 - 1, x1 + 1):
        a.rect(x, arch_top(x, x0 - 1, x1 + 1, apex - 1, rise + 1), x + 1, bot, STN_DK)
    for x in range(x0, x1):
        a.clear(x, arch_top(x, x0, x1, apex, rise), x + 1, bot)
    lw = (x1 - x0 - 4) // 3                       # 14px lights, 2px mullions
    ty = apex + rise + 11                         # transom
    a.rect(x0, ty, x1, ty + 1, STN_DK)
    for i in range(3):
        lx0 = x0 + i * (lw + 2)
        lx1 = lx0 + lw
        if i:
            a.rect(lx0 - 2, arch_top(lx0 - 2, x0, x1, apex, rise), lx0, bot, STN_DK)
        for dx, dy in ((0, 1), (1, 1), (0, 2)):   # cusped heads under the transom
            a.dot(lx0 + dx, ty + dy, STN_DK)
            a.dot(lx1 - 1 - dx, ty + dy, STN_DK)
    a.rect(x0 - 5, bot, x1 + 5, bot + 1, STN_HI)      # sill
    a.rect(x0 - 5, bot + 1, x1 + 5, bot + 2, STN)
    a.rect(x0 - 4, bot + 2, x1 + 4, bot + 3, OAK_SH)


def shield(a, x, y, col, charge=GOLD):
    a.rect(x - 3, y, x + 4, y + 5, col)
    a.rect(x - 2, y + 5, x + 3, y + 7, col)
    a.rect(x - 1, y + 7, x + 2, y + 8, col)
    a.rect(x - 3, y, x + 4, y + 1, GOLD_HI)
    a.rect(x, y + 1, x + 1, y + 7, charge)
    a.rect(x - 2, y + 3, x + 3, y + 4, charge)


def floor(a):
    """Green carpet, diamond weave in perspective, red sword line."""
    for y in range(150, STAGE_H):
        s = (y - VY) / float(H0)
        z = D0 * (1 - 1 / s)
        lvl = max(0.0, (164 - y) / 14.0) * 0.8
        for x in range(HALF):
            X = (HALF - x - 0.5) / s
            dark = lvl * 16 > BAYER[y & 3][x & 3] + 0.5
            if X >= 113:
                c = OAK_SH if dark else OAK_DK
            elif 63.5 <= X < 67.5:
                c = RED_DK if dark else RED
            elif X >= 105:
                c = LEA_DK if dark else LEA
            else:
                u, v = int((X + z) // 14), int((X - z + 1400) // 14)
                c = LEA if dark else (CAR1 if (u + v) & 1 else LEA_HI)
            a.p[x, y] = a.c(c)


def back_wall(a, R):
    # upper wall, cornice
    a.rect(64, 0, HALF, 56, OAK_DK)
    a.rect(64, 0, HALF, 10, OAK_SH)
    a.dither(64, 10, HALF, 14, OAK_SH, 0.5)
    a.rect(64, 0, HALF, 5, DEEP)
    a.rect(64, 5, HALF, 6, GOLD_DK)
    for x in range(72, HALF, 16):
        a.rect(x, 2, x + 2, 4, GOLD_DK)
    for x0 in (73, 137, 201):
        gothic_window(a, x0, x0 + 46, 9, 50)
    for i, px_ in enumerate((128, 192, 256)):          # piers: shaft + heraldic shield
        a.rect(px_ - 1, 6, px_ + 1, 50, OAK_MID)
        a.rect(px_ - 3, 20, px_ + 3, 22, OAK_MID)
        shield(a, px_, 26, (RED, BLUE, LEA_HI)[i], GOLD if i != 1 else CREAM)
    a.rect(64, 53, HALF, 60, OAK_SH)
    # gallery onlookers (press + strangers), then the carved gallery front
    x = 93 + R.randint(0, 3)
    while x < 250:
        person(a, R, x, 60, 1.0, R.choice((8, 9, 9, 10)), 1 if R.random() < 0.75 else -1, th_u=7, ext=2, jeer=0.2)
        x += R.choice((11, 12, 13, 15))
    a.rect(84, 60, HALF, 74, OAK)
    a.rect(84, 60, HALF, 61, GOLD_HI)
    a.rect(84, 61, HALF, 62, GOLD)
    a.rect(84, 62, HALF, 63, OAK_HI)
    a.rect(84, 71, HALF, 72, OAK_MID)
    a.rect(84, 72, HALF, 74, OAK_DK)
    for i, x in enumerate(range(96, HALF, 16)):
        a.rect(x - 1, 63, x + 1, 72, OAK_MID)
        a.rect(x + 1, 63, x + 2, 71, OAK_HI)
        c = x + 8
        for dx, dy in ((0, -2), (-2, 0), (2, 0), (0, 2), (-1, -1), (1, -1), (-1, 1), (1, 1)):   # quatrefoil
            a.dot(c + dx, 67 + dy, OAK_DK)
        a.dot(c, 67, GOLD if i % 2 else OAK_HI)
    a.rect(64, 74, HALF, 75, DEEP)
    # panelled dado under the gallery: pointed arcade over square panels
    a.rect(64, 75, HALF, 150, OAK_MID)
    for x in range(64, HALF, 16):
        a.rect(x, 75, x + 3, 146, OAK)
        a.rect(x, 75, x + 1, 146, OAK_DK)
        a.rect(x + 4, 88, x + 15, 114, OAK_DK)
        a.rect(x + 5, 89, x + 15, 114, OAK_MID)
        for j, n in enumerate((4, 3, 2, 1, 1)):       # pointed panel head
            a.rect(x + 4, 88 + j, x + 4 + n, 89 + j, OAK)
            a.rect(x + 15 - n, 88 + j, x + 15, 89 + j, OAK)
        a.rect(x + 4, 123, x + 15, 143, OAK_DK)
        a.rect(x + 5, 124, x + 15, 143, OAK_MID)
    a.rect(64, 80, HALF, 84, OAK)
    a.rect(64, 116, HALF, 121, OAK)
    a.rect(64, 116, HALF, 117, OAK_HI)
    a.rect(64, 120, HALF, 121, OAK_DK)
    a.rect(64, 145, HALF, 150, OAK_DK)
    a.rect(64, 145, HALF, 146, OAK)
    a.rect(64, 75, HALF, 79, OAK_SH)
    a.dither(64, 79, HALF, 82, OAK_SH, 0.5)
    a.dither(64, 82, HALF, 90, OAK_SH, 0.25)
    # division-lobby door
    a.rect(158, 98, 194, 150, OAK_DK)
    a.rect(160, 100, 192, 150, OAK)
    a.rect(162, 102, 190, 150, OAK_DK)
    a.rect(163, 103, 189, 150, OAK_MID)
    for j, n in enumerate((6, 4, 3, 2, 1, 1)):
        a.rect(162, 102 + j, 162 + n, 103 + j, OAK)
        a.rect(190 - n, 102 + j, 190, 103 + j, OAK)
    a.rect(175, 104, 177, 150, OAK_DK)
    for dx in (165, 179):
        a.rect(dx, 110, dx + 9, 126, OAK_DK)
        a.rect(dx + 1, 111, dx + 9, 126, OAK)
        a.rect(dx, 130, dx + 9, 146, OAK_DK)
        a.rect(dx + 1, 131, dx + 9, 146, OAK)
    a.rect(173, 128, 174, 130, GOLD)
    a.rect(178, 128, 179, 130, GOLD)
    a.rect(164, 87, 188, 97, GOLD_DK)                 # sign plaque (lettered after mirroring)
    a.rect(165, 88, 187, 96, LEA_DK)
    a.rect(64, 149, HALF, 150, DEEP)


def side_wall(a):
    wedge(a, 192, 0, 150, OAK_DK)
    wedge(a, 192, 0, 76, OAK_SH)
    for j in range(8):
        s = D0 / (D0 - 14 * j)
        a.line([L(192, 78, s), L(192, 150, s)], OAK_MID)
    # raking window
    s0, s1 = 1.06, 1.27
    sm = (s0 + s1) / 2
    a.poly([L(192, 94, s0 - .018), L(192, 131, s0 - .018), L(192, 147, sm), L(192, 131, s1 + .02), L(192, 94, s1 + .02)], STN)
    a.poly([L(192, 96, s0 - .008), L(192, 130, s0 - .008), L(192, 145, sm), L(192, 130, s1 + .008), L(192, 96, s1 + .008)], STN_DK)
    a.clear_poly([L(192, 98, s0), L(192, 128, s0), L(192, 142, sm), L(192, 128, s1), L(192, 98, s1)])
    a.line([L(192, 98, sm), L(192, 142, sm)], STN_DK)
    a.line([L(192, 114, s0), L(192, 114, s1)], STN_DK)
    a.line([L(192, 97, s0 - .02), L(192, 97, s1 + .03)], STN_HI)


def side_gallery(a, R):
    for i in range(5):
        s = depth(i, off=4, pitch=13)
        x, y = L(180, 90, s)
        person(a, R, x, y, s, max(8, int(9 * s)), 1, th_u=7, ext=int(4 * s), jeer=0.3, wave=(i == 2))
    hwedge(a, 170, 192, 76, DEEP)
    wedge(a, 170, 76, 90, OAK)
    wedge(a, 170, 76, 78.5, OAK_DK)
    wedge(a, 170, 86.5, 88, OAK_HI)
    wedge(a, 170, 88, 90, GOLD)
    a.line([L(170, 90, 1), L(170, 90, 4)], GOLD_HI)
    prev = None
    for j in range(9):
        s = D0 / (D0 - 16 * j)
        a.line([L(170, 78.5, s), L(170, 87, s)], OAK_MID)
        if prev:
            sm = (s + prev) / 2
            x, y = L(170, 82.5, sm)
            a.rect(int(x) - 1, int(y) - 1, int(x) + 1, int(y) + 1, OAK_DK)
        prev = s
    a.rect(84, 57, 88, 76, OAK_DK)                    # corner post where the galleries meet
    a.rect(85, 57, 86, 76, OAK)
    a.rect(84, 56, 88, 58, GOLD)


def benches(a, R):
    """Five raked rows of green leather, back row in the gallery's shadow."""
    front = []
    for k in (4, 3, 2, 1, 0):
        Xb, F, Xc = 131 + 15 * k, 9 * k, 123.5 + 15 * k
        dark = k == 4
        wedge(a, Xb, F + 6, F + 21, LEA_DK if dark else LEA)
        wedge(a, Xb, F + 19, F + 21, LEA if dark else LEA_HI)
        wedge(a, Xb, F + 21, F + 22.2, OAK_DK if dark else OAK)       # oak capping rail
        for j in range(1, 9):                                           # buttoned seams
            s = D0 / (D0 - 12 * j)
            a.line([L(Xb, F + 9, s), L(Xb, F + 19, s)], LEA_SH if dark else LEA_DK)
        if F + 11 < H0:
            hwedge(a, Xb - 15, Xb, F + 11, LEA_DK if dark else LEA_HI)
        seats = [depth(i) for i in range(10)]
        xs = [VX - Xc * s for s in seats]
        for i, s in enumerate(seats):
            if xs[i] < -24:
                break
            gap = xs[i] - xs[i + 1] if i + 1 < len(xs) else 40
            w = int(max(8, min(round(10 * s), round(0.86 * gap))))
            by = VY + (H0 - (F + 12)) * s
            wave = (not dark) and R.random() < (0.0, 0.12, 0.3, 0.34, 0)[k] and i > 0
            suit = person(a, R, xs[i], by, s, w, 1, dark=dark, wave=wave, ext=int(5 * s) + 3)
            if k == 0:
                front.append((s, suit, R.choice((SK1, SK1, SK2))))
    # front bench: seat front + the front-benchers' legs
    wedge(a, 116, 0, 12.5, LEA)
    wedge(a, 116, 10.5, 12.5, LEA_HI)
    wedge(a, 116, 0, 3, OAK_DK)
    wedge(a, 116, 3, 3.8, OAK)
    for s, suit, skin in front:
        t = max(3, int(round(2.9 * s)))
        fy = int(VY + H0 * s)
        kx, ky = L(110, 16, s)
        bx_, _ = L(119.5, 16, s)
        kx, ky, bx_ = int(kx), int(ky), int(bx_)
        a.rect(bx_, ky, kx + t - 1, ky + t, suit)                # thigh
        a.rect(kx, ky + 1, kx + t, fy - 1, suit)                 # shin
        a.rect(bx_, ky + t, kx, ky + t + 1, DEEP)
        a.rect(kx, ky + t, kx + 1, fy - 1, DEEP)
        a.rect(kx - 1, fy - max(2, t - 1), kx + t + max(1, t // 2), fy, DEEP)   # shoe
        h = max(2, t - 1)
        a.rect(kx - h, ky - 1, kx, ky + h - 1, skin)             # hand resting on the knee
        a.rect(kx - h - 1, ky - 1, kx - h, ky + h - 1, CREAM)    # cuff
    a.line([L(116, 0, 1), L(116, 0, 4)], DEEP)


def half(seed):
    R = random.Random(seed)
    a = Art(HALF, STAGE_H, mode="RGBA")
    a.rect(0, 0, HALF, 150, OAK_SH)
    floor(a)
    back_wall(a, R)
    side_wall(a)
    side_gallery(a, R)
    benches(a, R)
    return a.im


# ---- centre pieces ----------------------------------------------------------
def speakers_chair(a):
    c = VX
    # dais
    a.rect(c - 36, 143, c + 36, 150, OAK_DK)
    a.rect(c - 36, 143, c + 36, 144, OAK)
    # back panel + green leather
    a.rect(c - 23, 86, c + 23, 144, OAK_DK)
    a.rect(c - 18, 94, c + 18, 136, LEA_DK)
    a.rect(c - 17, 95, c + 17, 136, LEA)
    a.rect(c - 17, 95, c + 17, 97, LEA_HI)
    for bx in (-12, -4, 4, 12):
        for by in (102, 110):
            a.dot(c + bx, by, LEA_DK)
    # posts
    for sgn in (-1, 1):
        x0 = c + sgn * 26 - 3
        a.rect(x0, 82, x0 + 6, 144, OAK)
        a.rect(x0, 82, x0 + 1, 144, OAK_HI)
        a.rect(x0 + 5, 82, x0 + 6, 144, OAK_DK)
        for by in (96, 120):
            a.rect(x0, by, x0 + 6, by + 2, GOLD_DK)
        # pinnacle
        a.rect(x0 + 1, 68, x0 + 5, 76, OAK)
        a.rect(x0 + 2, 64, x0 + 4, 68, OAK)
        a.rect(x0 + 2, 61, x0 + 4, 64, GOLD)
        a.dot(x0 + 2, 61, GOLD_HI)
    # canopy
    a.rect(c - 32, 76, c + 32, 88, OAK)
    a.rect(c - 32, 76, c + 32, 77, OAK_HI)
    a.rect(c - 32, 86, c + 32, 88, GOLD_DK)
    a.rect(c - 32, 86, c + 32, 87, GOLD)
    a.rect(c - 30, 88, c + 30, 90, OAK_SH)
    for x in range(c - 28, c + 28, 8):                 # little arcade on the canopy front
        a.rect(x + 1, 80, x + 7, 85, OAK_DK)
        a.rect(x + 2, 79, x + 6, 80, OAK_DK)
        a.rect(x + 3, 78, x + 5, 79, OAK_DK)
    # gable + royal arms
    for j in range(17):
        hw_ = 26 - int(j * 1.5)
        a.rect(c - hw_, 75 - j, c + hw_, 76 - j, OAK_MID if j % 4 == 3 else OAK)
        a.dot(c - hw_, 75 - j, OAK_HI)
        a.dot(c + hw_ - 1, 75 - j, OAK_DK)
    a.rect(c - 4, 64, c + 4, 72, GOLD)
    a.rect(c - 3, 65, c + 3, 71, RED)
    a.rect(c - 1, 65, c + 1, 71, GOLD_HI)
    a.rect(c - 3, 67, c + 3, 69, GOLD_HI)
    a.rect(c - 1, 52, c + 1, 59, GOLD)
    a.rect(c - 3, 54, c + 3, 56, GOLD)
    a.dot(c - 1, 52, GOLD_HI)
    # the Speaker: full-bottomed wig, black robe, lace bands
    a.rect(c - 14, 116, c + 14, 137, DEEP)
    a.rect(c - 12, 114, c + 12, 116, DEEP)
    a.rect(c - 14, 118, c - 12, 137, CHAR)
    a.rect(c + 12, 118, c + 14, 137, CHAR)
    a.rect(c - 6, 101, c + 6, 117, WIG)
    a.rect(c - 5, 100, c + 5, 101, WIG)
    a.rect(c - 7, 106, c + 7, 116, WIG)
    a.rect(c + 4, 102, c + 6, 117, WIG_SH)
    a.rect(c + 6, 106, c + 7, 116, WIG_SH)
    for wy in (109, 112, 115):
        a.rect(c - 7, wy, c - 4, wy + 1, WIG_SH)
    a.rect(c - 3, 104, c + 3, 112, SK1)
    a.rect(c - 3, 111, c + 3, 112, SK_SH)
    a.dot(c - 2, 107, DEEP)
    a.dot(c + 1, 107, DEEP)
    a.rect(c - 1, 110, c + 1, 111, RED_DK)
    a.rect(c - 2, 113, c + 2, 120, CREAM)
    a.rect(c - 1, 113, c, 120, WIG)


def table(a):
    c = VX
    # three clerks with their backs to the Chair
    for dx, skin in ((-15, SK2), (0, SK1), (15, SK1)):
        x = c + dx
        a.rect(x - 6, 130, x + 6, 137, DEEP)
        a.rect(x - 5, 129, x + 5, 130, DEEP)
        a.rect(x - 4, 122, x + 4, 130, WIG)
        a.rect(x - 3, 121, x + 3, 122, WIG)
        a.rect(x + 3, 123, x + 4, 130, WIG_SH)
        a.rect(x - 2, 124, x + 2, 129, skin)
        a.dot(x - 1, 126, DEEP)
        a.dot(x + 1, 126, DEEP)
        a.rect(x - 1, 129, x + 1, 132, CREAM)
    s0, s1 = 1.08, 1.32
    yb, yf = int(VY + 23 * s0), int(VY + 23 * s1)             # 134, 140
    a.poly([(c - 30 * s0, yb), (c + 30 * s0 - 1, yb), (c + 30 * s1 - 1, yf), (c - 30 * s1, yf)], OAK_HI)
    a.poly([(c - 24 * s0, yb + 1), (c + 24 * s0 - 1, yb + 1), (c + 25 * s1 - 1, yf - 1), (c - 25 * s1, yf - 1)], LEA)
    x0, x1, yt, yb2 = c - 40, c + 40, yf, int(VY + H0 * s1)   # front face 216..296, 140..162
    a.rect(x0, yt, x1, yb2, OAK)
    a.rect(x0, yt, x1, yt + 1, OAK_HI)
    a.rect(x0, yt + 1, x1, yt + 3, OAK)
    a.rect(x0 + 1, yt + 3, x1 - 1, yt + 4, OAK_DK)
    for i in range(5):
        px0 = x0 + 3 + i * 15
        a.rect(px0, yt + 6, px0 + 14, yb2 - 4, OAK_DK)
        a.rect(px0 + 1, yt + 7, px0 + 14, yb2 - 4, OAK_MID)
        for j, n in enumerate((4, 2, 1)):
            a.rect(px0 + 1, yt + 7 + j, px0 + 1 + n, yt + 8 + j, OAK)
            a.rect(px0 + 14 - n, yt + 7 + j, px0 + 14, yt + 8 + j, OAK)
    a.rect(x0, yb2 - 3, x1, yb2, OAK_DK)
    a.rect(x0, yb2 - 1, x1, yb2, DEEP)
    a.rect(x0, yt, x0 + 1, yb2, OAK_HI)
    a.rect(x1 - 1, yt, x1, yb2, OAK_DK)
    # despatch boxes
    for sgn in (-1, 1):
        bx = c + sgn * 29 - 8
        a.rect(bx, 129, bx + 16, 139, OAK_DK)
        a.rect(bx, 129, bx + 16, 130, OAK)
        a.rect(bx, 132, bx + 16, 133, GOLD)
        for cx_ in (bx, bx + 14):
            a.rect(cx_, 129, cx_ + 2, 131, GOLD_HI)
            a.rect(cx_, 137, cx_ + 2, 139, GOLD)
        a.rect(bx + 7, 133, bx + 9, 135, GOLD_HI)
    # ...and a certain handbag on the Government one
    bx = c - 29 - 5
    a.rect(bx, 122, bx + 10, 129, DEEP)
    a.rect(bx + 1, 121, bx + 9, 122, DEEP)
    a.rect(bx, 123, bx + 10, 124, CHAR)
    a.rect(bx + 4, 122, bx + 6, 124, GOLD_HI)
    for hx_, hy_ in ((2, 119), (2, 120), (3, 118), (4, 117), (5, 117), (6, 118), (7, 119), (7, 120)):
        a.dot(bx + hx_, hy_, DEEP)
    # a pint of milk nobody dares touch (Opposition side)
    mx = c + 15
    a.rect(mx - 1, 130, mx + 4, 137, CREAM)
    a.rect(mx, 129, mx + 3, 130, CREAM)
    a.rect(mx, 126, mx + 3, 129, WIG)
    a.rect(mx, 125, mx + 3, 126, RED)
    a.rect(mx + 3, 130, mx + 4, 137, WIG)
    # the mace, crown toward the Government benches
    a.rect(c - 14, 137, c + 22, 139, GOLD)
    a.rect(c - 14, 137, c + 22, 138, GOLD_HI)
    for kx in (c - 6, c + 6, c + 16):
        a.rect(kx, 136, kx + 2, 140, GOLD)
        a.dot(kx, 136, GOLD_HI)
    a.rect(c + 22, 136, c + 25, 140, GOLD_DK)
    a.rect(c - 22, 134, c - 14, 141, GOLD)
    a.rect(c - 23, 136, c - 22, 140, GOLD)
    a.rect(c - 21, 133, c - 15, 134, GOLD)
    a.rect(c - 21, 134, c - 15, 135, GOLD_HI)
    a.rect(c - 19, 131, c - 17, 133, GOLD_HI)       # orb + cross
    a.rect(c - 21, 137, c - 15, 138, RED)
    a.rect(c - 22, 140, c - 14, 141, GOLD_DK)
    # shadow under the table
    a.dither(x0 - 2, yb2, x1 + 2, yb2 + 2, LEA_DK, 0.75)
    a.dither(x0 - 4, yb2 + 2, x1 + 4, yb2 + 4, LEA_DK, 0.4)


def union_flag(a, x, y):
    w, h = 21, 11
    a.rect(x, y, x + w, y + h, BLUE)
    for i in range(w):
        j = i * (h - 1) // (w - 1)
        a.dot(x + i, y + j, CREAM)
        a.dot(x + i, y + h - 1 - j, CREAM)
    a.rect(x + 8, y, x + 13, y + h, CREAM)
    a.rect(x, y + 3, x + w, y + 8, CREAM)
    a.rect(x + 9, y, x + 12, y + h, RED)
    a.rect(x, y + 4, x + w, y + 7, RED)


def lamp(a, x, drop, big):
    a.rect(x, 0, x + 1, drop, DEEP)
    w = 5 if big else 4
    a.rect(x - w, drop, x + w + 1, drop + 2, GOLD_DK)
    a.rect(x - w + 1, drop + 2, x + w, drop + (7 if big else 5), GOLD_HI)
    a.rect(x - w + 1, drop + 2, x - w + 2, drop + (7 if big else 5), GOLD)
    a.rect(x + w - 1, drop + 2, x + w, drop + (7 if big else 5), GOLD)
    a.rect(x - w + 2, drop + (7 if big else 5), x + w - 1, drop + (8 if big else 6), GOLD_DK)


# ---- far layer -------------------------------------------------------------
def cloud(f, cx, base, w, h, col, lit, seed):
    r = random.Random(seed)
    m = Image.new("L", (f.w, f.h), 0)
    d = ImageDraw.Draw(m)
    n = max(3, w // 9)
    for i in range(n):
        ew = w // n + r.randint(5, 11)
        eh = r.randint(max(2, h // 2), h)
        ex = cx - w // 2 + i * w // n
        if i in (0, n - 1):
            eh = max(2, eh // 2)
        d.ellipse([ex, base - eh, ex + ew, base + eh], fill=255)
    mp = m.load()
    for y in range(max(0, base - h - 1), base):
        for x in range(max(0, cx - w), min(f.w, cx + w)):
            if mp[x, y]:
                f.p[x, y] = f.c(lit if y >= base - 2 else col)


def build_far():
    f = Art(FAR_W, STAGE_H)
    SKY = ["#1c1c4c", "#34286c", "#683878", "#b85070", "#ec8c5c", "#fccc7c"]
    FARC, NEAR, LIT = "#40286c", "#201848", "#fce8a0"
    f.vgrad(0, 0, FAR_W, 58, SKY)
    f.rect(0, 58, FAR_W, STAGE_H, SKY[-1])
    # brooding cloud banks, underlit by the last of the sun
    for i, (cx, base, w, h) in enumerate(((40, 15, 90, 7), (170, 12, 70, 6), (300, 17, 110, 8), (420, 13, 60, 6))):
        cloud(f, cx, base, w, h, "#28204c", "#683878", 10 + i)
    for i, (cx, base, w, h) in enumerate(((100, 30, 80, 7), (236, 27, 70, 6), (372, 31, 84, 7), (20, 38, 50, 5), (452, 39, 60, 5))):
        cloud(f, cx, base, w, h, "#4c3074", "#ec8c5c", 20 + i)
    for i, (cx, base, w, h) in enumerate(((150, 42, 60, 4), (330, 43, 70, 4), (64, 45, 40, 3))):
        cloud(f, cx, base, w, h, "#b85070", "#fccc7c", 30 + i)
    # distant roofs
    r = random.Random(7)
    x = 0
    while x < FAR_W:
        w, h = r.randint(8, 20), r.randint(3, 9)
        f.rect(x, 48 - h, x + w, STAGE_H, FARC)
        if r.random() < 0.4:
            f.rect(x + 2, 48 - h - 3, x + 4, 48 - h, FARC)       # chimney stack
        x += w
    # St Paul's dome
    f.ellipse(311, 32, 330, 50, FARC)
    f.rect(313, 41, 328, 48, FARC)
    f.rect(318, 27, 323, 33, FARC)
    f.rect(320, 22, 321, 27, FARC)
    f.rect(319, 24, 322, 25, FARC)
    # Post Office Tower
    f.rect(62, 20, 67, 48, FARC)
    f.rect(60, 23, 69, 33, FARC)
    f.rect(64, 13, 65, 20, FARC)
    for wy in (25, 28, 31):
        f.rect(61, wy, 68, wy + 1, "#683878")
    # Battersea's four chimneys
    f.rect(371, 39, 399, 48, FARC)
    for cxh in (372, 379, 389, 396):
        f.rect(cxh, 25, cxh + 2, 40, FARC)
    # Palace of Westminster roofline: pinnacles along the parapet
    f.rect(0, 47, FAR_W, STAGE_H, NEAR)
    for x in range(2, FAR_W, 6):
        f.rect(x, 44, x + 1, 47, NEAR)
        if x % 4 == 2:
            f.rect(x + 3, 45, x + 4, 47, NEAR)
    # Elizabeth Tower (Big Ben)
    c = 192
    f.rect(c - 6, 36, c + 7, 60, NEAR)
    f.rect(c - 7, 24, c + 8, 37, NEAR)
    f.rect(c - 8, 23, c + 9, 24, NEAR)
    f.rect(c - 6, 19, c + 7, 23, NEAR)
    f.rect(c - 5, 16, c + 6, 19, NEAR)
    f.rect(c - 3, 13, c + 4, 16, NEAR)
    f.rect(c - 1, 10, c + 2, 13, NEAR)
    f.rect(c, 6, c + 1, 10, NEAR)
    f.ellipse(c - 4, 26, c + 5, 35, LIT)
    f.rect(c, 27, c + 1, 31, NEAR)                  # hands: ten to ... something
    f.rect(c, 30, c + 3, 31, NEAR)
    for dx in (-3, 0, 3):
        f.rect(c + dx, 20, c + dx + 1, 22, "#ec8c5c")
    f.dot(c, 14, LIT)
    for wy in range(39, 47, 3):
        f.dot(c - 3, wy, "#683878")
        f.dot(c + 3, wy, "#683878")
    # Victoria Tower + Union flag
    f.rect(152, 26, 169, 60, NEAR)
    for px_ in (152, 157, 162, 167):
        f.rect(px_, 21, px_ + 2, 26, NEAR)
    f.rect(160, 11, 161, 22, NEAR)
    f.rect(161, 11, 167, 15, "#c8383c")
    f.rect(161, 12, 167, 14, "#fce8a0")
    f.rect(161, 13, 167, 14, "#c8383c")
    f.rect(163, 11, 164, 15, "#c8383c")
    for wy in (30, 36, 42):
        for wx in (155, 160, 165):
            f.rect(wx, wy, wx + 1, wy + 3, "#ec8c5c" if (wx + wy) % 3 else "#683878")
    # Westminster Abbey's west towers
    for tx in (343, 355):
        f.rect(tx, 28, tx + 7, 60, NEAR)
        f.rect(tx, 24, tx + 1, 28, NEAR)
        f.rect(tx + 6, 24, tx + 7, 28, NEAR)
        f.rect(tx + 3, 32, tx + 4, 38, LIT)
    f.poly([(350, 47), (352, 36), (355, 47)], NEAR)
    # a lit office block and a church spire for the other bays
    f.rect(280, 30, 296, 60, NEAR)
    for wy in range(33, 46, 3):
        for wx in range(282, 295, 3):
            if (wx * 7 + wy * 3) % 5 < 2:
                f.dot(wx, wy, LIT)
    f.rect(94, 34, 100, 60, NEAR)
    f.poly([(94, 34), (97, 18), (99, 34)], NEAR)
    f.rect(96, 37, 98, 41, LIT)
    f.rect(26, 33, 40, 60, NEAR)
    f.rect(30, 29, 36, 33, NEAR)
    f.rect(412, 35, 424, 60, NEAR)
    f.poly([(412, 35), (418, 27), (424, 35)], NEAR)
    return f


def build():
    f = build_far()

    a = Art(STAGE_W, STAGE_H, mode="RGBA")
    a.im.paste(half(1979), (0, 0))
    a.im.paste(half(1990).transpose(Image.FLIP_LEFT_RIGHT), (HALF, 0))

    speakers_chair(a)
    table(a)

    # lettering + gallery dressing (after mirroring so it reads the right way round)
    a.text((169, 90), "AYES", GOLD_HI, tiny=True)
    a.text((329, 90), "NOES", GOLD_HI, tiny=True)
    union_flag(a, 150, 62)
    a.rect(302, 62, 367, 73, CREAM)
    a.rect(302, 72, 367, 73, WIG)
    a.rect(303, 60, 304, 62, DEEP)
    a.rect(365, 60, 366, 62, DEEP)
    a.text((305, 65), "NOT FOR TURNING", NAVY, tiny=True)

    # brass pendant lamps hanging in front of the windows
    for x, drop, big in ((146, 15, False), (365, 15, False), (82, 23, True), (429, 23, True)):
        lamp(a, x, drop, big)
    return f.im, a.im
