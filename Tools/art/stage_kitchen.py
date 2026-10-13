"""JULIA'S KITCHEN - Paris, France.  Julia Child's stage.

far  : afternoon Paris - zinc mansard roofs, chimney pots, the Eiffel Tower
       (seen through the French window) and Sacre-Coeur (through the balcony
       door on the right).
main : the Rue de l'Universite kitchen - pegboard of copper pans with painted
       outlines, sage cabinets under a butcher-block counter, the big range
       with a copper hood, terracotta checker floor.  Wall meets floor at
       y = WALL_Y (150).
"""
import math
import random

from bg import Art
from stages import FAR_W, STAGE_H, STAGE_W, WALL_Y, floor_checker

# ---- main-layer palette (kept small on purpose) -----------------------------
K = "#2c2444"      # darkest (blue-purple, never pure black)
D2 = "#4c3c68"
D3 = "#74649c"
RG = "#3c3458"     # range enamel
CR0 = "#fcf4dc"    # cream highlight
CR1 = "#f8e4b0"
CR2 = "#f0cc8c"
CR3 = "#d8a870"
T0 = "#7cccb4"     # pegboard / tile teals
T1 = "#48a898"
T2 = "#308088"
T3 = "#205c70"
SG0 = "#a4d0a4"    # sage cabinets
SG1 = "#70ac8c"
SG2 = "#488474"
SG3 = "#2c5860"
CO0 = "#fcd088"    # copper
CO1 = "#f09848"
CO2 = "#d06830"
CO3 = "#983c2c"
CO4 = "#64243c"
W0 = "#f0b868"     # butcher block / wood
W1 = "#c88448"
W2 = "#985838"
F1 = "#f0c48c"     # floor tiles
F2 = "#d88c5c"
F3 = "#a45458"
S0 = "#e4ecf4"     # chrome / steel
S1 = "#a4b0d0"
S2 = "#6470a0"
R1 = "#d8243c"
R2 = "#8c1830"
PK = "#f08878"
OR = "#e85428"     # flame-orange enamel
G1 = "#68b040"
G2 = "#2c7038"
Y1 = "#f8d048"
BT = "#1c4c40"     # wine-bottle green
SK = "#f4c098"
SK2 = "#c88868"


