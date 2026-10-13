"""ST. NICHOLAS CHURCH - The Bronx.  Sister Aloysius's stage (Doubt, 1964).

The nave, looking at the altar.  `main` is the nave wall (lancet windows and
the chancel arch are holes); `far` is a wall of stained glass plus the starry
apse with its rose window, so the glass drifts behind the stone tracery.

Layout notes for the integrator
  * wall / floor line  y = 150 (WALL_Y); pews stack up from y = 141..171 on
    both sides, the centre aisle (x ~ 180..332) is clear.
  * lancet centres are all = 16 (mod 32) and the saints on `far` sit on a
    32px pitch, so they are centred at camera 0 / 64 / 128.
"""
import math
import random

from bg import BAYER, Art
from px import rgb
from stages import FAR_W, STAGE_H, STAGE_W, WALL_Y, floor_checker

W, H = STAGE_W, STAGE_H
CX = 256
VY = 110                                   # floor vanishing line
WINS = (48, 144, 368, 464)                 # lancet window centres
COLS = (-6, 90, 186, 314, 410, 506)        # column left edges (12px wide)

# ---- stained glass (far layer)
LEAD = "#201840"
RUBY, RUBY_L = "#d0203c", "#f8607c"
COB, COB_L = "#2040c0", "#4c8cf0"
EME, EME_L = "#109860", "#58d888"
AMB, AMB_L = "#f09c20", "#fcd458"
VIO, VIO_L = "#8434bc", "#b870e8"
PALE = "#fcf4c0"
SKIN = "#fcd0a0"

# ---- nave (main layer)
S0, S1, S2, S3, S4, S5 = "#fcf4dc", "#f0e4c8", "#dcccac", "#c0a8b0", "#8c7ca0", "#5c5088"
DK = "#342c5c"
V0, V1, V2 = "#241c50", "#3c3478", "#54488c"
W1, W2, W3, W4 = "#d8a058", "#b07038", "#7c4434", "#4c2c3c"
G0, G1, G2 = "#fcf0a0", "#f8cc50", "#c88428"
R1, R2, R3 = "#e85064", "#c02840", "#8c1c3c"
C0, C1 = "#fcf8e8", "#d8d0e4"
F2 = "#c8b8c0"
LR, LA, LB, LG = "#f89098", "#fcd870", "#88b0f0", "#90dca0"
P1, P2, P3 = "#b060a8", "#84388c", "#582868"
B1, B2 = "#6c94e8", "#3454c0"
N1, N2 = "#58b868", "#2c7c58"
K1, K2 = "#f4c8a0", "#b87850"
O1, O2 = "#f08830", "#b04820"
INK = "#2c2444"


# ------------------------------------------------------------------ helpers
def arch_hw(w, rise, h):
    """Half-width of a two-centred pointed arch (half-span w) at height h above the springing."""
    k = (rise * rise - w * w) / (2.0 * w)
    v = (w + k) ** 2 - h * h
    return max(0, int(round(math.sqrt(v) - k))) if v > 0 else 0


def arch(a, cx, w, spring, apex, bottom, col):
    """Fill (col=None: punch out) a pointed-arch opening, mirror-exact about cx."""
    def row(x0, y, x1):
        if col is None:
            a.clear(x0, y, x1, y + 1)
        else:
            a.rect(x0, y, x1, y + 1, col)
    for y in range(apex, spring):
        hw = arch_hw(w, spring - apex, spring - y)
        if hw:
            row(cx - hw, y, cx + hw)
    for y in range(spring, bottom):
        row(cx - w, y, cx + w)


def disc(a, cx, cy, r, col):
    for y in range(int(cy - r) - 1, int(cy + r) + 2):
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 < r * r:
                a.dot(x, y, col)


def tint(a, x0, y0, x1, y1, level, cmap, default=None, inside=None):
    """Bayer-dither a light pool: recolour pixels through cmap (or to default)."""
    cmap = {rgb(k): a.c(v) for k, v in cmap.items()}
    for y in range(max(y0, 0), min(y1, a.h)):
        for x in range(max(x0, 0), min(x1, a.w)):
            if inside and not inside(x, y):
                continue
            if level * 16 > BAYER[y & 3][x & 3] + 0.5:
                new = cmap.get(tuple(a.p[x, y][:3]), a.c(default) if default else None)
                if new:
                    a.p[x, y] = new


