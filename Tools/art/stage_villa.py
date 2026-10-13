"""KALOKAIRI ISLAND - Greece.  Donna Sheridan's stage (Mamma Mia!).

far  : Aegean sky, hazy islands, sparkling sea, sailboat, jetty (+ Dynamos).
main : Villa Donna (left), pergola terrace over the sea (centre), chapel on
       the rock behind a retaining wall (right), sun-bleached flagstones.
Wall/floor line is WALL_Y (150).  The pergola shade band runs y=96..160.
"""
import random

from PIL import Image, ImageDraw

from bg import Art
from stages import FAR_W, STAGE_H, STAGE_W, WALL_Y

HZ = 78           # sea horizon on the far layer
CAP_Y = 114       # top of the low terrace wall (sea shows above it)
RET_Y = 96        # top of the taller retaining wall under the chapel
SHADE_Y = 96      # pergola shade line on the villa facade

# ---- main-layer palette ------------------------------------------------
W1, W2, W3, W4 = "#fcf8ec", "#e4e0f4", "#c4bce8", "#a09cd4"      # whitewash: sun .. shade
B1, B2, B3, DK = "#58c0f0", "#2470e0", "#1c44ac", "#2c2058"      # cobalt + darkest outline
T1, T2, T3 = "#f4a460", "#d86838", "#a04030"                     # terracotta
P1, P2, P3 = "#fc94cc", "#f03c98", "#b01c78"                     # bougainvillea
G1, G2, G3, G4 = "#a8c850", "#6c9c38", "#3c7038", "#24503c"      # foliage
SILV = "#c8dca4"                                                 # olive leaf backs
ST, STL, STD, STS = "#d4aa84", "#e2bc94", "#c09878", "#9c786c"   # shaded warm stone
CAP1, CAP2 = "#f8e8bc", "#e8cc98"                                # sunlit stone caps
F1, F2, F3, FS = "#f8ecc8", "#f0deb0", "#e6d0a0", "#c8a880"      # sunlit flagstones + seam
H1, H2, H3, HS = "#b8a8d0", "#ac9cc8", "#a090c0", "#8474ac"      # flagstones in shade
D1, D2, D3 = "#d8a060", "#a86838", "#683c2c"                     # wood
YL, AM, OR, RD = "#fcd848", "#f0a030", "#f87c30", "#e43840"      # lantern / flower accents
SK, SKD = "#e8a880", "#b87860"                                   # skin (in shade)
HR, HB = "#58344c", "#dcb450"                                    # hair: dark, blond

LIT2SHADE = {W1: W3, W2: W4, W3: W4, B1: B2, B2: B3, B3: DK, YL: AM}
FLOOR2SHADE = {F1: H1, F2: H2, F3: H3, FS: HS}