# =============================================================================
#  FAR LAYER
# =============================================================================
def _cloud(f, x, y, w):
    c, s = "#fcf8e8", "#d0dcf4"
    f.rect(x, y, x + w, y + 3, c)
    f.rect(x + 3, y - 2, x + w - 5, y, c)
    f.rect(x + w // 3, y - 4, x + w // 3 + w // 3, y - 2, c)
    f.rect(x + 2, y + 3, x + w - 3, y + 4, s)
    f.rect(x + 6, y + 4, x + w - 9, y + 5, s)


def _eiffel(f, cx, top, base, col, hi):
    h = base - top

    def hw(t):
        return int(round(1 + 10.5 * t ** 2.7))

    f.rect(cx, top - 7, cx + 1, top, col)
    for y in range(top, base):
        t = (y - top) / h
        w = hw(t)
        if t < 0.64:
            f.rect(cx - w, y, cx + w + 1, y + 1, col)
            if w >= 2:
                f.dot(cx - w, y, hi)
        else:
            lw = 2 if t < 0.82 else 3
            # arch between the legs just under the first platform
            if 0.82 <= t < 0.90:
                gap = int((t - 0.82) / 0.08 * (w - lw))
                f.rect(cx - w, y, cx - gap, y + 1, col)
                f.rect(cx + gap + 1, y, cx + w + 1, y + 1, col)
            else:
                f.rect(cx - w, y, cx - w + lw, y + 1, col)
                f.rect(cx + w + 1 - lw, y, cx + w + 1, y + 1, col)
                if t < 0.82 and (y & 1):                      # lattice cross-bracing
                    f.rect(cx - w + lw, y, cx + w + 1 - lw, y + 1, col)
            f.dot(cx - w, y, hi)
    for t, ext in ((0.30, 1), (0.64, 1), (0.82, 1)):          # the three platforms
        y = top + int(h * t)
        w = hw(t) + ext
        f.rect(cx - w, y, cx + w + 1, y + 2, col)
        f.rect(cx - w, y, cx + w + 1, y + 1, hi)


def _sacre_coeur(f, cx, base):
    c, s = "#fcf8e8", "#8c9cd8"
    f.rect(cx - 13, base - 8, cx + 14, base, c)               # nave
    f.rect(cx - 5, base - 16, cx + 6, base - 8, c)            # drum
    f.ellipse(cx - 5, base - 27, cx + 6, base - 9, c)         # great dome
    f.rect(cx, base - 32, cx + 1, base - 26, c)               # lantern
    f.rect(cx - 1, base - 30, cx + 2, base - 28, c)
    for dx in (-12, 8):                                       # side domes
        f.ellipse(dx + cx, base - 16, dx + cx + 6, base - 6, c)
        f.rect(dx + cx + 2, base - 18, dx + cx + 3, base - 15, c)
    f.rect(cx + 3, base - 24, cx + 6, base - 8, s)            # shade side
    f.rect(cx + 11, base - 13, cx + 14, base, s)
    f.rect(cx - 9, base - 5, cx - 7, base, s)
    f.rect(cx - 1, base - 6, cx + 2, base, s)
    f.rect(cx + 6, base - 5, cx + 8, base, s)


def _building(f, x, w, top, r, chimneys=True):
    zinc, zhi, zsh = "#7084b8", "#a4b8e0", "#566496"
    stone, stone_s, win = "#f4e0b8", "#d8b894", "#585490"
    # chimney stacks with their rows of terracotta pots
    for _ in range(r.randint(1, 2) if chimneys else 0):
        cx = x + r.randint(3, max(4, w - 16))
        cw = r.randint(8, 13)
        ch = r.randint(5, 9)
        f.rect(cx, top - ch, cx + cw, top, "#c47858")
        f.rect(cx, top - ch, cx + 2, top, "#e09c74")
        f.rect(cx - 1, top - ch - 1, cx + cw + 1, top - ch, "#8c4c50")
        for px_ in range(cx + 1, cx + cw - 1, 3):
            f.rect(px_, top - ch - 4, px_ + 2, top - ch - 1, "#e8843c")
            f.dot(px_, top - ch - 4, "#fcb468")
    # zinc mansard
    f.rect(x, top, x + w, top + 12, zinc)
    f.rect(x, top, x + w, top + 1, zhi)
    f.rect(x, top + 1, x + w, top + 2, zsh)
    for sx in range(x + 2, x + w, 5):
        f.rect(sx, top + 2, sx + 1, top + 12, zsh)
    for dx in range(x + 4, x + w - 6, 10):                    # dormers
        f.rect(dx - 1, top + 3, dx + 6, top + 4, zhi)
        f.rect(dx, top + 4, dx + 5, top + 12, stone)
        f.rect(dx + 1, top + 6, dx + 4, top + 12, win)
        f.dot(dx + 2, top + 8, "#fce8a0") if r.random() < 0.3 else None
    # stone facade
    f.rect(x, top + 12, x + w, STAGE_H, stone)
    f.rect(x, top + 12, x + w, top + 14, "#fcf4dc")
    f.rect(x, top + 14, x + w, top + 15, stone_s)
    f.rect(x + w - 3, top + 12, x + w, STAGE_H, stone_s)
    f.rect(x, top + 12, x + 1, STAGE_H, stone_s)
    row = 0
    for wy in range(top + 18, STAGE_H, 15):
        for wx in range(x + 4, x + w - 7, 8):
            f.rect(wx, wy, wx + 4, wy + 9, win)
            f.rect(wx - 1, wy, wx, wy + 9, "#88b4a8")           # shutters
            f.rect(wx + 4, wy, wx + 5, wy + 9, "#88b4a8")
        if row % 2 == 0:                                       # iron balcony line
            f.rect(x + 1, wy + 9, x + w - 3, wy + 10, "#3c3868")
            f.rect(x + 1, wy + 11, x + w - 3, wy + 12, stone_s)
        row += 1


def _far():
    f = Art(FAR_W, STAGE_H)
    f.vgrad(0, 0, FAR_W, 112, ["#3c88dc", "#58a0e8", "#78b8f0", "#90c8f4", "#b0d8f4", "#ececd8"])
    f.rect(0, 112, FAR_W, STAGE_H, "#ececd8")
    for x, y, w in ((4, 46, 26), (70, 60, 24), (118, 40, 34), (176, 62, 22), (226, 46, 30),
                    (290, 58, 26), (338, 42, 32), (420, 52, 24)):
        _cloud(f, x, y, w)
    # hazy mid-distance city
    haze = "#a8b8e4"
    r = random.Random(11)
    x = 0
    while x < FAR_W:
        w = r.randint(8, 20)
        f.rect(x, 104 - r.randint(4, 14), x + w, 130, haze)
        x += w
    f.ellipse(120, 82, 136, 104, haze)                         # a dome on the skyline
    f.rect(127, 78, 129, 84, haze)
    hill = "#7c9cc4"
    f.ellipse(350, 90, 460, 132, hill)                         # butte Montmartre
    f.rect(350, 110, 460, 132, hill)
    for hx, hy in ((366, 100), (374, 97), (384, 99), (424, 98), (434, 100), (442, 103)):
        f.rect(hx, hy, hx + 6, hy + 8, "#c8d0ec")
        f.rect(hx, hy, hx + 6, hy + 2, "#6478b0")
    _sacre_coeur(f, 405, 99)
    _eiffel(f, 43, 42, 104, "#6068ac", "#9098d0")
    # near rooftops
    r = random.Random(1949)
    x = -8
    while x < FAR_W:
        w = r.randint(30, 50)
        top = r.randint(82, 94)
        if x < 64 and x + w > 22:
            top = 101 + r.randint(0, 2)                        # keep the tower clear
        low = x < 436 and x + w > 380
        if low:
            top = 103 + r.randint(0, 2)                        # ...and the basilica
        _building(f, x, w, top, r, chimneys=not low)
        x += w
    return f


# =============================================================================
#  MAIN LAYER helpers
# =============================================================================
def _tiles(a, x0, y0, x1, y1, face, grout, s=8):
    a.rect(x0, y0, x1, y1, face)
    for x in range(x0, x1, s):
        a.rect(x, y0, x + 1, y1, grout)
    for y in range(y0, y1, s):
        a.rect(x0, y, x1, y + 1, grout)


def _gingham(a, x0, y0, x1, y1, s=2):
    for y in range(y0, y1):
        for x in range(x0, x1):
            i, j = (x // s) & 1, (y // s) & 1
            a.dot(x, y, R1 if i and j else (PK if i or j else CR0))


def _pan(a, cx, hook_y, d, hl=7, empty=False):
    """Copper pan hanging bottom-out from a hook, with Paul's painted outline."""
    top = hook_y + hl
    x0 = cx - d // 2
    a.rect(cx - 2, hook_y - 1, cx + 3, top + 1, T3)             # outline: handle
    a.ellipse(x0 - 2, top - 2, x0 + d + 2, top + d + 2, T3)     # outline: body
    if empty:
        a.rect(cx - 1, hook_y, cx + 2, top + 1, T1)
        a.ellipse(x0 - 1, top - 1, x0 + d + 1, top + d + 1, T1)
        for y in range(top, top + d, 4):                        # peg holes show through
            for x in range(x0 + 1, x0 + d - 1, 4):
                if (x - cx) ** 2 + (y - top - d // 2) ** 2 < (d // 2 - 2) ** 2:
                    a.dot(x, y, T2)
        a.rect(cx, hook_y, cx + 1, hook_y + 2, S1)              # the lonely hook
        return
    a.rect(cx - 1, hook_y, cx + 2, top + 1, D2)                 # iron handle
    a.dot(cx, hook_y + 1, S0)
    a.ellipse(x0, top, x0 + d, top + d, CO3)
    a.ellipse(x0, top, x0 + d - 1, top + d - 1, CO2)
    if d >= 12:
        a.ellipse(x0 + 2, top + 2, x0 + 2 + d // 2, top + 2 + d // 2, CO1)
        a.rect(x0 + 4, top + 4, x0 + 4 + d // 6, top + 5, CO0)
        a.rect(x0 + 4, top + 5, x0 + 5, top + 5 + d // 6, CO0)
    else:
        a.rect(x0 + 2, top + 2, x0 + 2 + d // 3, top + 3, CO1)
        a.dot(x0 + 2, top + 3, CO1)


def _lid(a, cx, hook_y, d):
    x0, top = cx - d // 2, hook_y + 2
    a.ellipse(x0 - 2, top - 2, x0 + d + 2, top + d + 2, T3)
    a.ellipse(x0, top, x0 + d, top + d, CO3)
    a.ellipse(x0, top, x0 + d - 1, top + d - 1, CO1)
    a.ellipse(x0 + 2, top + 2, x0 + d - 2, top + d - 2, CO2)
    a.rect(cx - 1, top + 2, cx + 1, top + d - 2, CO4)           # strap handle
    a.rect(cx - 1, top + 2, cx, top + d - 2, CO0)
    a.rect(cx, hook_y, cx + 1, hook_y + 2, S1)


def _pegboard(a, x0, y0, x1, y1):
    a.rect(x0 - 3, y0 - 3, x1 + 3, y1 + 3, W2)
    a.rect(x0 - 3, y0 - 3, x1 + 3, y0 - 2, W0)
    a.rect(x0 - 3, y1 + 3, x1 + 4, y1 + 5, CR3)                 # cast shadow on the wall
    a.rect(x1 + 3, y0, x1 + 5, y1 + 5, CR3)
    a.rect(x0, y0, x1, y1, T1)
    a.rect(x0, y0, x1, y0 + 2, T2)
    a.rect(x0, y0, x0 + 2, y1, T2)
    for y in range(y0 + 4, y1 - 1, 4):
        for x in range(x0 + 4, x1 - 1, 4):
            a.dot(x, y, T2)


def _cat(a, x, y):
    """Minette on the sill, eyeing the pigeon."""
    rows = [
        "k...k.........",
        "kk.kk.........",
        "kkkkk.........",
        "kykyk.........",
        "kkkkk.........",
        ".kwk..........",
        ".kwwkk........",
        ".kwwkkk.......",
        ".kwwkkkk......",
        ".kkwkkkkk.....",
        ".kkwkkkkk.....",
        ".kkkkkkkkk....",
        ".kkkkkkkkk..k.",
        ".kkkkkkkkk...k",
        ".kkkkkkkkk...k",
        ".kkkkkkkkkk..k",
        "wwkkkwwkkkkkk.",
    ]
    a.stamp(rows, {"k": K, "w": CR0, "y": Y1}, x, y)


def _pigeon(a, x, y):
    rows = [
        ".....ww.",
        "....wkwo",
        ".wwwwww.",
        "wssssww.",
        ".wsssw..",
        "...p.p..",
    ]
    a.stamp(rows, {"w": CR0, "s": S1, "k": K, "o": CO1, "p": R1}, x, y)


def _paul(a, x):
    """Paul Child on the balcony, camera round his neck, raising a glass."""
    def R(d0, y0, d1, y1, c):          # mirrored rect helper (drawn facing left)
        a.rect(x - d1 + 1, y0, x - d0 + 1, y1, c)

    R(-6, 147, -1, 150, K)                                      # shoes
    R(1, 147, 6, 150, K)
    R(-5, 124, -1, 147, D2)                                     # flannels
    R(1, 124, 5, 147, D2)
    R(-5, 124, -4, 147, K)
    R(1, 124, 2, 147, K)
    R(-7, 102, 7, 126, W1)                                      # tweed jacket
    R(4, 102, 7, 126, W2)
    R(-7, 102, -6, 126, W0)
    a.poly([(x - 2, 102), (x + 3, 102), (x, 111)], CR0)         # shirt
    R(-3, 102, 3, 104, R1)                                      # bow tie
    a.rect(x, 102, x + 1, 104, R2)
    R(-11, 104, -7, 112, W1)                                    # raised arm
    R(-12, 100, -9, 105, W1)
    R(-13, 96, -10, 100, SK)
    R(-14, 90, -9, 95, R1)                                      # glass of red
    R(-14, 89, -9, 90, CR0)
    R(-12, 95, -11, 98, CR0)
    R(7, 104, 10, 122, W2)                                      # other arm
    R(7, 122, 10, 125, SK2)
    R(-4, 113, 4, 119, K)                                       # camera
    R(-2, 114, 2, 118, S1)
    a.dot(x, 115, S0)
    a.line([(x - 3, 104), (x - 3, 113)], D2)                    # strap
    a.line([(x + 4, 104), (x + 4, 113)], D2)
    R(-2, 100, 2, 102, SK2)                                     # neck
    a.ellipse(x - 5, 88, x + 6, 101, SK)                        # head (bald)
    R(3, 91, 5, 99, SK2)
    R(-5, 93, -4, 98, S1)                                       # grey side hair
    R(5, 93, 6, 98, S1)
    R(-4, 93, 5, 94, K)                                         # glasses
    R(-3, 94, -1, 95, K)
    R(1, 94, 3, 95, K)
    R(-2, 97, 3, 98, W2)                                        # moustache


# =============================================================================
def build():
    f = _far()

    a = Art(STAGE_W, STAGE_H, mode="RGBA")
    # ---- plaster wall
    a.vgrad(0, 0, STAGE_W, WALL_Y, [CR0, CR1, CR1, CR2])
    a.rect(0, 143, STAGE_W, WALL_Y, CR3)                        # skirting
    a.rect(0, 143, STAGE_W, 144, CR0)

    # ---- FRENCH WINDOW (left): a hole onto the rooftops
    a.rect(10, 12, 102, 128, CR0)
    a.frame(10, 12, 102, 128, CR3)
    a.clear(16, 18, 96, 126)
    a.frame(15, 17, 97, 127, W2)
    #   balcony rail + geranium box, outside the glass
    a.rect(16, 108, 96, 110, D2)
    a.rect(16, 123, 96, 124, D2)
    for x in range(18, 96, 5):
        a.rect(x, 110, x + 1, 123, D2)
        if (x // 5) & 1:
            a.rect(x + 2, 115, x + 4, 116, D2)
            a.rect(x + 2, 118, x + 4, 119, D2)
    a.rect(22, 112, 90, 120, CO2)
    a.rect(22, 112, 90, 113, CO1)
    a.rect(22, 118, 90, 120, CO3)
    r = random.Random(7)
    for x in range(23, 89, 3):
        h = r.randint(3, 8)
        if 58 <= x < 80:
            h = 1
        a.rect(x, 112 - h, x + 3, 112, G2)
        a.rect(x, 112 - h, x + 2, 112 - h + 2, G1)
        if r.random() < 0.6 and h > 1:
            a.rect(x, 110 - h, x + 2, 112 - h, R1)
            a.dot(x, 110 - h, PK)
    #   muntins
    a.rect(55, 18, 58, 126, CR0)
    a.rect(57, 18, 58, 126, CR3)
    for y in (52, 88):
        a.rect(16, y, 96, y + 2, CR0)
        a.rect(16, y + 2, 96, y + 3, CR3)
    #   gingham valance + tied-back drapes
    _gingham(a, 16, 18, 96, 27)
    for x in range(16, 96):
        if (x // 4) & 1:
            _gingham(a, x, 27, x + 1, 29)
    for y in range(27, 126):
        if y < 74:
            w = 12 - (y - 27) * 6 // 47
        elif y < 78:
            w = 5
        else:
            w = 6 + (y - 78) * 5 // 48
        for x0, x1 in ((16, 16 + w), (96 - w, 96)):
            a.rect(x0, y, x1, y + 1, Y1 if not 74 <= y < 78 else R1)
        if not 74 <= y < 78:
            for k in range(2, w, 3):
                a.dot(16 + k, y, W0)
                a.dot(95 - k, y, W0)
            a.dot(16 + w - 1, y, W1)
            a.dot(96 - w, y, W1)
    _pigeon(a, 31, 102)
    _cat(a, 62, 109)
    #   sill + radiator
    a.rect(6, 126, 106, 130, CR0)
    a.rect(6, 129, 106, 130, CR3)
    a.rect(8, 130, 104, 131, W2)
    for x in range(22, 90, 4):
        a.rect(x, 134, x + 3, 147, CR0)
        a.rect(x + 2, 134, x + 3, 147, CR3)
    a.rect(22, 133, 90, 134, CR0)
    a.rect(22, 147, 90, 148, W2)
    a.rect(20, 138, 22, 140, W2)

    # ---- wall strip: garlic + onion braids, the Valentine's card
    for bx, n, kind in ((112, 8, "garlic"), (123, 7, "onion")):
        a.rect(bx, 16, bx + 1, 22 + n * 6, W1)
        a.rect(bx - 1, 15, bx + 2, 17, D2)
        for i in range(n):
            ox = bx - 4 if i & 1 else bx - 1
            oy = 22 + i * 6
            if kind == "garlic":
                a.ellipse(ox, oy, ox + 6, oy + 7, CR3)
                a.ellipse(ox, oy, ox + 5, oy + 6, CR0)
                a.dot(ox + 2, oy + 6, W2)
            else:
                red = i in (2, 5)
                a.ellipse(ox, oy, ox + 6, oy + 7, R2 if red else CO3)
                a.ellipse(ox, oy, ox + 5, oy + 6, R1 if red else CO1)
                a.dot(ox + 1, oy + 1, PK if red else CO0)
    #   framed Valentine: Julia & Paul in the bubble bath
    a.rect(131, 42, 151, 62, W2)
    a.rect(132, 43, 150, 61, CR0)
    a.rect(134, 45, 148, 59, R1)
    a.rect(134, 54, 148, 59, CR0)
    for bx in (135, 139, 143):
        a.rect(bx, 53, bx + 3, 54, CR0)
    a.rect(136, 49, 140, 54, SK)
    a.rect(136, 48, 140, 50, W2)
    a.rect(142, 49, 146, 54, SK)
    a.rect(142, 51, 146, 52, K)
    a.rect(139, 46, 140, 47, CR0)
    a.rect(141, 46, 142, 47, CR0)
    a.rect(139, 47, 142, 48, CR0)
    a.dot(140, 48, CR0)

    # ---- PEGBOARD with the copper batterie de cuisine
    _pegboard(a, 157, 15, 369, 93)
    x = 176
    for d in (26, 23, 20, 17, 15, 13, 11, 9):
        _pan(a, x, 19, d, hl=6)
        x += d + 7 + (2 if d > 15 else 0)
    #   lower row, left: utensils
    hy = 58
    a.rect(165, hy, 166, hy + 2, S1)
    a.rect(164, hy + 1, 167, hy + 10, W2)                       # whisk
    for dx in (-3, -1, 1, 3):
        a.line([(165, hy + 10), (165 + dx, hy + 18), (165 + dx, hy + 24), (165, hy + 28)], S0)
    a.rect(178, hy, 179, hy + 20, S1)                           # ladle
    a.ellipse(174, hy + 18, 183, hy + 27, CO3)
    a.ellipse(174, hy + 18, 182, hy + 26, CO1)
    a.rect(176, hy + 20, 178, hy + 21, CO0)
    a.rect(190, hy, 193, hy + 9, W2)                            # cleaver
    a.rect(188, hy + 9, 198, hy + 25, S1)
    a.rect(188, hy + 9, 190, hy + 25, S0)
    a.rect(188, hy + 24, 198, hy + 25, S2)
    a.dot(195, hy + 12, T1)
    a.rect(206, hy, 207, hy + 10, S1)                           # sieve
    a.ellipse(201, hy + 9, 213, hy + 21, S2)
    a.ellipse(202, hy + 10, 212, hy + 20, S1)
    a.dither(203, hy + 11, 211, hy + 19, S2, 0.5)
    #   centre: enamel plaque
    a.rect(219, 61, 309, 79, R2)
    a.rect(220, 62, 308, 78, CR0)
    a.frame(221, 63, 307, 77, R1)
    a.text((264, 67), "BON APPETIT!", R1, bold=True, align="center")
    a.rect(221, 60, 223, 62, S1)
    a.rect(305, 60, 307, 62, S1)
    #   lower row, right: the pan that's on the stove (outline only), lids, fish mould
    _pan(a, 324, 58, 17, hl=6, empty=True)
    _lid(a, 345, 58, 13)
    _lid(a, 361, 58, 10)
    a.ellipse(338, 79, 358, 90, T3)                             # copper fish mould
    a.poly([(355, 84), (364, 79), (364, 90)], T3)
    a.ellipse(339, 80, 357, 89, CO2)
    a.poly([(355, 84), (362, 81), (362, 88)], CO2)
    a.ellipse(340, 81, 352, 86, CO1)
    a.dot(343, 83, CO4)
    for sx in (347, 350, 353):
        a.line([(sx, 82), (sx + 1, 84), (sx, 87)], CO3)
    a.rect(342, 82, 346, 83, CO0)

    # ---- backsplash, butcher-block counter, sage cabinets
    _tiles(a, 108, 97, 376, 112, CR0, CR2, 8)
    a.rect(108, 96, 376, 97, CR3)
    a.rect(108, 117, 376, 146, SG1)
    for i in range(8):
        x = 110 + i * 33
        a.rect(x, 117, x + 1, 146, SG3)
        a.rect(x + 3, 119, x + 31, 126, SG1)                    # drawer
        a.rect(x + 3, 119, x + 31, 120, SG0)
        a.rect(x + 3, 125, x + 31, 126, SG2)
        a.rect(x + 30, 119, x + 31, 126, SG2)
        a.rect(x + 14, 121, x + 20, 123, CO1)
        a.rect(x + 14, 123, x + 20, 124, CO3)
        a.rect(x + 3, 128, x + 31, 145, SG1)                    # door
        a.rect(x + 3, 128, x + 31, 129, SG0)
        a.rect(x + 3, 144, x + 31, 145, SG2)
        a.rect(x + 30, 128, x + 31, 145, SG2)
        a.frame(x + 6, 131, x + 28, 142, SG2)
        a.rect(x + 7, 141, x + 28, 142, SG0)
        a.rect(x + 27, 132, x + 28, 142, SG0)
        kx = x + 25 if i & 1 else x + 8
        a.rect(kx, 135, kx + 2, 138, CO1)
        a.dot(kx + 1, 137, CO3)
    a.rect(374, 117, 376, 146, SG3)
    a.rect(108, 117, 110, 146, SG3)
    a.rect(108, 146, 376, WALL_Y, SG3)                          # toe kick
    a.rect(106, 112, 378, 113, CO0)                             # counter top
    a.rect(106, 113, 378, 116, W0)
    a.rect(106, 116, 378, 117, W2)
    for x in range(110, 378, 7):
        a.rect(x, 113, x + 1, 116, W1)
    a.rect(108, 117, 376, 118, SG3)

    # ---- things on the counter
    #   baguettes in a basket
    for bx, by, ln in ((114, 86, 22), (119, 82, 26), (125, 88, 20)):
        for i in range(ln):
            x = bx + i * 5 // ln
            a.rect(x, by + i, x + 4, by + i + 1, W0)
            a.dot(x, by + i, CO0)
            a.dot(x + 3, by + i, W1)
            if i % 5 == 2:
                a.rect(x + 1, by + i, x + 3, by + i + 1, W1)
        a.rect(bx + 1, by - 1, bx + 3, by, W0)
    a.rect(111, 103, 133, 112, W1)
    a.dither(111, 104, 133, 112, W2, 0.5)
    a.rect(110, 102, 134, 104, W0)
    a.rect(110, 104, 134, 105, W2)
    #   mixing bowl of egg whites + whisk
    a.line([(146, 99), (153, 84)], S2)
    a.line([(147, 99), (154, 84)], S1)
    a.rect(153, 81, 156, 85, W2)
    a.rect(140, 97, 150, 101, CR0)
    a.rect(142, 95, 147, 97, CR0)
    a.dot(144, 94, CR0)
    a.rect(148, 99, 150, 101, S0)
    a.poly([(137, 101), (155, 101), (151, 111), (141, 111)], Y1)
    a.rect(137, 101, 156, 102, CR0)
    a.rect(139, 105, 154, 107, CR0)
    a.poly([(152, 102), (155, 102), (151, 111), (149, 111)], W0)
    a.rect(141, 111, 152, 112, W1)
    #   roast chicken
    a.ellipse(165, 106, 199, 113, S1)
    a.ellipse(166, 105, 198, 111, CR0)
    a.ellipse(171, 96, 193, 110, CO3)
    a.ellipse(171, 96, 192, 108, CO1)
    a.ellipse(174, 97, 185, 103, CO0)
    a.rect(190, 96, 194, 100, CO1)                              # drumsticks
    a.rect(193, 93, 196, 97, CO1)
    a.rect(195, 91, 198, 94, CR0)
    a.rect(186, 94, 190, 98, CO2)
    a.rect(188, 91, 191, 95, CO2)
    a.rect(190, 89, 193, 92, CR0)
    for gx in (167, 170, 194, 196):
        a.rect(gx, 107, gx + 2, 109, G1)
    a.dot(169, 108, R1)
    a.dot(195, 109, R1)
    #   vin rouge
    for bx, top in ((207, 88), (214, 91)):
        a.rect(bx, top + 8, bx + 6, 112, BT)
        a.rect(bx + 2, top, bx + 4, top + 9, BT)
        a.rect(bx + 1, top + 6, bx + 5, top + 8, BT)
        a.rect(bx + 2, top, bx + 4, top + 3, R2)
        a.rect(bx, top + 12, bx + 6, top + 18, CR0)
        a.rect(bx + 1, top + 14, bx + 5, top + 15, R1)
        a.rect(bx + 1, top + 9, bx + 2, top + 12, G2)
    a.rect(224, 100, 231, 101, S1)                              # a poured glass
    a.rect(224, 101, 231, 106, R1)
    a.rect(224, 101, 225, 106, S1)
    a.rect(230, 101, 231, 106, S1)
    a.rect(225, 106, 230, 107, S1)
    a.rect(227, 107, 228, 111, S1)
    a.rect(225, 111, 230, 112, S1)
    #   never enough butter
    for i, bx in enumerate((241, 244, 240)):
        y = 104 - i * 8
        a.rect(bx, y, bx + 29, y + 8, Y1)
        a.rect(bx, y, bx + 29, y + 1, CR0)
        a.rect(bx, y + 7, bx + 29, y + 8, W0)
        a.rect(bx + 28, y, bx + 29, y + 8, W0)
        a.text((bx + 3, y + 2), "BEURRE", R1, tiny=True)
    #   THE cookbook
    a.rect(279, 87, 312, 112, T2)
    a.rect(281, 87, 313, 112, CR0)
    a.rect(281, 87, 313, 88, T0)
    a.rect(312, 88, 313, 112, CR3)
    for fy in range(90, 111, 4):
        for fx in range(283 + (fy // 4 & 1) * 2, 311, 4):
            a.dot(fx, fy, T1)
    a.rect(283, 92, 311, 106, CR0)
    a.text((297, 93), "FRENCH", R1, tiny=True, align="center")
    a.text((297, 100), "COOKING", R1, tiny=True, align="center")
    #   flame-orange cocotte of boeuf bourguignon
    a.rect(322, 102, 348, 112, OR)
    a.rect(322, 102, 326, 112, CO1)
    a.rect(344, 102, 348, 112, R2)
    a.rect(320, 104, 322, 107, OR)
    a.rect(348, 104, 350, 107, R2)
    a.rect(321, 99, 349, 102, OR)
    a.rect(321, 99, 349, 100, CO1)
    a.rect(321, 101, 349, 102, R2)
    a.rect(333, 96, 337, 99, K)
    a.rect(333, 96, 335, 97, D3)
    #   marble mortar + pestle
    a.line([(362, 100), (370, 88)], W2)
    a.line([(363, 100), (371, 88)], W1)
    a.line([(364, 100), (372, 88)], W1)
    a.poly([(356, 99), (372, 99), (369, 111), (359, 111)], S1)
    a.rect(355, 98, 373, 100, S0)
    a.poly([(368, 100), (372, 100), (369, 111), (366, 111)], S2)
    a.rect(358, 111, 370, 112, S2)

    # ---- THE RANGE under its copper hood
    _tiles(a, 378, 57, 446, 104, T0, T1, 8)
    a.rect(402, 9, 422, 28, CO2)                                # flue
    a.rect(402, 9, 406, 28, CO1)
    a.rect(418, 9, 422, 28, CO3)
    a.rect(402, 19, 422, 21, CO3)
    a.poly([(390, 28), (434, 28), (449, 50), (375, 50)], CO2)
    a.poly([(390, 28), (397, 28), (385, 50), (375, 50)], CO1)
    a.poly([(427, 28), (434, 28), (449, 50), (438, 50)], CO3)
    a.line([(393, 31), (384, 47)], CO0)
    a.rect(390, 28, 435, 29, CO0)
    a.rect(374, 50, 451, 57, CO3)
    a.rect(374, 50, 451, 51, CO1)
    a.rect(374, 56, 451, 57, CO4)
    for x in range(378, 450, 8):
        a.dot(x, 53, CO0)
        a.dot(x, 54, CO4)
    #   utensil rail
    a.rect(416, 63, 446, 64, S2)
    a.rect(421, 64, 422, 80, S0)
    a.ellipse(418, 78, 426, 86, S2)
    a.ellipse(418, 78, 425, 85, S0)
    a.rect(430, 64, 431, 75, S0)
    a.rect(428, 75, 434, 85, S0)
    a.rect(429, 77, 430, 83, T1)
    a.rect(432, 77, 433, 83, T1)
    a.rect(440, 64, 441, 80, S0)
    a.rect(438, 80, 439, 86, S0)
    a.rect(440, 80, 441, 86, S0)
    a.rect(442, 80, 443, 86, S0)
    a.rect(438, 79, 443, 80, S0)
    #   steam
    for cx, ph, y0 in ((387, 0.0, 60), (396, 2.2, 59), (405, 4.0, 62)):
        for y in range(y0, 76):
            sx = cx + int(round(2.2 * math.sin(y / 2.4 + ph)))
            a.rect(sx, y, sx + 2, y + 1, CR0)
    #   stock pot with tonight's lobster
    a.rect(384, 91, 408, 110, S1)
    a.rect(386, 91, 389, 110, S0)
    a.rect(403, 91, 408, 110, S2)
    a.rect(383, 89, 409, 92, S0)
    a.rect(383, 91, 409, 92, S2)
    a.rect(380, 96, 384, 99, S2)
    a.rect(408, 96, 412, 99, S2)
    claw = [".rr...r.", "rrr..rr.", "rrr.rrr.", "rrrrrrr.", "rrddddr.", ".rrrrd..", "..rrd...", "..rrd...", "..rrd..."]
    lp = {"r": R1, "d": R2}
    a.stamp(claw, lp, 384, 80)
    a.stamp(claw + claw[-1:], lp, 400, 79, flip=True)
    a.rect(393, 85, 399, 89, R1)                                # head
    a.rect(393, 88, 399, 89, R2)
    a.dot(394, 84, K)
    a.dot(397, 84, K)
    a.line([(394, 83), (392, 78)], R2)                          # feelers
    a.line([(397, 83), (399, 77)], R2)
    #   skillet + a flipped omelette
    a.rect(418, 106, 437, 110, K)
    a.rect(418, 106, 437, 107, S2)
    a.rect(437, 106, 446, 108, K)
    a.rect(422, 95, 433, 98, Y1)
    a.rect(424, 94, 431, 95, Y1)
    a.rect(423, 95, 429, 96, CR0)
    a.rect(424, 98, 432, 99, W0)
    for dx in (421, 427, 433):
        a.rect(dx, 101, dx + 1, 104, CR0)
    #   the range itself
    a.rect(378, 104, 446, 110, D2)
    a.rect(378, 104, 446, 105, S1)
    a.rect(376, 110, 448, 112, S0)
    a.rect(376, 112, 448, 114, S1)
    a.rect(378, 114, 446, WALL_Y, RG)
    a.rect(378, 115, 446, 122, S1)
    a.rect(378, 115, 446, 116, S0)
    a.rect(378, 121, 446, 122, S2)
    for kx in (383, 394, 405, 425, 436):
        a.rect(kx, 117, kx + 4, 121, K)
        a.dot(kx + 1, 118, R1)
    a.rect(414, 117, 420, 121, CR0)                             # oven clock
    a.dot(416, 118, K)
    a.dot(417, 119, K)
    a.frame(382, 125, 418, 146, D3)                             # big oven
    a.rect(386, 127, 414, 129, S0)
    a.rect(386, 129, 414, 130, S2)
    a.rect(388, 133, 412, 143, K)
    a.rect(390, 135, 410, 141, CO4)
    a.rect(394, 138, 406, 141, CO3)
    a.rect(397, 139, 403, 141, CO1)
    a.frame(421, 125, 443, 146, D3)                             # warming oven
    a.rect(424, 127, 440, 129, S0)
    a.rect(424, 129, 440, 130, S2)
    a.frame(425, 133, 439, 143, D2)
    a.rect(378, 146, 446, WALL_Y, K)
    a.rect(380, 146, 384, WALL_Y, S2)
    a.rect(440, 146, 444, WALL_Y, S2)

    # ---- BALCONY DOOR (right): second hole, with Paul looking in
    a.rect(451, 30, 509, WALL_Y, CR0)
    a.frame(451, 30, 509, WALL_Y + 1, CR3)
    a.clear(456, 36, 504, WALL_Y)
    a.frame(455, 35, 505, WALL_Y + 1, W2)
    a.rect(456, 118, 504, 120, D3)                              # balcony rail
    a.rect(456, 145, 504, 146, D3)
    for x in range(458, 504, 5):
        a.rect(x, 120, x + 1, 145, D3)
        if (x // 5) & 1:
            a.rect(x + 2, 128, x + 4, 129, D3)
            a.rect(x + 2, 134, x + 4, 135, D3)
    a.rect(456, 146, 504, WALL_Y, CR3)                          # stone threshold
    a.rect(456, 146, 504, 147, CR0)
    a.rect(456, 36, 504, 38, CR0)
    a.rect(456, 38, 504, 39, CR3)
    _gingham(a, 456, 39, 504, 46)
    _paul(a, 487)

    # ---- ceiling beams
    a.rect(0, 0, STAGE_W, 7, W1)
    a.rect(0, 0, STAGE_W, 1, W0)
    a.rect(0, 7, STAGE_W, 9, W2)
    a.rect(0, 9, STAGE_W, 10, CR3)
    for x in range(28, STAGE_W, 64):
        if 396 < x < 428:
            continue
        a.rect(x, 0, x + 9, 12, W2)
        a.rect(x, 0, x + 2, 12, W1)
        a.rect(x, 12, x + 9, 13, CO4)

    # ---- floor: terracotta + cream checker
    floor_checker(a, WALL_Y, STAGE_H, F1, F2)
    a.dither(0, WALL_Y, STAGE_W, WALL_Y + 8, F3, 0.5)
    a.dither(0, WALL_Y + 8, STAGE_W, WALL_Y + 20, F3, 0.25)
    a.rect(0, WALL_Y, STAGE_W, WALL_Y + 2, D2)
    return f.im, a.im