# ------------------------------------------------------------------ far layer
def saint(f, cx, kind, robe, robe_l, trim):
    """A 20px-wide leaded saint, feet on y=90."""
    disc(f, cx, 54, 7.5, LEAD)                       # halo
    disc(f, cx, 54, 6.5, AMB_L)
    disc(f, cx, 54, 4.6, PALE)
    for y in range(58, 90):                          # robe
        hw = min(8, 4 + (y - 58)) if y < 61 else 6 + (y - 60) // 12
        f.rect(cx - hw - 1, y, cx + hw + 1, y + 1, LEAD)
        f.rect(cx - hw, y, cx + hw, y + 1, robe)
        f.rect(cx - hw, y, cx - hw + 2, y + 1, robe_l)
    f.rect(cx - 2, 60, cx + 2, 90, trim)             # stole / tunic
    f.rect(cx - 3, 62, cx - 2, 90, LEAD)
    f.rect(cx + 2, 62, cx + 3, 90, LEAD)
    f.rect(cx - 8, 76, cx - 3, 77, LEAD)             # leading across the robe
    f.rect(cx + 3, 76, cx + 8, 77, LEAD)
    f.rect(cx - 4, 50, cx + 4, 59, LEAD)             # head
    f.rect(cx - 3, 51, cx + 3, 58, SKIN)
    f.dot(cx - 2, 54, LEAD)
    f.dot(cx + 1, 54, LEAD)
    f.rect(cx - 1, 56, cx + 1, 57, RUBY)
    f.rect(cx - 2, 67, cx + 2, 70, SKIN)             # hands
    f.rect(cx - 2, 70, cx + 2, 71, LEAD)
    if kind == 0:                                    # St. Nicholas: mitre + crozier
        for i in range(5):
            f.rect(cx - 1 - i, 47 + i, cx + 1 + i, 48 + i, LEAD)
        for i in range(4):
            f.rect(cx - 1 - i, 48 + i, cx + 1 + i, 49 + i, PALE)
        f.rect(cx - 1, 48, cx + 1, 52, RUBY)
        f.rect(cx - 3, 58, cx + 3, 60, PALE)         # beard
        f.rect(cx + 8, 53, cx + 9, 90, PALE)
        f.rect(cx + 6, 51, cx + 9, 52, PALE)
        f.dot(cx + 6, 52, PALE)
        f.dot(cx + 6, 53, PALE)
    elif kind == 1:                                  # the Virgin: veil
        f.rect(cx - 4, 50, cx + 4, 53, robe)
        f.rect(cx - 4, 53, cx - 3, 59, robe)
        f.rect(cx + 3, 53, cx + 4, 59, robe)
    elif kind == 2:                                  # friar: tonsure + book
        f.rect(cx - 3, 51, cx + 3, 52, "#7c4434")
        f.rect(cx - 3, 52, cx - 2, 54, "#7c4434")
        f.rect(cx + 2, 52, cx + 3, 54, "#7c4434")
        f.rect(cx + 2, 64, cx + 7, 71, LEAD)
        f.rect(cx + 3, 65, cx + 6, 70, PALE)
    else:                                            # martyr: long hair + palm
        f.rect(cx - 3, 51, cx + 3, 53, AMB)
        f.rect(cx - 4, 53, cx - 3, 60, AMB)
        f.rect(cx + 3, 53, cx + 4, 60, AMB)
        f.rect(cx - 8, 56, cx - 7, 76, EME_L)
        f.dot(cx - 9, 57, EME_L)
        f.dot(cx - 6, 59, EME_L)
        f.dot(cx - 9, 61, EME_L)


SAINTS = (  # kind, robe, robe light, trim  (even bays have a cobalt ground, odd bays ruby)
    (2, EME, EME_L, AMB_L), (1, COB, COB_L, PALE), (0, RUBY, RUBY_L, AMB_L), (3, VIO, VIO_L, PALE),
)


def glass_panel(f, k):
    """One 32px bay of the glass wall: roundel head, saint light, base panes."""
    x0, cx = 32 * k, 32 * k + 16
    odd = k & 1
    ground, ground_l = ((COB, COB_L), (RUBY, RUBY_L))[odd]
    head, head_l = ((RUBY, RUBY_L), (COB, COB_L))[odd]
    kind, robe, robe_l, trim = SAINTS[k % 4]
    # arch head: diamond quarries + roundel
    f.vgrad(x0, 0, x0 + 32, 40, [head, head, head_l, head])
    for y in range(0, 40):
        for x in range(x0, x0 + 32):
            if (x - cx + y) % 8 == 0 or (x - cx + 1 - y) % 8 == 0:
                f.dot(x, y, LEAD)
    disc(f, cx, 29, 10.5, LEAD)
    disc(f, cx, 29, 9.5, AMB_L)
    disc(f, cx, 29, 7.5, LEAD)
    disc(f, cx, 29, 6.5, (EME, VIO)[odd])
    f.rect(cx - 1, 24, cx + 1, 34, PALE)
    f.rect(cx - 5, 28, cx + 5, 30, PALE)
    f.rect(cx - 1, 28, cx + 1, 30, (AMB, RUBY_L)[odd])
    # saint light
    f.vgrad(x0, 44, x0 + 32, 90, [ground, ground_l, ground_l, ground])
    for y in (56, 68, 80):
        f.rect(x0 + 6, y, x0 + 26, y + 1, LEAD)
    saint(f, cx, kind, robe, robe_l, trim)
    # bands
    f.rect(x0, 40, x0 + 32, 45, LEAD)
    f.rect(x0, 41, x0 + 32, 44, AMB_L)
    for x in range(x0 + 2, x0 + 32, 4):
        f.rect(x, 42, x + 2, 43, RUBY)
    f.rect(x0, 90, x0 + 32, 112, LEAD)
    for i, x in enumerate(range(cx - 12, cx + 12, 8)):
        f.rect(x + 1, 91, x + 8, 98, (EME, AMB_L, (VIO, COB)[odd])[i])
        f.rect(x + 1, 99, x + 8, 112, ground)
    # side borders (two of them make the "mullion" between saints)
    c1, c2 = ((AMB_L, EME), (AMB_L, VIO))[odd]
    for bx0, bx1 in ((x0 + 1, x0 + 5), (x0 + 27, x0 + 32)):
        f.rect(bx0 - 1, 0, bx1 + 1, 112, LEAD)
        for j, y in enumerate(range(-2, 112, 6)):
            f.rect(bx0, y + 1, bx1, y + 6, c1 if j & 1 else c2)
    f.rect(x0, 0, x0 + 1, 112, LEAD)