def _hex(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def _remap(a, mask, table):
    """Recolour the pixels under `mask` (PIL '1' image) through a palette table."""
    t = {_hex(k) + (255,): _hex(v) + (255,) for k, v in table.items()}
    m = mask.load()
    for y in range(a.h):
        for x in range(a.w):
            if m[x, y]:
                c = a.p[x, y]
                if c in t:
                    a.p[x, y] = t[c]


def _stones(a, x0, y0, x1, y1, seed, rh=6, wmin=8, wmax=17):
    """Dry-stone courses: flat blocks, 1px seams, low contrast."""
    r = random.Random(seed)
    a.rect(x0, y0, x1, y1, STS)
    y = y0
    while y < y1:
        h = min(rh, y1 - y)
        x = x0 - r.randint(0, wmax // 2)
        while x < x1:
            w = r.randint(wmin, wmax)
            c = r.choice((ST, ST, ST, STL, STD))
            a.rect(max(x, x0), y, min(x + w - 1, x1), y + h - 1, c)
            if c == ST and w > 11 and r.random() < 0.5:
                a.rect(max(x + 2, x0), y, min(x + w - 4, x1), y + 1, STL)
            x += w
        y += h


def _blooms(a, clusters, cols, flecks, seed):
    """Chunky foliage / blossom mass.  cols = (light, mid, dark)."""
    r = random.Random(seed)
    for x, y, q in clusters:
        a.ellipse(x - q, y - q, x + q + 1, y + q + 1, cols[2])
    for x, y, q in clusters:
        a.ellipse(x - q, y - q - 1, x + q - 1, y + q - 1, cols[1])
    for x, y, q in clusters:
        for _ in range(q):
            dx, dy = r.randint(-q + 1, q // 3), r.randint(-q + 1, q // 3)
            a.rect(x + dx, y + dy, x + dx + 2, y + dy + 1, cols[0])
        for _ in range(max(1, q // 2)):
            dx, dy = r.randint(-q, q - 1), r.randint(-q, q - 1)
            fc = r.choice(flecks)
            a.rect(x + dx, y + dy, x + dx + 2, y + dy + 2, fc)
        if q >= 5:                                   # loose sprigs break up the silhouette
            for _ in range(3):
                dx = r.choice((-q - 2, q + 1))
                dy = r.randint(-q + 2, q - 2)
                a.rect(x + dx, y + dy, x + dx + 2, y + dy + 2, cols[1])
                a.dot(x + dx + 1, y + dy + 1, cols[2])
                a.dot(x + dx, y + dy, cols[0])


def _pot(a, x, base, w, h, flowers=None, seed=0):
    """Terracotta pot standing on `base`; optional geranium colour."""
    top = base - h
    a.poly([(x + 1, top + 2), (x + w - 2, top + 2), (x + w - 3, base - 1), (x + 2, base - 1)], T2)
    a.rect(x + 2, top + 3, x + 3 + w // 5, base - 1, T1)
    a.rect(x + w - 3 - w // 5, top + 3, x + w - 2, base, T3)
    a.rect(x, top, x + w, top + 2, T1)
    a.rect(x + w - 2, top, x + w, top + 2, T2)
    a.rect(x + 1, top + 2, x + w - 1, top + 3, T3)
    if flowers:
        r = random.Random(seed + x)
        q = w // 2 + 1
        cx, cy = x + w // 2, top - q + 2
        a.ellipse(cx - q - 1, cy - q + 1, cx + q + 1, cy + q, G3)
        a.ellipse(cx - q - 1, cy - q, cx + q - 1, cy + q - 2, G2)
        for _ in range(q + 1):
            dx, dy = r.randint(-q, q - 2), r.randint(-q, q - 3)
            a.rect(cx + dx, cy + dy, cx + dx + 2, cy + dy + 2, flowers)
            a.dot(cx + dx, cy + dy, P1 if flowers != P2 else W1)


LANTERN = [
    "...kkk...",
    "..hLLLm..",
    ".hLLLLLm.",
    "hhLLLLLmm",
    "LhLLLLLmm",
    "LLLLLLLmm",
    "LLLLLLmmm",
    ".LLLLmmm.",
    "..Lmmmm..",
    "...kkk...",
    "....t....",
    "....t....",
]
LANTERN_PALS = {
    "pink": {"L": P2, "h": P1, "m": P3, "k": DK, "t": YL},
    "yellow": {"L": YL, "h": W1, "m": AM, "k": DK, "t": RD},
    "cyan": {"L": B1, "h": W1, "m": B2, "k": DK, "t": YL},
    "orange": {"L": OR, "h": YL, "m": T2, "k": DK, "t": YL},
    "red": {"L": RD, "h": T1, "m": T3, "k": DK, "t": YL},
}


def _lantern(a, x, y, drop, kind):
    a.rect(x, y, x + 1, y + drop, D3)
    a.stamp(LANTERN, LANTERN_PALS[kind], x - 4, y + drop)


def _swag(a, xa, xb, y, dip, phase=0):
    """String of party bulbs sagging between two hooks."""
    cols = (YL, P2, B1, OR)
    n = xb - xa
    for i in range(n + 1):
        t = i / n
        a.dot(xa + i, y + int(round(4 * dip * t * (1 - t))), D3)
    k = phase
    for i in range(4, n - 2, 7):
        t = i / n
        yy = y + int(round(4 * dip * t * (1 - t)))
        a.rect(xa + i, yy + 1, xa + i + 2, yy + 3, cols[k % 4])
        k += 1


GOAT = [
    "..............d.d..",
    "..............dd...",
    ".............nnnn..",
    "............dnnkww.",
    "............nnnnwwp",
    ".n.nnnnnnnnnnnn.ww.",
    "..nnnnnnnnnnnnn.w..",
    "..nnnwwnnnnnnnn.w..",
    "..nnwwwwnnnnnnm....",
    "..mnnwwnnnnnnmm....",
    "..nm.mm...mn.mm....",
    "..nm..m...mn..m....",
    "..nm..m...mn..m....",
    "..dd..d...dd..d....",
]

DYNAMO = [
    "...hh...a",
    "..hhhh.a.",
    "..hssh.a.",
    "...ss.cc.",
    ".acccccc.",
    "a.cccc...",
    "a.cccc...",
    "..cccc...",
    "..cc.cc..",
    "..cc.cc..",
    ".ccc.ccc.",
    ".bbb.bbb.",
]


def _head(a, x, y, hair, facing, hat=None):
    """7x8 onlooker head; facing -1 / 0 / +1."""
    a.rect(x, y, x + 7, y + 3, hair)
    a.rect(x + 1, y + 2, x + 6, y + 8, SK)
    a.rect(x + 1, y + 7, x + 6, y + 8, SKD)
    if facing > 0:
        a.rect(x, y, x + 2, y + 6, hair)
        a.dot(x + 4, y + 4, DK)
    elif facing < 0:
        a.rect(x + 5, y, x + 7, y + 6, hair)
        a.dot(x + 2, y + 4, DK)
    else:
        a.rect(x, y + 2, x + 1, y + 5, hair)
        a.rect(x + 6, y + 2, x + 7, y + 5, hair)
        a.dot(x + 2, y + 4, DK)
        a.dot(x + 4, y + 4, DK)
    if hat:
        a.rect(x - 2, y + 1, x + 9, y + 2, hat)
        a.rect(x + 1, y - 2, x + 6, y + 1, hat)
        a.rect(x + 1, y, x + 6, y + 1, T2)


def _chair(a, x, facing):
    """Blue taverna chair, side view.  x = back post; seat at y=137."""
    s = 1 if facing > 0 else -1
    a.rect(x, 121, x + 2, WALL_Y, B3)
    a.rect(x, 121, x + 1, 137, B2)
    x0, x1 = (x, x + 13) if s > 0 else (x - 11, x + 2)
    a.rect(x0, 137, x1, 139, AM)
    a.rect(x0, 139, x1, 140, B3)
    fx = x1 - 2 if s > 0 else x0
    a.rect(fx, 140, fx + 2, WALL_Y, B3)
    a.rect(x0 + 1, 145, x1 - 1, 146, B3)


def _table(a, x0, x1):
    """Taverna table with a terracotta-check cloth; top at y=130."""
    a.rect(x0 + 3, 140, x0 + 5, WALL_Y, D3)
    a.rect(x1 - 5, 140, x1 - 3, WALL_Y, D3)
    a.rect(x0, 130, x1, 132, F1)
    for y in range(132, 141, 3):
        for x in range(x0, x1, 3):
            a.rect(x, y, min(x + 3, x1), y + 3, T2 if ((x - x0) // 3 + (y - 132) // 3) & 1 else F2)
    a.rect(x0, 132, x1, 133, STD)


def _sitter(a, x, facing, hair, shirt, shirt_sh, pants, hat=None):
    """Seated onlooker in profile.  x = left edge of the head."""
    s = 1 if facing > 0 else -1
    _head(a, x, 108, hair, facing, hat)
    a.rect(x, 116, x + 8, 133, shirt)
    bx = x if s > 0 else x + 6
    a.rect(bx, 117, bx + 2, 133, shirt_sh)
    if s > 0:
        a.rect(x + 5, 121, x + 13, 124, shirt_sh)
        a.rect(x + 13, 121, x + 15, 124, SK)
        a.rect(x + 2, 133, x + 14, 138, pants)
        a.rect(x + 11, 138, x + 14, 148, pants)
        a.rect(x + 11, 148, x + 16, WALL_Y, DK)
    else:
        a.rect(x - 6, 121, x + 2, 124, shirt_sh)
        a.rect(x - 8, 121, x - 6, 124, SK)
        a.rect(x - 7, 133, x + 5, 138, pants)
        a.rect(x - 7, 138, x - 4, 148, pants)
        a.rect(x - 9, 148, x - 4, WALL_Y, DK)


def _cloud(f, x, base, blobs, lit="#fcfcf4", sh="#a8d4f8"):
    """Flat-bottomed cumulus: blobs = (dx, radius) resting on `base`."""
    w = max(dx + q for dx, q in blobs) + 4
    h = max(q for _, q in blobs) * 2 + 4
    c = Art(w, h, mode="RGBA")
    for dx, q in blobs:
        c.ellipse(dx - q + 2, h - 2 * q + q // 2, dx + q + 2, h + q // 2, sh)
    for dx, q in blobs:
        c.ellipse(dx - q + 1, h - 2 * q + q // 2 - 2, dx + q, h + q // 2 - 3, lit)
    c.rect(0, h - 2, w, h, sh)
    cp = c.im.load()
    for xx in range(w):                      # keep the base strip only under the cloud
        if cp[xx, h - 3][3] == 0:
            cp[xx, h - 2] = cp[xx, h - 1] = (0, 0, 0, 0)
    f.paste(c.im, (x, base - h))


def _far():
    f = Art(FAR_W, STAGE_H)
    f.vgrad(0, 0, FAR_W, HZ, ["#1468d8", "#2088e8", "#40b0f4", "#84d8f8", "#c8f0f8"])
    _cloud(f, 18, 40, [(8, 6), (20, 11), (36, 9), (50, 6)])
    _cloud(f, 150, 30, [(6, 5), (18, 9), (32, 12), (48, 8), (60, 5)])
    _cloud(f, 300, 46, [(8, 7), (22, 12), (40, 10), (56, 6)])
    _cloud(f, 244, 24, [(6, 5), (16, 8), (28, 5)])
    _cloud(f, 96, 66, [(5, 3), (13, 5), (24, 4), (33, 3)], sh="#b8e4f8")
    _cloud(f, 236, 70, [(5, 3), (12, 4), (22, 3)], sh="#b8e4f8")

    # hazy islands on the horizon (far -> near)
    f.poly([(20, HZ), (34, 70), (52, 66), (70, 61), (84, 64), (100, 70), (124, 74), (140, HZ)], "#94c4f0")
    f.poly([(196, HZ), (214, 73), (236, 70), (262, 72), (284, 75), (300, HZ)], "#94c4f0")
    f.poly([(318, HZ), (336, 68), (352, 62), (366, 54), (384, 50), (400, 56), (418, 60), (448, 64),
            (448, HZ)], "#6c9ce4")
    f.poly([(366, 54), (384, 50), (400, 56), (392, 60), (376, 60)], "#84b4ec")
    f.poly([(0, HZ), (0, 68), (10, 70), (24, 75), (32, HZ)], "#6c9ce4")
    for vx, vy in ((372, 66), (378, 69), (386, 64), (392, 68), (404, 66), (398, 71), (412, 70), (426, 69)):
        f.rect(vx, vy, vx + 3, vy + 2, "#f4fcfc")           # whitewashed village
        f.dot(vx + 2, vy + 1, "#3c6cd0")
    f.rect(386, 62, 388, 64, "#2c58c8")
    f.dither(0, HZ - 3, FAR_W, HZ, "#c8f0f8", 0.5)

    # sea
    f.vgrad(0, HZ, FAR_W, WALL_Y, ["#50b0f4", "#2c84e8", "#1c60d4", "#1848b4", "#183ca0"])
    f.rect(0, WALL_Y, FAR_W, STAGE_H, "#183ca0")
    f.rect(0, HZ, FAR_W, HZ + 1, "#b4ecf8")
    r = random.Random(7)
    y = HZ + 2
    while y < STAGE_H:
        d = y - HZ
        x = r.randint(0, 8)
        while x < FAR_W:
            ln = 2 + d // 9 + r.randint(0, 2)
            k = r.random()
            glitter = 120 < x < 190 - d // 3 + 30
            if k < (0.5 if glitter else 0.22):
                f.rect(x, y, x + ln, y + 1, "#f4fcfc" if (glitter and k < 0.3) or k < 0.05 else "#7cd0f8")
            elif k > 0.86:
                f.rect(x, y, x + ln + 2, y + 1, "#143494" if d > 20 else "#2470d8")
            x += ln + r.randint(3, 9 + d // 6)
        y += 2 + d // 14

    # gulls
    for gx, gy in ((132, 50), (141, 46), (282, 56), (206, 30), (352, 40)):
        f.rect(gx, gy, gx + 2, gy + 1, "#f4fcfc")
        f.rect(gx + 3, gy, gx + 5, gy + 1, "#f4fcfc")
        f.dot(gx + 2, gy + 1, "#2c2058")

    # sailboat
    bx, by = 176, 101
    f.poly([(bx + 8, by - 20), (bx + 8, by - 3), (bx - 2, by - 3)], "#fcfcf4")
    f.poly([(bx + 10, by - 18), (bx + 10, by - 3), (bx + 19, by - 3)], "#fcfcf4")
    f.poly([(bx + 10, by - 9), (bx + 10, by - 3), (bx + 19, by - 3), (bx + 15, by - 9)], "#b8d8f8")
    f.rect(bx + 8, by - 22, bx + 10, by - 2, "#683c2c")
    f.rect(bx + 9, by - 23, bx + 13, by - 21, "#e43840")
    f.poly([(bx - 2, by - 2), (bx + 21, by - 2), (bx + 18, by + 1), (bx + 1, by + 1)], "#fcfcf4")
    f.rect(bx - 1, by - 1, bx + 20, by, "#e43840")
    f.rect(bx + 2, by + 1, bx + 18, by + 2, "#143494")
    for dx, dy, ln in ((4, 3, 10), (7, 5, 6), (3, 7, 5), (11, 8, 4)):
        f.rect(bx + dx, by + dy, bx + dx + ln, by + dy + 1, "#b8e4f8")
    # tiny far sails + a caique
    for sx, sy in ((62, 86), (330, 84)):
        f.poly([(sx, sy - 6), (sx, sy), (sx - 4, sy)], "#fcfcf4")
        f.poly([(sx + 1, sy - 5), (sx + 1, sy), (sx + 4, sy)], "#d8ecf8")
        f.rect(sx - 4, sy, sx + 5, sy + 1, "#143494")
    cx, cy = 356, 97
    f.poly([(cx, cy - 3), (cx + 18, cy - 3), (cx + 15, cy + 1), (cx + 3, cy + 1)], "#f4fcfc")
    f.rect(cx + 1, cy - 2, cx + 17, cy - 1, "#f87c30")
    f.rect(cx + 7, cy - 8, cx + 12, cy - 3, "#f4fcfc")
    f.rect(cx + 8, cy - 7, cx + 10, cy - 5, "#143494")
    f.rect(cx + 4, cy + 1, cx + 15, cy + 2, "#143494")

    # jetty with three Dynamos mid-routine
    jx0, jx1, jy = 226, 300, 107
    for px_ in range(jx0 + 4, jx1, 13):
        f.rect(px_, jy + 2, px_ + 2, jy + 9, "#4c2c34")
        f.rect(px_, jy + 10, px_ + 2, jy + 11, "#143494")
        f.rect(px_ - 1, jy + 12, px_ + 3, jy + 13, "#143494")
    f.poly([(jx1, jy), (jx1 + 22, jy), (jx1 + 70, WALL_Y), (jx1 + 30, WALL_Y)], "#a86838")
    f.poly([(jx1 + 18, jy), (jx1 + 22, jy), (jx1 + 70, WALL_Y), (jx1 + 62, WALL_Y)], "#683c2c")
    f.rect(jx0, jy, jx1 + 20, jy + 1, "#f0c078")
    f.rect(jx0, jy + 1, jx1 + 20, jy + 3, "#a86838")
    for px_ in range(jx0 + 6, jx1 + 18, 8):
        f.dot(px_, jy + 1, "#683c2c")
    f.rect(jx0 - 1, jy - 4, jx0 + 1, jy + 3, "#4c2c34")
    for i, (cc, hair, flip) in enumerate((("#fc5cac", "#fcd848", False), ("#fcd848", "#e45c30", True),
                                           ("#f4fcfc", "#683c2c", False))):
        pal = {"h": hair, "s": "#f8b890", "a": "#f8b890", "c": cc, "b": "#f4fcfc" if i != 2 else "#fc5cac"}
        f.stamp(DYNAMO, pal, 240 + i * 15, jy - 12, flip=flip)
    f.rect(238, jy + 4, 284, jy + 5, "#143494")
    return f


def build():
    f = _far()
    a = Art(STAGE_W, STAGE_H, mode="RGBA")

    # ================= RIGHT: chapel on the rock (behind the retaining wall)
    # cypress at the far edge
    a.poly([(506, 26), (500, 50), (498, 80), (500, RET_Y), (512, RET_Y), (512, 40)], G3)
    a.poly([(507, 30), (509, 60), (508, RET_Y), (512, RET_Y), (512, 40)], G4)
    for cy_ in range(36, 94, 7):
        a.rect(501 + (cy_ // 7) % 3, cy_, 503 + (cy_ // 7) % 3, cy_ + 3, G2)
    # dome
    a.ellipse(429, 24, 475, 72, B3)
    a.ellipse(429, 24, 469, 68, B2)
    a.ellipse(435, 28, 452, 42, B1)
    a.rect(438, 31, 442, 33, W1)
    a.rect(449, 17, 455, 25, W1)
    a.rect(453, 17, 455, 25, W2)
    a.rect(451, 5, 453, 17, W1)
    a.rect(447, 9, 457, 11, W1)
    # drum + nave
    a.rect(427, 46, 477, 58, W1)
    a.rect(469, 46, 477, 58, W2)
    a.rect(427, 46, 477, 47, W2)
    for wx in (434, 444, 454, 464):
        a.rect(wx, 50, wx + 3, 55, B3)
    a.rect(402, 58, 500, RET_Y, W1)
    a.rect(400, 56, 502, 59, W1)
    a.rect(400, 59, 502, 60, W3)
    a.rect(492, 60, 500, RET_Y, W2)
    a.vgrad(402, 64, 492, RET_Y + 24, [W1, W2])
    # bell-cote
    bc = 479
    a.rect(bc, 34, bc + 20, 56, W1)
    a.rect(bc + 16, 34, bc + 20, 56, W2)
    a.poly([(bc, 34), (bc + 10, 28), (bc + 20, 34)], W1)
    a.d.ellipse([bc + 4, 38, bc + 15, 49], fill=(0, 0, 0, 0))
    a.clear(bc + 4, 44, bc + 16, 52)
    a.rect(bc + 9, 38, bc + 11, 42, D3)
    a.rect(bc + 7, 42, bc + 13, 47, YL)
    a.rect(bc + 11, 42, bc + 13, 47, AM)
    a.rect(bc + 6, 47, bc + 14, 48, AM)
    a.rect(bc + 9, 48, bc + 11, 50, D3)
    a.rect(bc + 9, 21, bc + 11, 28, W1)
    a.rect(bc + 7, 23, bc + 13, 25, W1)
    # arched door + round windows
    a.ellipse(441, 66, 463, 86, B3)
    a.rect(441, 76, 463, RET_Y, B3)
    a.ellipse(443, 68, 461, 86, B2)
    a.rect(443, 77, 461, RET_Y, B2)
    a.rect(451, 69, 453, RET_Y, B3)
    a.rect(444, 77, 446, RET_Y, B1)
    a.rect(455, 84, 457, 86, YL)
    for wx in (414, 476):
        a.ellipse(wx, 68, wx + 10, 78, B3)
        a.ellipse(wx + 2, 70, wx + 8, 76, DK)
        a.rect(wx + 4, 69, wx + 5, 77, B3)
        a.rect(wx + 1, 72, wx + 9, 73, B3)
    # olive tree growing behind the wall
    a.poly([(384, RET_Y), (386, 84), (383, 74), (387, 72), (390, 80), (394, 70), (398, 72), (394, 84),
            (396, RET_Y)], D3)
    a.poly([(387, RET_Y), (389, 84), (391, 84), (392, RET_Y)], D2)
    _blooms(a, [(378, 62, 9), (392, 52, 11), (406, 62, 9), (386, 68, 8), (400, 70, 7), (372, 70, 6),
                (396, 44, 7), (412, 54, 6)], (G1, G2, G3), (SILV, SILV, G4), 11)

    # ================= LEFT: Villa Donna
    a.rect(0, 14, 104, 116, W1)                    # tall block
    a.rect(0, 14, 104, 16, W2)
    a.rect(0, 19, 104, 20, W2)
    a.clear(102, 14, 104, 15)
    a.rect(100, 20, 104, 116, W2)
    a.rect(104, 66, 150, 116, W1)                  # lower wing with the front door
    a.rect(104, 64, 152, 67, W1)
    a.rect(104, 67, 152, 68, W3)
    a.poly([(104, 68), (111, 68), (104, 92)], W3)
    r = random.Random(5)
    for _ in range(26):                            # plaster flecks
        x, y = r.randint(2, 96), r.randint(24, 92)
        a.rect(x, y, x + r.randint(2, 5), y + 1, W2)
    # window + shutters
    a.rect(29, 53, 81, 89, W3)                     # cast shadow (drawn first, offset)
    a.rect(38, 50, 66, 86, B3)
    a.rect(40, 52, 64, 84, DK)
    a.rect(40, 52, 49, 84, W4)                     # curtain
    a.rect(42, 52, 43, 84, W2)
    a.rect(46, 52, 47, 80, W2)
    a.rect(51, 52, 53, 84, B2)
    a.rect(40, 66, 64, 68, B2)
    for sx in (26, 66):
        a.rect(sx, 50, sx + 12, 86, B2)
        a.rect(sx, 50, sx + 1, 86, B1)
        a.rect(sx + 11, 50, sx + 12, 86, B3)
        for sy in range(53, 85, 3):
            a.rect(sx + 2, sy, sx + 10, sy + 1, B3)
    a.rect(36, 86, 68, 92, T2)
    a.rect(36, 86, 68, 87, T1)
    a.rect(36, 91, 68, 92, T3)
    _blooms(a, [(42, 83, 4), (52, 82, 4), (62, 83, 4)], (P1, RD, G3), (G2, G2, RD), 3)
    # front door
    a.rect(112, 78, 140, 128, W2)
    a.rect(114, 80, 138, 128, B3)
    a.rect(115, 81, 137, 128, B2)
    a.rect(115, 81, 116, 128, B1)
    for py in (84, 99, 114):
        for px_ in (118, 128):
            a.frame(px_, py, px_ + 8, py + 12, B3)
            a.rect(px_ + 1, py + 11, px_ + 8, py + 12, B1)
    a.rect(126, 81, 127, 128, B3)
    a.rect(123, 104, 125, 106, YL)
    a.rect(143, 82, 146, 87, YL)                   # porch lamp
    a.rect(142, 81, 147, 82, DK)
    a.rect(144, 87, 145, 89, DK)

    # ================= stone: dado, low terrace wall, retaining wall
    _stones(a, 0, 116, 150, WALL_Y, 21)
    a.rect(0, 116, 150, 117, STL)
    a.rect(114, 116, 138, 128, B2)                 # door runs down through the dado
    a.rect(114, 116, 115, 128, B3)
    a.rect(115, 116, 116, 128, B1)
    a.rect(126, 116, 127, 128, B3)
    a.rect(137, 116, 138, 128, B3)
    a.rect(112, 116, 114, 128, W2)
    a.rect(138, 116, 140, 128, W2)
    _stones(a, 150, CAP_Y + 4, 372, WALL_Y, 22)
    a.rect(148, CAP_Y, 372, CAP_Y + 2, CAP1)
    a.rect(148, CAP_Y + 2, 372, CAP_Y + 4, CAP2)
    a.rect(150, CAP_Y + 4, 372, CAP_Y + 5, STS)
    # gap in the wall: steps down to the beach, sea straight through
    a.clear(240, CAP_Y, 272, 144)
    a.rect(240, 144, 272, 146, CAP2)
    a.rect(240, 146, 272, WALL_Y, STD)
    for gx in (230, 272):
        _stones(a, gx, 104, gx + 10, WALL_Y, 30 + gx, rh=6, wmin=5, wmax=9)
        a.rect(gx - 1, 101, gx + 11, 103, CAP1)
        a.rect(gx - 1, 103, gx + 11, 105, CAP2)
        a.rect(gx + 8, 105, gx + 10, WALL_Y, STD)
    _stones(a, 372, RET_Y + 4, STAGE_W, WALL_Y, 23, rh=7, wmin=10, wmax=20)
    a.rect(370, RET_Y, STAGE_W, RET_Y + 2, CAP1)
    a.rect(370, RET_Y + 2, STAGE_W, RET_Y + 4, CAP2)
    a.rect(372, RET_Y + 4, STAGE_W, RET_Y + 5, STS)
    # door steps
    for i, (sx0, sx1) in enumerate(((108, 144), (104, 148), (100, 152))):
        y = 128 + i * 7
        a.rect(sx0, y, sx1, y + 2, CAP2)
        a.rect(sx0, y + 2, sx1, y + 7, ST)
        a.rect(sx0, y + 6, sx1, y + 7, STS)
        a.rect(sx1 - 2, y + 2, sx1, y + 7, STD)

    # ================= pergola shade on the facade (crisp slatted edge)
    m = Image.new("1", (STAGE_W, STAGE_H), 0)
    md = ImageDraw.Draw(m)
    md.rectangle([0, SHADE_Y, 151, 128], fill=1)
    for x in range(-4, 164, 12):
        md.polygon([(x, SHADE_Y), (x + 6, SHADE_Y), (x - 2, SHADE_Y - 12), (x - 8, SHADE_Y - 12)], fill=1)
    md.rectangle([152, 0, STAGE_W, STAGE_H], fill=0)
    _remap(a, m, LIT2SHADE)

    # ================= pergola: beam, rafters, posts
    for px_ in (152, 365):
        a.rect(px_, 36, px_ + 5, WALL_Y, D2)
        a.rect(px_, 36, px_ + 1, WALL_Y, D1)
        a.rect(px_ + 4, 36, px_ + 5, WALL_Y, D3)
        a.rect(px_ - 2, 144, px_ + 7, WALL_Y, STD)
        a.rect(px_ - 2, 144, px_ + 7, 145, STL)
    for x0, y0, x1, y1 in ((157, 48, 169, 36), (364, 48, 352, 36)):
        a.line([(x0, y0), (x1, y1)], D2, 2)
        a.line([(x0, y0 + 1), (x1, y1 + 1)], D3)
    for x in range(4, 372, 12):
        a.rect(x, 25, x + 4, 30, D2)
        a.rect(x, 25, x + 4, 26, D1)
        a.rect(x + 3, 26, x + 4, 30, D3)
    a.rect(0, 30, 374, 36, D2)
    a.rect(0, 30, 374, 31, D1)
    a.rect(0, 35, 374, 36, D3)
    a.rect(372, 30, 374, 36, D3)

    # party lights + paper lanterns
    hooks = [-10, 44, 100, 156, 206, 256, 306, 366]
    for i in range(len(hooks) - 1):
        _swag(a, hooks[i], hooks[i + 1], 36, 6, phase=i)
    for x, drop, kind in ((14, 9, "pink"), (44, 5, "yellow"), (88, 8, "cyan"), (138, 4, "orange"),
                          (171, 9, "pink"), (341, 9, "yellow"), (356, 3, "cyan")):
        _lantern(a, x, 36, drop, kind)

    # the sign
    a.rect(198, 36, 199, 42, D3)
    a.rect(313, 36, 314, 42, D3)
    a.rect(182, 42, 330, 64, B3)
    a.rect(183, 43, 329, 63, B2)
    a.rect(185, 45, 327, 61, W1)
    a.rect(185, 60, 327, 61, W2)
    a.text((256, 46), "VILLA DONNA", B3, scale=2, align="center")

    # vines along the pergola top
    for vx, q in ((30, 4), (70, 5), (118, 4), (200, 4), (236, 5), (290, 4), (322, 5)):
        _blooms(a, [(vx, 26, q), (vx + q + 2, 28, q - 1), (vx - q, 28, q - 2)], (G1, G2, G3), (P2, G4, P1), vx)

    # ================= floor: sun-bleached flags, pergola shade by the wall
    lit = (F2, F1, F2, F3, F2, F1, F2)
    prev = None
    for y in range(WALL_Y, STAGE_H):
        d = y - 106
        row = int(400.0 / d)
        new_row, prev = row != prev, row
        off = 1000 + (0.5 if row & 1 else 0)
        left = None
        for x in range(STAGE_W):
            b = int((x - 256) / d * 3.2 + off)
            up = int((x - 256) / (d - 1) * 3.2 + off)      # same joint one scanline up
            if new_row or (left is not None and b != left) or b != up:
                a.p[x, y] = a.c(FS)                         # unbroken stair-stepped seams
            else:
                a.p[x, y] = a.c(lit[(b * 73 + row * 151) % 7])
            left = b
    m = Image.new("1", (STAGE_W, STAGE_H), 0)
    md = ImageDraw.Draw(m)
    md.polygon([(0, WALL_Y), (378, WALL_Y), (384, 158), (0, 158)], fill=1)
    for x in range(-8, 384, 16):                           # slat shadows, gently fanned
        k = (x - 256) // 14
        md.polygon([(x, 158), (x + 10, 158), (x + 10 + k, 167), (x + k, 167)], fill=1)
    md.rectangle([378, WALL_Y, STAGE_W, WALL_Y + 2], fill=1)
    _remap(a, m, FLOOR2SHADE)
    a.rect(0, WALL_Y, STAGE_W, WALL_Y + 1, HS)

    # ================= props
    # goat on the wing roof, eyeing the bougainvillea
    a.stamp(GOAT, {"w": W1, "n": D1, "m": D2, "d": DK, "k": DK, "p": P1}, 108, 50)

    # bougainvillea cascades
    a.line([(5, WALL_Y), (4, 120), (7, 96), (5, 70)], D3)
    _blooms(a, [(4, 22, 9), (16, 28, 8), (6, 40, 8), (20, 44, 6), (4, 56, 7), (14, 62, 5), (5, 72, 6),
                (10, 84, 5), (4, 94, 4), (8, 104, 3)], (P1, P2, P3), (G2, G3, G2), 1)
    _blooms(a, [(146, 60, 8), (156, 54, 7), (136, 62, 5), (158, 68, 7), (150, 76, 6), (160, 84, 5),
                (154, 94, 5), (159, 104, 4), (155, 112, 3)], (P1, P2, P3), (G2, G3, G2), 2)
    _blooms(a, [(366, 26, 8), (356, 24, 6), (374, 34, 6), (370, 44, 5), (366, 54, 4)],
            (P1, P2, P3), (G2, G3, G2), 3)
    _blooms(a, [(500, RET_Y, 9), (488, RET_Y + 2, 7), (506, 108, 7), (496, 112, 6), (504, 122, 5),
                (508, 132, 4), (478, RET_Y + 1, 4)], (P1, P2, P3), (G2, G3, G2), 4)

    # pots: along the villa, on the gate pillars, on the retaining wall
    _pot(a, 12, WALL_Y, 16, 20, RD, 1)
    _pot(a, 36, WALL_Y, 11, 12, P2, 2)
    _pot(a, 76, WALL_Y, 13, 15, RD, 3)
    _pot(a, 231, 101, 8, 8, RD, 4)
    _pot(a, 273, 101, 8, 8, RD, 5)
    _pot(a, 426, RET_Y, 10, 10, RD, 6)
    _pot(a, 462, RET_Y, 9, 9, P2, 7)
    _pot(a, 474, WALL_Y, 18, 24, RD, 8)
    _pot(a, 384, WALL_Y, 12, 13, P2, 9)

    # taverna table 1: three possible dads sharing an ouzo
    _chair(a, 158, 1)
    _chair(a, 225, -1)
    _head(a, 188, 106, HB, 0, hat=F3)                          # Bill
    a.rect(185, 114, 198, 131, T1)
    a.rect(185, 114, 187, 131, T2)
    a.rect(196, 114, 198, 131, T2)
    a.rect(190, 114, 193, 117, SKD)
    _sitter(a, 161, 1, HR, W2, W4, STD)                        # Sam
    _sitter(a, 217, -1, HR, P1, P2, DK)                        # Harry
    _table(a, 175, 209)
    a.rect(190, 121, 193, 130, G3)                             # bottle + glasses
    a.rect(191, 118, 192, 121, G3)
    a.rect(190, 124, 193, 127, W2)
    for gx in (181, 199, 204):
        a.rect(gx, 126, gx + 2, 130, B1)
        a.dot(gx, 126, W1)
    # gig poster pasted on the retaining wall
    a.rect(413, 101, 463, 120, P2)
    a.rect(414, 102, 462, 119, F2)
    a.text((438, 104), "DONNA AND", B3, tiny=True, align="center")
    a.text((438, 112), "THE DYNAMOS", P3, tiny=True, align="center")
    # taverna table 2 (free - for now)
    _chair(a, 408, 1)
    _chair(a, 463, -1)
    _table(a, 420, 452)
    a.rect(434, 121, 437, 130, G3)
    a.rect(435, 118, 436, 121, G3)
    a.rect(434, 124, 437, 127, YL)
    a.rect(426, 126, 428, 130, B1)
    a.rect(443, 127, 449, 130, W2)

    # fallen petals + soft contact shadows
    r = random.Random(9)
    for _ in range(16):
        x = r.choice((r.randint(0, 40), r.randint(140, 176), r.randint(470, 510)))
        y = r.randint(153, 174)
        a.rect(x, y, x + 2, y + 1, P2)
    return f.im, a.im