def rose(f, cx, cy):
    """Rose window: 16 outer lights, 8 petals, amber eye."""
    outer = (RUBY, AMB_L, COB_L, EME_L)
    inner = (COB, RUBY_L)
    for y in range(cy - 20, cy + 20):
        for x in range(cx - 20, cx + 20):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            d = math.hypot(dx, dy)
            if d >= 18.5:
                continue
            ang = (math.atan2(dy, dx) + math.pi) / (2 * math.pi)
            if d >= 17.5:
                col = "#3c3478"
            elif d >= 15.6:
                col = "#b0a4dc"
            elif d >= 14.6 or 8.2 <= d < 9.4 or 2.6 <= d < 3.6:
                col = LEAD
            elif d >= 9.4:
                t = ang * 16
                col = LEAD if abs(t - round(t)) * d * 0.39 < 0.55 else outer[int(t) % 4]
            elif d >= 3.6:
                t = ang * 8 + 0.5
                col = LEAD if abs(t - round(t)) * d * 0.78 < 0.55 else inner[int(t) % 2]
            else:
                col = AMB_L
            f.dot(x, y, col)


def build_far():
    f = Art(FAR_W, H, LEAD)
    for k in range(FAR_W // 32):
        glass_panel(f, k)
    # the apse, seen through the chancel arch: starry blue vault + rose window
    ax0, ax1, acx = 164, 284, 224
    f.vgrad(ax0, 0, ax1, 66, ["#241c5c", "#30287c", "#40389c", "#4c44a8"])
    f.rect(ax0, 66, ax1, 112, "#5c50a8")
    for j, y in enumerate(range(6, 64, 8)):                      # gilt stars
        for x in range(ax0 + 6 + (j & 1) * 6, ax1 - 4, 12):
            f.dot(x, y, AMB_L)
            if (x + j) % 5 == 0:
                f.dot(x - 1, y, AMB)
                f.dot(x + 1, y, AMB)
                f.dot(x, y - 1, AMB)
                f.dot(x, y + 1, AMB)
    for px0 in (acx - 30, acx + 27):                             # wall shafts
        f.rect(px0, 0, px0 + 3, 112, "#8478c8")
        f.rect(px0 + 2, 0, px0 + 3, 112, "#3c3478")
    f.rect(ax0, 64, ax1, 67, "#8478c8")                          # string course
    f.rect(ax0, 67, ax1, 68, "#3c3478")
    for x in range(ax0 + 8, ax1 - 4, 12):                        # blind arcade under it
        f.rect(x, 74, x + 1, 112, "#4c44a8")
        f.rect(x + 1, 72, x + 7, 73, "#4c44a8")
        f.rect(x + 7, 74, x + 8, 112, "#4c44a8")
    rose(f, acx, 44)
    for ex in (ax0, ax1 - 4):                                    # apse jambs
        f.rect(ex, 0, ex + 4, 112, "#8478c8")
        f.rect(ex + (3 if ex == ax0 else 0), 0, ex + (4 if ex == ax0 else 1), 112, "#3c3478")
    f.rect(0, 112, FAR_W, H, LEAD)
    return f


# ------------------------------------------------------------------ main-layer props
ALTAR_BOY = [
    "...hhh...",
    "..hhhhh..",
    "..hsssh..",
    "..sksks..",
    "..sssss..",
    "...sss...",
    ".wwwwwww.",
    "wwwwwwwww",
    "wwwwwwwww",
    "wwwssswww",
    "wwwssswww",
    "wwwwwwwww",
    ".wwwwwww.",
    ".wwwwwww.",
    ".WwWwWwW.",
    ".rrrrrrr.",
    ".rrrrrrr.",
    ".rRrrrRr.",
    ".rRrrrRr.",
    ".rRrrrRr.",
    ".rrrrrrr.",
    ".rrrrrrr.",
    ".rrrrrrr.",
    "..kk.kk..",
]

NUN = [
    "...kkkkk...",
    "..kkkkkkk..",
    ".kkkkkkkkk.",
    ".kssssskkk.",
    ".ksesesKkk.",
    ".kssssskkk.",
    ".kkssskkkk.",
    "..kwwwwkk..",
    ".kkkwwkkkk.",
    "kkkkkkkkkkk",
    "kkKkkkkkKkk",
    "kkKkkkkkKkk",
    "kkKkkkkkKkk",
    "kkKksssKkkk",
    "kkkksssKkkk",
    ".kkkkgkkkk.",
    ".kkkkgkkkk.",
    ".kkkgggkkk.",
    ".kkkkgkkkk.",
    ".kkkkkkkkk.",
    ".kkKkkkKkk.",
    ".kkKkkkKkk.",
    ".kkKkkkKkk.",
    ".kkKkkkKkk.",
    ".kkKkkkKkk.",
    ".kkKkkkKkk.",
    ".kkKkkkKkk.",
    ".kkKkkkKkk.",
    "kkkKkkkKkkk",
    "kkkKkkkKkkk",
    "kkkKkkkKkkk",
    "kkkKkkkKkkk",
    "kkkKkkkKkkk",
    "kkkKkkkKkkk",
    "kkkkkkkkkkk",
    "kkkkkkkkkkk",
    "kkkkkkkkkkk",
    "kkkkkkkkkkk",
]

MARY = [
    "...wwww...",
    "..wwwwww..",
    "..wsssww..",
    "..wsssww..",
    "..bwsswb..",
    ".bbwwwwbb.",
    ".bbwwwwbb.",
    ".bbwsswbb.",
    ".bbwsswbb.",
    ".bBwwwwBb.",
    ".bBwwwwBb.",
    ".bBwwwwBb.",
    ".bBwwwwBb.",
    ".bBwwwwBb.",
    ".bbwwwwbb.",
    ".bbwwwwbb.",
    ".bbwWWwbb.",
    "bbbwWWwbbb",
    "bbbwWWwbbb",
    "bbbwWWwbbb",
    "bbbWWWWbbb",
    "bbbWWWWbbb",
]

LEAF = [
    "....oo.",
    "..oooyo",
    ".ooyyo.",
    "ooyoo..",
    "dyoo...",
    "d......",
]


def pendant(a, x, top, lit=True):
    """Bare-bulb pendant lamp; the dead one is the film's blown light bulb."""
    if lit:
        tint(a, x - 9, top - 4, x + 10, top + 16, 0.5, {}, G0,
             inside=lambda px_, py: (px_ + 0.5 - x - 0.5) ** 2 + (py - top - 7) ** 2 < 30)
        tint(a, x - 9, top - 4, x + 10, top + 16, 0.25, {}, G0,
             inside=lambda px_, py: (px_ + 0.5 - x - 0.5) ** 2 + (py - top - 7) ** 2 < 72)
    a.rect(x, 0, x + 1, top, DK)                     # cord
    a.rect(x - 1, top, x + 2, top + 2, DK)           # socket
    a.rect(x - 3, top + 2, x + 4, top + 3, S5)       # enamel shade
    a.rect(x - 4, top + 3, x + 5, top + 4, DK)
    if lit:
        a.rect(x - 1, top + 4, x + 2, top + 7, G0)
        a.rect(x - 1, top + 6, x + 2, top + 7, G1)
        a.dot(x, top + 7, G1)
    else:
        a.rect(x - 1, top + 4, x + 2, top + 7, S4)
        a.dot(x, top + 7, S4)
        a.dot(x, top + 5, DK)                        # snapped filament
        a.dot(x + 1, top + 6, DK)
        for sx, sy in ((x + 3, top + 6), (x + 4, top + 4), (x + 4, top + 3), (x + 6, top + 1),
                       (x + 5, top - 1), (x + 7, top - 3), (x + 6, top - 5)):
            a.dot(sx, sy, S5)                        # wisp of smoke


def station(a, cx, numeral):
    """Station-of-the-Cross plaque with its Roman numeral."""
    a.rect(cx - 5, 58, cx + 9, 76, S3)                # shadow
    a.rect(cx - 7, 56, cx + 7, 74, W3)
    a.rect(cx - 6, 57, cx + 6, 73, W1)
    a.rect(cx - 5, 58, cx + 5, 72, S0)
    a.rect(cx - 1, 60, cx + 1, 70, W3)
    a.rect(cx - 3, 62, cx + 3, 64, W3)
    a.rect(cx - 2, 53, cx + 2, 56, W3)
    a.rect(cx - 1, 51, cx + 1, 53, G1)
    w = len(numeral) * 6 - 1
    a.rect(cx - w // 2 - 2, 76, cx - w // 2 + w + 2, 87, S0)
    a.rect(cx - w // 2 - 2, 86, cx - w // 2 + w + 2, 87, S2)
    a.text((cx - w // 2, 78), numeral, DK)


def person(a, x, top, size, coat, hair, skin, hat=None, turned=False):
    """Parishioner seated in a pew, seen over its back rail (top)."""
    hw, hh, sw, sh = size
    sx = x - sw // 2
    a.rect(sx, top - sh + 1, sx + sw, top, coat)
    a.rect(sx + 1, top - sh, sx + sw - 1, top - sh + 1, coat)
    hx, hy = x - hw // 2, top - sh - hh
    a.rect(hx, hy, hx + hw, top - sh, hair)
    if turned:
        a.rect(hx, hy + 2, hx + hw, top - sh, skin)
        a.dot(hx + 1, hy + 2 + (hh - 2) // 2, INK)
        a.dot(hx + hw - 2, hy + 2 + (hh - 2) // 2, INK)
    else:
        a.rect(hx + 1, top - sh - 1, hx + hw - 1, top - sh, skin)      # nape
    if hat:
        a.rect(hx - 1, hy, hx + hw + 1, hy + 2, hat)
        a.rect(hx, hy - 1, hx + hw, hy, hat)


# ------------------------------------------------------------------ main layer
def build_main():
    a = Art(W, H, mode="RGBA")
    vault = Art(W, 72)
    vault.vgrad(0, 0, W, 72, [V0, V1, V2, V2])

    def roof(x0, y, x1):                              # copy a run of the vault gradient
        for x in range(max(x0, 0), min(x1, W)):
            a.p[x, y] = vault.p[x, y] + (255,)

    # ---- wall: shadowy up in the vault, lit pale stone at fighter height
    a.vgrad(0, 0, W, 112, [S4, S3, S2, S1, S1])
    a.rect(0, 112, W, WALL_Y, S1)
    for j, y in enumerate(range(104, 150, 11)):       # ashlar joints
        a.rect(0, y, W, y + 1, S2)
        for x in range((j & 1) * 13 + 4, W, 26):
            a.rect(x, y + 1, x + 1, y + 11, S2)
    a.rect(0, 99, W, 100, S0)                         # string course at sill height
    a.rect(0, 100, W, 101, S2)
    a.rect(0, 101, W, 102, S3)

    # ---- floor: marble checker (painted early; pews, carpet and light go on top)
    floor_checker(a, WALL_Y, H, S1, F2, vx=CX, vy=VY)
    a.dither(0, WALL_Y, W, WALL_Y + 8, S4, 0.5)
    a.dither(0, WALL_Y + 8, W, WALL_Y + 18, S4, 0.25)

    # ---- arcade: pointed wall-arches over each side bay, dark vault above
    for cx in WINS:
        for y in range(0, 48):
            ho = arch_hw(42, 48, 48 - y)
            hi = arch_hw(38, 44, 48 - y) if y >= 4 else 0
            roof(cx - 42, y, cx - ho)
            roof(cx + ho, y, cx + 42)
            if ho > hi:
                a.rect(cx - ho, y, cx - hi, y + 1, S2)
                a.rect(cx + hi, y, cx + ho, y + 1, S2)
                a.dot(cx - ho, y, S0)
                a.dot(cx + ho - 1, y, S0)
                a.dot(cx - hi - 1, y, S4)
                a.dot(cx + hi, y, S4)
    for y in range(0, 70):                            # chancel bay
        ho = arch_hw(58, 70, 70 - y)
        roof(198, y, CX - ho)
        roof(CX + ho, y, 314)

    # ---- columns
    bands = ((S3, 1), (S1, 2), (S0, 3), (S1, 2), (S2, 2), (S3, 1), (S4, 1))
    for x0 in COLS:
        for y in range(0, 42):
            roof(x0, y, x0 + 12)
        a.rect(x0 + 4, 0, x0 + 8, 42, S4)             # vault shaft
        a.rect(x0 + 4, 0, x0 + 5, 42, S3)
        a.rect(x0 + 12, 49, x0 + 14, 141, S2)         # cast shadow on the wall
        x = x0
        for col, n in bands:
            a.rect(x, 48, x + n, WALL_Y, col)
            x += n
        a.rect(x0 - 2, 41, x0 + 14, 43, S0)           # capital
        a.rect(x0 - 2, 43, x0 + 14, 44, S3)
        a.rect(x0 - 1, 44, x0 + 13, 47, S1)
        a.rect(x0 - 1, 46, x0 + 13, 47, S2)
        a.rect(x0, 47, x0 + 12, 49, S4)
        a.rect(x0 - 2, 144, x0 + 14, WALL_Y, S2)      # base
        a.rect(x0 - 1, 141, x0 + 13, 144, S0)
        a.rect(x0 - 1, 143, x0 + 13, 144, S4)

    # ---- lancet windows (holes: the glass lives on the far layer)
    for cx in WINS:
        arch(a, cx, 24, 44, 9, 100, S3)
        arch(a, cx, 23, 44, 10, 100, S0)
        arch(a, cx, 22, 44, 12, 99, S4)
        arch(a, cx, 21, 44, 13, 98, DK)
        arch(a, cx, 20, 44, 14, 98, None)
        for y in (44, 62, 80):                        # saddle bars
            a.rect(cx - 20, y, cx + 20, y + 1, DK)
        a.rect(cx - 27, 98, cx + 27, 101, S0)         # sill
        a.rect(cx - 27, 100, cx + 27, 101, S2)
        a.rect(cx - 25, 101, cx + 25, 103, S4)
        a.dither(cx - 25, 103, cx + 25, 106, S2, 0.5)

    # ---- chancel arch (hole: the apse lives on the far layer)
    arch(a, CX, 58, 70, 0, 98, S3)
    arch(a, CX, 57, 70, 1, 98, S0)
    arch(a, CX, 55, 70, 3, 98, S1)
    arch(a, CX, 52, 70, 5, 98, S4)
    arch(a, CX, 51, 70, 5, 98, DK)
    arch(a, CX, 50, 70, 6, 98, None)
    for x0, x1 in ((197, 207), (305, 315)):           # respond capitals
        a.rect(x0, 64, x1, 66, S0)
        a.rect(x0 + 1, 66, x1 - 1, 69, S2)
        a.rect(x0 + 1, 69, x1 - 1, 70, S4)
    # sanctuary screen wall under the opening
    a.rect(198, 98, 314, WALL_Y, S2)
    a.rect(198, 98, 314, 100, S0)
    a.rect(198, 100, 314, 101, S4)
    for x in range(204, 312, 10):
        a.rect(x, 104, x + 1, 142, S3)

    # ---- altar: steps, reredos, crucifix, tabernacle, candles, lilies
    a.rect(200, 146, 312, WALL_Y, S1)                 # lower step
    a.rect(200, 146, 312, 147, S0)
    a.rect(200, 149, 312, WALL_Y, S4)
    a.rect(206, 142, 306, 146, S1)                    # predella
    a.rect(206, 142, 306, 143, S0)
    a.rect(206, 145, 306, 146, S3)
    a.rect(224, 102, 288, 124, W3)                    # reredos
    a.rect(226, 104, 286, 124, W2)
    a.rect(226, 104, 286, 105, G1)
    for x in (228, 236, 270, 278):
        a.rect(x, 108, x + 6, 124, G1)
        a.rect(x + 1, 107, x + 5, 108, G1)
        a.rect(x + 4, 109, x + 6, 124, G2)
        a.rect(x + 2, 111, x + 4, 113, R2)
    for x in (224, 285):
        a.rect(x, 97, x + 3, 102, W3)
        a.rect(x + 1, 95, x + 2, 97, G1)
    a.rect(244, 96, 268, 124, W3)
    a.rect(246, 98, 266, 124, W2)
    for i in range(6):
        a.rect(CX - 12 + 2 * i, 95 - i, CX + 12 - 2 * i, 96 - i, W3)
    a.rect(CX - 8, 94, CX + 8, 95, G1)
    # crucifix (stands against the apse)
    a.rect(254, 61, 258, 92, W3)
    a.rect(243, 69, 269, 73, W3)
    a.rect(254, 61, 255, 92, W2)
    a.rect(243, 69, 269, 70, W2)
    for gx0, gy0, gx1, gy1 in ((254, 60, 258, 61), (242, 69, 243, 73), (269, 69, 270, 73)):
        a.rect(gx0, gy0, gx1, gy1, G1)
    a.rect(253, 63, 259, 65, C0)                      # titulus
    a.rect(255, 66, 257, 69, K1)                      # corpus
    a.rect(245, 70, 267, 71, K1)
    a.dot(245, 69, K1)
    a.dot(266, 69, K1)
    a.rect(255, 71, 257, 79, K1)
    a.rect(254, 72, 258, 75, K1)
    a.rect(254, 79, 258, 82, C0)
    a.rect(255, 82, 257, 89, K1)
    # altar table
    a.rect(218, 120, 294, 123, C0)
    a.rect(218, 123, 294, 124, C1)
    a.rect(220, 124, 292, 142, C0)
    a.rect(220, 124, 292, 126, G1)
    for x in range(221, 292, 4):
        a.rect(x, 124, x + 2, 126, R2)
    a.rect(220, 138, 292, 142, C1)
    for x in range(220, 292, 2):
        a.dot(x, 141, C0)
    for x in (230, 278):
        a.rect(x, 126, x + 4, 142, G1)
        a.rect(x + 3, 126, x + 4, 142, G2)
    a.text((CX, 129), "IHS", G2, bold=True, align="center")
    # tabernacle
    a.rect(250, 108, 262, 120, G1)
    a.rect(250, 108, 262, 109, G0)
    a.rect(260, 109, 262, 120, G2)
    a.rect(252, 105, 260, 108, G1)
    a.rect(254, 103, 258, 105, G0)
    a.frame(252, 110, 260, 119, G2)
    a.rect(255, 112, 257, 117, R2)
    # candles: tallest by the tabernacle
    for x, top in ((228, 104), (236, 100), (244, 96), (266, 96), (274, 100), (282, 104)):
        a.rect(x, top, x + 2, 116, C0)
        a.rect(x + 1, top + 2, x + 2, 116, C1)
        a.rect(x - 1, 116, x + 3, 117, G0)
        a.rect(x, 117, x + 2, 119, G1)
        a.rect(x - 1, 119, x + 3, 120, G2)
        a.rect(x, top - 3, x + 2, top - 1, G0)
        a.dot(x, top - 4, O1)
        a.dot(x + 1, top - 1, O1)
    # lilies
    for vx, sgn in ((221, 1), (287, -1)):
        a.rect(vx, 113, vx + 4, 120, B2)
        a.rect(vx, 113, vx + 1, 120, B1)
        a.rect(vx - 1, 112, vx + 5, 113, B1)
        for (dx, dy) in ((1, -10), (-2, -6), (4, -7)):
            a.line([(vx + 2, 112), (vx + 1 + dx, 112 + dy)], N2)
            fx, fy = vx + dx, 111 + dy
            a.rect(fx, fy, fx + 3, fy + 2, C0)
            a.dot(fx + 1, fy - 1, C0)
            a.dot(fx + 1, fy, G1)
        a.dot(vx - 1, 108, N1)
        a.dot(vx + 4, 110, N1)
    # altar boys on the predella
    pal = dict(h=W4, s=K1, k=INK, w=C0, W=C1, r=R2, R=R3)
    a.stamp(ALTAR_BOY, pal, 207, 118)
    a.stamp(ALTAR_BOY, dict(pal, h=W2, s=K2), 296, 118, flip=True)
    # red sanctuary lamp on a wrought bracket (kept below the rose window)
    a.rect(206, 75, 219, 76, DK)
    a.line([(206, 81), (211, 76)], DK)
    a.rect(217, 76, 218, 79, G2)
    a.rect(215, 79, 220, 81, G1)
    a.rect(214, 81, 221, 88, R2)
    a.rect(215, 82, 217, 86, R1)
    a.dot(217, 84, G0)
    a.rect(215, 88, 220, 90, G1)
    a.rect(217, 90, 218, 92, G2)

    # ---- pulpit against the right chancel column
    a.rect(324, 86, 356, 88, W1)                      # tester (sounding board)
    a.rect(324, 88, 356, 91, W2)
    a.rect(326, 91, 354, 92, W3)
    a.rect(334, 83, 346, 86, W3)
    a.rect(336, 82, 344, 83, W1)
    a.rect(339, 75, 341, 82, G1)
    a.rect(337, 77, 343, 78, G1)
    a.rect(330, 92, 350, 113, W3)                     # back board
    a.rect(332, 94, 348, 113, W2)
    a.rect(332, 94, 348, 95, W1)
    a.rect(339, 96, 341, 113, W3)
    a.rect(322, 112, 358, 115, W1)                    # tub
    for i, y in enumerate(range(115, 133)):
        ins = i // 6
        a.rect(323 + ins, y, 357 - ins, y + 1, W2)
        a.rect(346, y, 357 - ins, y + 1, W3)
        a.rect(323 + ins, y, 334, y + 1, W1)
    a.rect(334, 115, 335, 133, W3)
    a.rect(345, 115, 346, 133, W3)
    a.rect(339, 118, 341, 129, G1)
    a.rect(336, 121, 344, 123, G1)
    a.rect(322, 115, 358, 116, W3)
    a.rect(328, 133, 352, 135, W3)
    a.rect(332, 135, 348, 137, W2)
    a.rect(336, 137, 344, WALL_Y, W3)
    a.rect(337, 137, 339, WALL_Y, W2)

    # ---- Our Lady on the left chancel column + votive candles
    a.stamp(MARY, dict(w=C0, W=C1, s=K1, b=B2, B=B1), 187, 102)
    a.rect(190, 99, 194, 100, G1)
    a.dot(189, 100, G1)
    a.dot(194, 100, G1)
    a.dot(188, 101, G1)
    a.dot(195, 101, G1)
    a.rect(185, 124, 199, 126, S0)
    a.rect(187, 126, 197, 128, S4)
    a.rect(180, 136, 204, 137, S5)
    a.rect(180, 141, 204, 142, S5)
    a.rect(180, 132, 181, WALL_Y, S5)
    a.rect(203, 132, 204, WALL_Y, S5)
    for row, y in enumerate((133, 138)):
        for i, x in enumerate(range(182 + row, 202, 3)):
            if (i + row) % 4 != 3:
                a.rect(x, y, x + 2, y + 3, R2)
                a.dot(x, y, R1)
                a.dot(x + (i & 1), y - 1, G0)

    # ---- confessional (bay 2)
    a.rect(176, 104, 178, 141, S3)                    # its shadow on the wall
    a.rect(178, 106, 179, 141, S2)
    a.rect(114, 106, 174, WALL_Y, W2)
    for i in range(5):                                # little pediment + cross
        a.rect(134 + 2 * i, 101 - i, 154 - 2 * i, 102 - i, W3)
    a.rect(143, 91, 145, 98, G1)
    a.rect(141, 93, 147, 94, G1)
    a.rect(112, 102, 176, 105, W1)
    a.rect(112, 105, 176, 106, W3)
    for px0 in (114, 132, 154, 172):
        a.rect(px0, 106, px0 + 2, WALL_Y, W3)
    for cx0 in (116, 156):                            # penitents' curtains
        a.rect(cx0, 106, cx0 + 16, 109, W3)
        a.rect(cx0, 109, cx0 + 16, WALL_Y, P2)
        for fx in range(cx0 + 1, cx0 + 16, 5):
            a.rect(fx, 109, fx + 1, WALL_Y, P1)
            a.rect(fx + 2, 109, fx + 3, WALL_Y, P3)
        a.rect(cx0, 109, cx0 + 16, 110, G1)
    a.rect(134, 106, 154, WALL_Y, W1)                 # priest's door
    a.frame(136, 108, 152, 148, W2)
    a.rect(139, 112, 149, 124, W4)
    for gy in range(112, 124, 2):
        for gx in range(139 + (gy // 2 & 1), 149, 2):
            a.dot(gx, gy, W2)
    a.rect(150, 130, 152, 132, G1)

    # ---- small wall furniture
    pendant(a, 79, 50)
    pendant(a, 175, 50)
    pendant(a, 337, 50, lit=False)                    # "...the bulb blew."
    pendant(a, 433, 50)
    for cx, num in ((17, "IV"), (113, "V"), (399, "VI"), (495, "VII")):
        station(a, cx, num)
    # hymn board (bay 4)
    a.rect(368, 135, 394, 137, S3)
    a.rect(392, 109, 394, 137, S3)
    a.rect(372, 105, 386, 107, W3)
    a.rect(366, 107, 392, 135, W3)
    a.rect(367, 108, 391, 134, W4)
    a.text((370, 110), "HYMNS", G1, tiny=True)
    a.rect(369, 117, 389, 124, C0)
    a.text((372, 118), "1964", DK, tiny=True)
    a.rect(369, 126, 389, 133, C0)
    a.text((374, 127), "217", DK, tiny=True)
    # parish notice board (bay 1)
    a.rect(26, 134, 74, 136, S3)
    a.rect(72, 108, 74, 136, S3)
    a.rect(24, 106, 72, 134, W3)
    a.rect(25, 107, 71, 133, W1)
    a.rect(28, 110, 60, 126, C0)
    a.text((30, 112), "BINGO", R2, tiny=True)
    a.text((30, 119), "FRI 7PM", DK, tiny=True)
    a.rect(43, 108, 45, 110, R2)
    a.rect(62, 112, 69, 122, LB)
    a.rect(63, 114, 68, 115, B2)
    a.rect(63, 117, 68, 118, B2)
    a.rect(50, 127, 60, 132, LA)
    a.rect(52, 129, 58, 130, G2)
    # radiator (bay 5)
    a.rect(446, 118, 482, 120, S5)
    for x in range(446, 482, 4):
        a.rect(x, 119, x + 3, WALL_Y, S4)
        a.rect(x, 119, x + 1, WALL_Y, S3)
        a.rect(x + 3, 120, x + 4, WALL_Y, S5)
    # Sister James keeps an eye on things (bay 4)
    a.stamp(NUN, dict(k=INK, K=DK, s=K1, e=INK, w=C0, g=G1), 396, 104)

    # ---- red carpet runner up the aisle and over the steps
    a.rect(236, 142, 276, WALL_Y, R2)
    a.rect(236, 145, 276, 146, R3)
    a.rect(236, 149, 276, WALL_Y, R3)
    for y in range(WALL_Y, H):
        hw = int(round(0.5 * (y - VY)))
        a.rect(CX - hw, y, CX + hw, y + 1, R2)
        a.rect(CX - hw, y, CX - hw + 2, y + 1, R3)
        a.rect(CX + hw - 2, y, CX + hw, y + 1, R3)
        a.dot(CX - hw + 3, y, G2)
        a.dot(CX + hw - 4, y, G2)
    a.dither(CX - 22, WALL_Y, CX + 22, WALL_Y + 6, R3, 0.5)

    # ---- pews, far row first, with the congregation
    rows = ((141, 152, 58), (145, 157, 64), (150, 163, 72), (156, 171, 81))
    sizes = ((4, 4, 8, 3), (5, 5, 9, 4), (5, 5, 10, 4), (6, 6, 12, 5))
    coats = (B2, P2, W3, N2, R3, S5, INK, P3)
    hairs = (W4, W3, C1, INK, W2, S4)
    hats = (None, None, None, R3, INK, B2, C0, P3, W3)
    r = random.Random(1964)
    for i, (t, b, hw) in enumerate(rows):
        for side in (-1, 1):
            x0, x1 = (0, CX - hw) if side < 0 else (CX + hw, W)
            x = x0 + r.randint(8, 18)
            while x < x1 - 10:
                if x > x0 + 10 and r.random() < (0.45, 0.5, 0.55, 0.5)[i]:
                    person(a, x, t, sizes[i], r.choice(coats), r.choice(hairs),
                           K2 if r.random() < 0.25 else K1, r.choice(hats), r.random() < 0.4)
                x += r.randint(15, 26)
            a.rect(x0, t, x1, b, W2)
            a.rect(x0, t, x1, t + 2, W1)
            a.rect(x0, t + 2, x1, t + 3, W3)
            a.rect(x0, b - 1, x1, b, W3)
            for gx in range(x0 + 7, x1 - 6, 18):
                a.rect(gx, t + 4, gx + 1, b - 1, W3)
            ex = x1 - 5 if side < 0 else x0                     # pew end on the aisle
            a.rect(ex, t - 3, ex + 5, b + 1, W3)
            a.rect(ex + 1, t - 4, ex + 4, t - 3, W3)
            a.rect(ex + 1, t - 2, ex + 4, b, W1)
            a.rect(ex + 2, t, ex + 3, b - 2, W2)
            if i == 3:
                a.dither(x0, b, x1, b + 3, S5, 0.5)             # shadow on the floor
                a.dither(x0, b + 3, x1, b + 5, S5, 0.25)

    # ---- coloured light from the glass, pooled on the floor
    def shaft(xa, xb, ya, y0, y1, col, level):        # xa..xb measured on row ya
        for y in range(y0, y1):
            s = (y - VY) / float(ya - VY)
            a.dither(int(round(CX + (xa - CX) * s)), y, int(round(CX + (xb - CX) * s)), y + 1, col, level)

    for cx, cols3 in ((48, (LR, LA, LB)), (144, (LB, LA, LR)), (368, (LR, LA, LG)), (464, (LG, LA, LR))):
        for j, col in enumerate(cols3):
            xa = cx - 19 + j * 13
            shaft(xa, xa + 11, 176, 176, 192, col, 0.5)
            shaft(xa, xa + 11, 176, 192, 204, col, 0.25)
    for xa, col in ((210, LB), (223, LA), (279, LA), (292, LR)):   # from the apse, flanking the runner
        shaft(xa, xa + 11, 156, 156, 182, col, 0.5)
        shaft(xa, xa + 11, 156, 182, 200, col, 0.25)
    oval = lambda x, y: ((x + 0.5 - CX) / 40.0) ** 2 + ((y - 180) / 12.0) ** 2 < 1
    tint(a, 190, 164, 322, 196, 0.5, {R2: R1}, inside=oval)
    oval2 = lambda x, y: ((x + 0.5 - CX) / 52.0) ** 2 + ((y - 181) / 18.0) ** 2 < 1
    tint(a, 176, 160, 336, 202, 0.25, {R2: R1}, inside=oval2)

    # ---- wind-tossed leaves blown up the aisle
    lp = dict(o=O1, y=G1, d=O2)
    a.stamp(LEAF, lp, 322, 178)
    a.stamp(LEAF, lp, 346, 191, flip=True)
    a.stamp(LEAF, lp, 186, 187, flip=True)
    return a


def build():
    f = build_far()
    a = build_main()
    return f.im, a.im
