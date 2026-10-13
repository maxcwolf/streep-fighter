"""THE ENCHANTED WOODS - a moonlit clearing.  The Witch's stage (Into the Woods)."""
import math
import random

from PIL import Image, ImageDraw

from bg import BAYER, Art
from stages import FAR_W, STAGE_H, STAGE_W

GROUND_Y = 148          # where the undergrowth meets the clearing floor

# ---- main-layer palette (kept tight: ~55 colours)
BK0, BK1, BK2, BK3 = "#18143c", "#2c2464", "#483c90", "#7060b8"      # violet bark
RIM, RIMH = "#8ce4e8", "#d4fcf0"                                      # moonlit rim
FOL0, FOL1, FOL2, FOL3 = "#0c2c48", "#14505c", "#1c7c6c", "#48bc90"  # leaves
BU0, BU1, BU2, BU3 = "#1c5870", "#287c84", "#40a090", "#84dcb8"      # misted undergrowth
MOSS0, MOSS1, MOSS2 = "#226c70", "#2c8874", "#44a480"
DIRT0, DIRT1, DIRT2 = "#645c98", "#7c74ac", "#9890c4"
DIRTS, MOSSS = "#4c4884", "#1c5068"                                  # in cast shadow
MID0, MID1, MIST = "#3c5c98", "#4c78ac", "#5cacbc"                    # mid-distance trunks
G0, G1, G2, G3 = "#14583c", "#209048", "#48c450", "#a8f068"          # beanstalk
RED0, RED1, RED2 = "#8c1848", "#d8283c", "#f8687c"
COW0, COW1, COW2 = "#eef0fc", "#a8b0e0", "#f098b0"
GOLD0, GOLD1, GOLD2 = "#c88820", "#f8d040", "#fcf8b0"
ORA0, ORA1 = "#c84838", "#f89038"
PLK0, PLK1 = "#7c5848", "#c49868"


def _dth(x, y, f):
    return f * 16 > BAYER[y & 3][x & 3] + 0.5


def _hash(i, j):
    n = (i * 374761393 + j * 668265263) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0


def ramp(a, x, y, v, cols):
    """Plot one pixel from a colour ramp, ordered-dithered between steps."""
    if 0 <= x < a.w and 0 <= y < a.h:
        n = len(cols) - 1
        v = min(max(v, 0.0), n)
        i = min(int(v), n - 1)
        a.p[x, y] = a.c(cols[i + 1] if _dth(x, y, v - i) else cols[i])


def disc(a, cx, cy, r, col, level=1.0):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r and (level >= 1 or _dth(x, y, level)):
                a.dot(x, y, col)


def dither_poly(a, pts, col, level):
    m = Image.new("1", (a.w, a.h), 0)
    ImageDraw.Draw(m).polygon([(int(x), int(y)) for x, y in pts], fill=1)
    mp = m.load()
    x0, x1 = max(int(min(p[0] for p in pts)), 0), min(int(max(p[0] for p in pts)) + 1, a.w)
    y0, y1 = max(int(min(p[1] for p in pts)), 0), min(int(max(p[1] for p in pts)) + 1, a.h)
    for y in range(y0, y1):
        for x in range(x0, x1):
            if mp[x, y] and _dth(x, y, level):
                a.dot(x, y, col)


def foliage(a, blobs, cols, light="down"):
    """Paint the union of ellipses as one leaf mass; the edge facing `light`
    (down = canopy lit from below, up = bushes lit from above) gets the rim."""
    m = Image.new("1", (a.w, a.h), 0)
    d = ImageDraw.Draw(m)
    for cx, cy, rx, ry in blobs:
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=1)
    mp = m.load()
    step = 1 if light == "down" else -1
    deep, body, mid, rim = cols
    for x in range(a.w):
        for y in range(a.h):
            if not mp[x, y]:
                continue
            k, yy = 0, y + step
            while k < 8 and 0 <= yy < a.h and mp[x, yy]:
                k += 1
                yy += step
            if not 0 <= yy < a.h:
                k = 8
            if k == 0:
                c = rim
            elif k <= 2:
                c = mid
            elif k <= 4:
                c = mid if _dth(x, y, 0.5 if k == 3 else 0.25) else body
            elif k <= 7:
                c = body
            else:
                c = deep if _dth(x, y, 0.75) else body
            a.dot(x, y, c)


def _path(pts, step=1.0):
    out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(int(max(abs(x1 - x0), abs(y1 - y0)) / step), 1)
        for i in range(n):
            out.append((x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n))
    out.append(pts[-1])
    return out


def limb(a, pts, w0, w1, cols=(BK0, BK1, BK3), top=None):
    """Tapering branch / root with a dark outline and a lit upper edge."""
    line, body, hi = cols
    sm = _path(pts)
    n = max(len(sm) - 1, 1)

    def blob(x, y, w, col):
        w = max(int(round(w)), 1)
        x, y = int(round(x - w / 2.0)), int(round(y - w / 2.0))
        if w >= 4:
            a.ellipse(x, y, x + w, y + w, col)
        else:
            a.rect(x, y, x + w, y + w, col)
    for i, (x, y) in enumerate(sm):
        blob(x, y, w0 + (w1 - w0) * i / n + 2, line)
    for i, (x, y) in enumerate(sm):
        blob(x, y, w0 + (w1 - w0) * i / n, body)
    for i, (x, y) in enumerate(sm):
        w = w0 + (w1 - w0) * i / n
        if w >= 3:
            blob(x, y - w / 2.0 + 1.5, max(w / 3.0, 1), hi)
        if top:
            a.dot(int(round(x)), int(round(y - w / 2.0)), top)


def trunk(a, cx, y0, y1, hw, lit, seed, flare=14, flare_h=36, sway=3.0, top_flare=7, furrows=5):
    """Gnarled back-lit trunk.  lit = +1 if the moon is to its right, -1 left."""
    r = random.Random(seed)
    ph = r.uniform(0, 6.28)
    cols = [BK3, BK2, BK1, BK0]
    spans = {}
    for y in range(y0, y1):
        c = cx + sway * math.sin(y / 23.0 + ph) + sway * 0.5 * math.sin(y / 9.0 + ph * 2)
        w = hw + 1.3 * math.sin(y / 6.0 + ph)
        if y > y1 - flare_h:
            w += flare * ((y - (y1 - flare_h)) / float(flare_h)) ** 2
        if y < y0 + 44:
            w += top_flare * (1 - (y - y0) / 44.0) ** 2
        xl, xr = int(round(c - w)), int(round(c + w))
        spans[y] = (xl, xr)
        n = float(xr - xl)
        for x in range(xl, xr + 1):
            t = (x - xl) / n
            if lit > 0:
                t = 1 - t
            if t < 0.16:
                v = t / 0.16
            elif t < 0.58:
                v = 1 + (t - 0.16) / 0.42
            else:
                v = 2 + (t - 0.58) / 0.42 * 0.85
            ramp(a, x, y, v, cols)
        le, de = (xr, xl) if lit > 0 else (xl, xr)
        a.dot(le, y, RIM)
        a.dot(le - lit, y, BK3)
        a.dot(de, y, BK0)
    order = [a.c(c) for c in cols]

    def nudge(x, y, k):
        if 0 <= x < a.w and 0 <= y < a.h and a.p[x, y] in order:
            i = order.index(a.p[x, y])
            a.p[x, y] = order[min(max(i + k, 0), 3)]
    for j in range(furrows):
        tj = (j + 1.0) / (furrows + 1)
        on, run, fph = True, r.randint(6, 24), r.uniform(0, 6.28)
        for y in range(y0, y1):
            run -= 1
            if run <= 0:
                on = not on
                run = r.randint(12, 36) if on else r.randint(3, 8)
            if not on:
                continue
            xl, xr = spans[y]
            x = int(xl + (tj + 0.04 * math.sin(y / 8.0 + fph)) * (xr - xl))
            if xl + 2 < x < xr - 2:
                nudge(x, y, 1)
                nudge(x + lit, y, -1)
    return spans


def pine(a, x, base, h, w, col):
    tiers = max(h // 7, 2)
    for i in range(tiers):
        ty = base - h + i * (h - 4) // tiers
        half = 2 + (i + 1) * w // (2 * tiers)
        a.poly([(x, ty), (x + half, ty + (h // tiers) + 4), (x - half, ty + (h // tiers) + 4)], col)
    a.rect(x - 1, base - 6, x + 1, base + 12, col)


def mushroom(a, x, y, w, h):
    """Glowing toadstool, foot at (x, y)."""
    for i in range(-w, w + 1):                    # warm light pooling on the ground
        if (i + y) & 1:
            a.dot(x + i, y + 1, ORA1)
        elif abs(i) < w - 1:
            a.dot(x + i, y, ORA0)
    a.rect(x - 1, y - h, x + 1, y + 1, GOLD2)
    a.dot(x, y, GOLD1)
    top = y - h - (w // 2)
    for j in range(w // 2 + 1):
        half = int(round(math.sqrt(max((w / 2.0) ** 2 - (w / 2.0 - j) ** 2, 0)) * 1.25))
        a.rect(x - half, top + j, x + half, top + j + 1, ORA1)
    a.rect(x - w // 2 - 1, y - h, x + w // 2 + 1, y - h + 1, ORA0)
    a.dot(x - 1, top + 1, GOLD2)
    if w >= 6:
        a.dot(x + 2, top + 2, GOLD2)
        a.dot(x - 3, top + 3, GOLD1)


def firefly(a, x, y, big=False):
    a.dot(x, y, GOLD2)
    if big:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            a.dot(x + dx, y + dy, G3)


COW = [                      # Milky White's head, face-on
    "....H.........H....",
    "...KHK.......KHK...",
    "...KHHK.....KHHK...",
    "KKK.KHKKKKKKKHK.KKK",
    "KccKKWWWWWWWSSKKccK",
    ".KPcKWWWWWWSSSSKcPK",
    "..KKKWWWWWWSSSSSKK.",
    "....KWKKWWWSSKWSK..",
    "....KWKKWWWSSKKSK..",
    "....KWWWWWWWSSSSK..",
    "....KcWWWWWWWSSWK..",
    "....KPPPPPPPPPPPK..",
    "...KPPPPPPPPPPPPPK.",
    "...KPPKKPPPPPKKPPK.",
    "...KPPPPPPPPPPPPPK.",
    "....KKPPPPPPPPPKK..",
    "......KKKKKKKKK....",
]
COW_PAL = {"K": BK0, "W": COW0, "c": COW1, "P": COW2, "H": GOLD2, "S": BK1}

SLIPPER = [
    ".......yy..",
    "......yYYg.",
    ".yy..yYYYg.",
    "yYYyyYYYgg.",
    "gYYYYYgg.g.",
    ".gggg....g.",
]
SLIPPER_PAL = {"y": GOLD2, "Y": GOLD1, "g": GOLD0}


def build_far():
    f = Art(FAR_W, STAGE_H)
    f.vgrad(0, 0, FAR_W, 116, ["#10104c", "#1c1c68", "#2c2888", "#3c44a4", "#4470b8", "#5ca0c4"])
    r = random.Random(7)
    for _ in range(90):                                   # stars
        x, y = r.randrange(FAR_W), r.randrange(0, 78)
        f.dot(x, y, "#c8d0fc" if r.random() < 0.4 else "#7c88d8")
    for x, y in ((40, 22), (118, 12), (196, 30), (330, 16), (398, 34), (300, 52), (70, 52)):
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            f.dot(x + dx, y + dy, "#e8ecfc" if not (dx or dy) else "#98a4ec")

    # ---- the moon
    mx, my, mr = 252, 58, 32
    disc(f, mx, my, mr + 15, "#3440a0", 0.25)
    disc(f, mx, my, mr + 9, "#4c60c0", 0.5)
    disc(f, mx, my, mr + 4, "#84a4e4", 0.5)
    disc(f, mx, my, mr + 1, "#b8d0f0")
    for y in range(my - mr, my + mr + 1):
        for x in range(mx - mr, mx + mr + 1):
            if (x - mx) ** 2 + (y - my) ** 2 <= mr * mr:
                d2 = math.hypot(x - (mx + 5), y - (my - 5))
                ramp(f, x, y, (d2 - mr + 9) / 9.0, ["#fcf8cc", "#f4e4a0", "#d8c088"])
    for cx, cy, cr in ((240, 46, 6), (262, 64, 8), (246, 70, 4), (268, 42, 4), (234, 60, 3), (258, 80, 3), (274, 56, 2)):
        disc(f, cx, cy, cr, "#e4cc88")
        disc(f, cx + 1, cy + 1, cr - 1, "#f0dc98")
    # ---- cloud wisps
    for cx, cy, w in ((60, 40, 70), (300, 70, 90), (180, 24, 60), (400, 50, 60), (220, 82, 54)):
        f.rect(cx + 10, cy, cx + w - 16, cy + 1, "#7c88dc")
        f.rect(cx + 4, cy + 1, cx + w - 8, cy + 2, "#5c64c0")
        f.rect(cx, cy + 2, cx + w, cy + 4, "#3c3c98")
        f.rect(cx + 12, cy + 4, cx + w - 6, cy + 5, "#3c3c98")
        f.dither(cx + 20, cy + 5, cx + w - 20, cy + 6, "#3c3c98", 0.5)
    # ---- birds crossing the moon
    for bx, by in ((228, 44), (238, 38), (250, 46), (262, 36), (274, 44)):
        for dx, dy in ((-2, -1), (-1, 0), (0, 1), (1, 0), (2, -1)):
            f.dot(bx + dx, by + dy, "#2c2470")

    # ---- far ridge with Rapunzel's tower on its hill
    tx = 150

    def ridge(x):
        return 99 + 4 * math.sin(x / 31.0) + 2.5 * math.sin(x / 11.0 + 2) - 17 * math.exp(-((x - tx) / 34.0) ** 2)
    for x in range(FAR_W):
        ry = int(ridge(x))
        f.rect(x, ry, x + 1, 130, "#5c8cd0")
        f.dot(x, ry, "#84b4e4")
    f.rect(tx - 6, 52, tx + 6, 90, "#8c98dc")            # shaft
    f.rect(tx - 6, 52, tx - 2, 90, "#5460a8")
    f.rect(tx + 5, 52, tx + 6, 90, "#c4d0f8")
    f.rect(tx - 9, 42, tx + 9, 54, "#8c98dc")            # chamber
    f.rect(tx - 9, 42, tx - 4, 54, "#5460a8")
    f.rect(tx + 8, 42, tx + 9, 54, "#c4d0f8")
    f.rect(tx - 9, 53, tx + 9, 54, "#343c84")
    for i in range(-9, 9, 4):                            # corbels
        f.rect(tx + i, 54, tx + i + 2, 56, "#5460a8")
    f.poly([(tx - 11, 42), (tx, 24), (tx + 10, 42)], "#2c2470")
    f.poly([(tx + 2, 42), (tx, 24), (tx + 10, 42)], "#5c58b0")
    f.rect(tx, 18, tx + 1, 25, "#2c2470")
    f.rect(tx + 1, 18, tx + 5, 21, "#d8283c")            # pennant
    for sx, sy in ((-4, 62), (1, 70), (-3, 80), (3, 60), (2, 84), (-5, 74)):   # stone courses
        f.rect(tx + sx, sy, tx + sx + 2, sy + 1, "#6c78c0")
    f.rect(tx - 2, 45, tx + 2, 51, "#f89c40")            # the lit window
    f.rect(tx - 1, 44, tx + 1, 45, "#f89c40")
    f.rect(tx - 1, 46, tx + 1, 51, "#fce890")
    for y in range(51, 88):                              # the rope of golden hair
        hx = tx + (1 if (y // 5) % 2 else 0)
        f.dot(hx, y, "#f8d040")
        f.dot(hx - 1, y, "#c88820" if y % 3 == 0 else "#f8d040")
    f.rect(tx - 1, 88, tx + 2, 90, "#f8d040")

    # ---- treelines, each one sinking into the ground mist
    r = random.Random(11)
    x = -6
    while x < FAR_W + 10:
        rr = r.randint(6, 11)
        disc(f, x, 104 - r.randint(0, 5), rr, "#3c62a8")
        x += r.randint(7, 13)
    f.rect(0, 104, FAR_W, 130, "#3c62a8")
    f.dither(0, 100, FAR_W, 106, "#5ca0c4", 0.25)
    x = 4
    while x < FAR_W:
        if abs(x - tx) > 16:
            h = r.randint(22, 44)
            pine(f, x, 118, h, r.randint(12, 18), "#2c4890")
        x += r.randint(9, 20)
    f.rect(0, 114, FAR_W, 130, "#2c4890")
    # ---- moonlit ground mist
    f.dither(0, 100, FAR_W, 106, MIST, 0.25)
    f.dither(0, 106, FAR_W, 112, MIST, 0.5)
    f.dither(0, 112, FAR_W, 118, MIST, 0.75)
    f.vgrad(0, 118, FAR_W, 152, [MIST, "#74c4c4", "#94d8cc"])
    f.rect(0, 152, FAR_W, STAGE_H, "#94d8cc")
    for i in range(15):                                   # drifting streaks
        x, y, w = r.randrange(-40, FAR_W), r.randrange(108, 146), r.randrange(50, 120)
        c = "#94d8cc" if y < 126 else "#b4ecd8"
        f.rect(x + 14, y, x + w - 22, y + 1, c)
        f.rect(x, y + 1, x + w, y + 2, c)
        f.rect(x + 8, y + 2, x + w - 10, y + 3, c)
    return f


def ground(a, shadows):
    """Mossy dirt in perspective: hashed patches on a grid converging on (vx, vy);
    moss crowds the back and front edges, the fight lane stays bare and calm.
    `shadows` = polygons of cast shadow, painted one flat step darker."""
    core, pen = Image.new("1", (a.w, a.h), 0), Image.new("1", (a.w, a.h), 0)
    for pts in shadows:
        ImageDraw.Draw(core).polygon(pts, fill=1)
        (x0, y0), (x1, y1), (x2, y2), (x3, y3) = pts
        ImageDraw.Draw(pen).polygon([(x0 - 3, y0), (x1 + 3, y1), (x2 + 8, y2), (x3 - 8, y3)], fill=1)
    core, pen = core.load(), pen.load()
    dirt, moss = [DIRT2, DIRT1, DIRT0, DIRTS], [MOSS2, MOSS1, MOSS0, MOSSS]
    vx, vy, depth, cols = 256, 116, 420.0, 2.4
    for y in range(GROUND_Y, STAGE_H):
        for x in range(STAGE_W):
            d = max(y - vy + 1.5 * math.sin(x * 0.07) + 0.9 * math.sin(x * 0.19 + 1.3), 8.0)
            row = int(depth / d)
            u = (x - vx) / d * cols + 1000 + (row * 0.37) % 1.0 + 0.10 * math.sin(y * 0.8 + row)
            cell = int(u)
            h1, h2 = _hash(row, cell), _hash(cell + 91, row + 17)
            yc = vy + depth / (row + 0.5)
            lane = abs(yc - 186) / 27.0
            p_moss = min(max(lane * lane * 0.95, 0.07), 0.96)
            if h1 < p_moss:
                ramp_, i = moss, 0 if h2 < 0.3 else 1 if h2 < 0.8 else 2
            else:
                ramp_, i = dirt, 0 if h2 < 0.22 else 1 if h2 < 0.8 else 2
            if core[x, y] or (pen[x, y] and _dth(x, y, 0.5)):
                i += 1
            a.p[x, y] = a.c(ramp_[i])


def bean_leaf(a, sx, sy, d):
    top = [(sx, sy), (sx + d * 5, sy - 7), (sx + d * 13, sy - 9), (sx + d * 21, sy - 4), (sx + d * 24, sy + 1)]
    pts = top + [(sx + d * 15, sy + 5), (sx + d * 6, sy + 4)]
    a.poly(pts, G1)
    a.poly(top, G2)
    a.line(pts + [pts[0]], G0)
    a.line([(sx, sy), (sx + d * 24, sy + 1)], G0)
    for i in (7, 13, 18):
        a.line([(sx + d * i, sy - 1), (sx + d * (i + 3), sy - 5)], G3)


def tendril(a, ox, oy, d):
    for i in range(30):
        t = i / 29.0
        ang, rad = t * 3.6 * math.pi, 5.5 * (1 - t) + 0.5
        a.dot(int(round(ox + d * rad * math.cos(ang))), int(round(oy - rad * math.sin(ang))), G2)


def beanstalk(a, cx, y1):
    def centre(y, k):
        return cx + (150 - y) * 0.07 + k * 7.0 * math.sin(y / 12.0)
    a.ellipse(cx - 15, y1 - 5, cx + 17, y1 + 6, DIRT0)             # burst earth
    a.ellipse(cx - 12, y1 - 6, cx + 2, y1 + 1, DIRT1)
    a.ellipse(cx + 3, y1 - 5, cx + 14, y1 + 2, DIRT1)
    a.rect(cx - 9, y1 - 5, cx - 3, y1 - 4, DIRT2)
    a.rect(cx + 6, y1 - 4, cx + 11, y1 - 3, DIRT2)
    for k in range(4):                                             # leaves at each bend
        y = int(18.85 + 37.7 * k)
        d = 1 if k % 2 == 0 else -1
        bean_leaf(a, int(centre(y, 1)) + d * 3, y, d)
    for y, d in ((40, -1), (76, 1), (112, -1)):
        tendril(a, int(centre(y, -1)) + d * 9, y, d)
        a.line([(int(centre(y, -1)), y + 2), (int(centre(y, -1)) + d * 9, y + 5)], G2)
    for y in range(0, y1):
        front = 1 if math.cos(y / 12.0) > 0 else -1
        for k in (-front, front):
            w = 8 if k == 1 else 6
            xl = int(round(centre(y, k) - w / 2.0))
            a.dot(xl - 1, y, G0)
            a.dot(xl + w, y, G0)
            for i in range(w):
                a.dot(xl + i, y, G3 if i == 1 else G2 if i < w * 0.5 else G1 if i < w - 1 else G0)


def build():
    f = build_far()
    a = Art(STAGE_W, STAGE_H, mode="RGBA")
    r = random.Random(42)

    # ---- mid-distance trunks, half lost in the mist
    for mxc, mw, lean in ((230, 9, 0.03),):
        for y in range(0, GROUND_Y):
            c = mxc + lean * (y - 80) + 1.5 * math.sin(y / 19.0 + mxc)
            w = mw + (3 if y > 128 else 0) * (y - 128) / 20.0
            xl, xr = int(c - w / 2), int(c + w / 2) + 1
            a.rect(xl, y, xr, y + 1, MID1)
            a.rect(xl, y, xl + max(mw // 3, 1), y + 1, MID0)
        a.dither(mxc - 8, 112, mxc + 9, GROUND_Y, MIST, 0.25)
        a.dither(mxc - 8, 128, mxc + 9, GROUND_Y, MIST, 0.5)
    limb(a, [(232, 62), (244, 52), (252, 36), (256, 18)], 4, 2, (MID0, MID1, MID1))

    # ---- undergrowth along the back of the clearing (taller toward the big trees)
    blobs = []
    x = -8
    while x < STAGE_W + 10:
        side = max(0.0, 1 - min(abs(x - 88), abs(x - 424), abs(x - 6), abs(x - 506)) / 60.0)
        blobs.append((x, GROUND_Y + r.randint(-1, 2), r.randint(7, 11), int(r.randint(7, 11) + 9 * side)))
        x += r.randint(6, 10)
    foliage(a, blobs, (BU0, BU1, BU2, BU3), light="up")

    # ---- the clearing floor
    # long tree shadows are thrown toward the camera (the moon is behind the trees)
    ground(a, [[(60, 150), (118, 150), (96, 216), (-30, 216)],
               [(398, 150), (452, 150), (560, 216), (424, 216)],
               [(-6, 150), (34, 150), (-10, 200), (-12, 216)],
               [(482, 150), (518, 150), (524, 216), (520, 200)],
               [(224, 148), (238, 148), (226, 172), (204, 172)]])
    a.dither(0, GROUND_Y, STAGE_W, GROUND_Y + 6, MOSS0, 0.75)
    a.dither(0, GROUND_Y + 6, STAGE_W, GROUND_Y + 12, MOSS0, 0.5)
    a.dither(0, GROUND_Y + 12, STAGE_W, GROUND_Y + 18, MOSS0, 0.25)
    tx = 2
    while tx < STAGE_W:                                            # tufts breaking the ground line
        for dx, hh in ((0, 2), (1, 4), (2, 3), (4, 2)) if r.random() < 0.5 else ((0, 1), (1, 3), (3, 2)):
            a.rect(tx + dx, GROUND_Y - hh + 2, tx + dx + 1, GROUND_Y + 2, BU1 if dx != 1 else BU2)
        tx += r.randint(6, 21)

    # ---- Milky White, peeking from behind the right-hand tree
    a.rect(381, 127, 408, 147, BK0)
    a.rect(382, 128, 408, 146, COW0)
    a.rect(382, 141, 408, 146, COW1)
    a.ellipse(393, 129, 404, 139, BK1)
    for lx in (383, 392):
        a.rect(lx - 1, 146, lx + 5, 155, BK0)
        a.rect(lx, 146, lx + 4, 152, COW0)
        a.rect(lx + 3, 146, lx + 4, 152, COW1)
    a.stamp(COW, COW_PAL, 366, 114)

    # ---- the beanstalk
    beanstalk(a, 346, 152)

    # ---- the big gnarled trees
    trunk(a, 8, 0, 160, 19, +1, seed=1, flare=10)
    trunk(a, 506, 0, 160, 18, -1, seed=4, flare=10)
    for pts, w0, w1 in (([(72, 62), (58, 48), (46, 30), (40, 12)], 7, 3),
                        ([(102, 42), (116, 28), (128, 14), (134, 0)], 7, 3),
                        ([(104, 72), (116, 65), (128, 61), (140, 56)], 6, 2),
                        ([(406, 64), (392, 56), (380, 50), (368, 38), (362, 22)], 6, 2),
                        ([(442, 56), (458, 44), (470, 26), (474, 10)], 7, 3),
                        ([(410, 38), (398, 24), (392, 8)], 6, 3)):
        limb(a, pts, w0, w1)
    for pts, w0, w1 in (([(104, 148), (118, 155), (132, 158), (148, 160)], 5, 1),      # roots
                        ([(72, 148), (58, 156), (44, 160), (30, 162)], 5, 1),
                        ([(96, 152), (104, 162), (112, 167), (124, 169)], 4, 1),
                        ([(408, 148), (394, 155), (382, 158), (368, 160)], 5, 1),
                        ([(440, 148), (454, 156), (468, 160), (484, 162)], 5, 1),
                        ([(416, 152), (408, 162), (400, 167), (388, 169)], 4, 1)):
        limb(a, pts, w0, w1)
    trunk(a, 88, 0, 158, 20, +1, seed=2, flare=15)
    trunk(a, 424, 0, 158, 21, -1, seed=3, flare=15)

    # nest with a golden egg (right tree), two white birds (left tree)
    a.rect(381, 46, 393, 50, PLK0)
    a.rect(380, 45, 394, 47, PLK1)
    a.dot(382, 48, PLK1)
    a.dot(387, 49, PLK1)
    a.dot(391, 48, PLK1)
    a.ellipse(384, 40, 390, 47, GOLD1)
    a.dot(385, 42, GOLD2)
    a.dot(388, 45, GOLD0)
    for bx, by, d in ((112, 60, 1), (119, 58, -1)):
        a.rect(bx, by, bx + 4, by + 3, COW0)
        a.rect(bx + (3 if d > 0 else -1), by - 2, bx + (5 if d > 0 else 1), by, COW0)
        a.dot(bx + (5 if d > 0 else -2), by - 1, GOLD1)
        a.dot(bx + (-1 if d > 0 else 4), by + 1, COW1)
        a.rect(bx, by + 2, bx + 4, by + 3, COW1)
    # moss creeping up the roots + glowing bracket fungi on the bark
    for cx, lit in ((88, 1), (424, -1)):
        mb = [(cx + lit * 16 + i * 5 * -lit, 151 + (i * 3) % 5, 5, 4) for i in range(6)]
        if lit > 0:
            mb += [(cx + 22, 139, 4, 6), (cx + 14, 144, 5, 4)]
        foliage(a, mb, (MOSS0, MOSS0, MOSS1, MOSS2), light="up")
        for i, by in enumerate((104, 113, 124)):
            bx = cx + lit * (15 - i * 2)
            a.rect(bx - 3, by, bx + 4, by + 1, GOLD2)
            a.rect(bx - 4, by + 1, bx + 5, by + 2, ORA1)
            a.rect(bx - 3, by + 2, bx + 4, by + 3, ORA0)
    # owl in a hollow (left tree)
    a.ellipse(80, 82, 93, 98, BK0)
    a.rect(83, 88, 85, 90, GOLD1)
    a.rect(88, 88, 90, 90, GOLD1)
    a.dot(83, 88, GOLD2)
    a.dot(88, 88, GOLD2)
    a.dot(86, 91, GOLD0)
    # signpost planks (right tree)
    for y, label, d in ((74, "GRANNY'S", -1), (87, "FESTIVAL", 1)):
        a.rect(406, y, 443, y + 10, PLK0)
        a.rect(406, y, 443, y + 9, PLK1)
        tip = 405 if d < 0 else 443
        a.poly([(tip, y), (tip + d * 5, y + 4), (tip + d * 5, y + 5), (tip, y + 9)], PLK1)
        a.text((409, y + 2), label, BK0, tiny=True)

    # ---- red cape snagged on a branch
    cape = [(126, 59), (132, 58), (135, 63), (137, 72), (141, 84), (144, 96), (140, 94), (137, 98),
            (133, 95), (129, 99), (125, 95), (122, 97), (121, 86), (123, 74), (125, 65)]
    a.poly(cape, RED1)
    a.poly([(133, 64), (135, 63), (137, 72), (141, 84), (144, 96), (140, 94), (137, 98), (135, 96), (135, 80)], RED0)
    a.line([(126, 66), (123, 86), (123, 94)], RED2)
    a.line([(129, 68), (128, 96)], RED0)
    a.line(cape + [cape[0]], RED0)
    a.ellipse(125, 55, 135, 63, RED1)
    a.rect(128, 58, 132, 61, RED0)
    a.rect(127, 56, 131, 57, RED2)

    # ---- stump with the golden slipper
    a.hgrad(153, 136, 176, 155, [BK1, BK2, BK2, BK3])
    a.poly([(153, 150), (148, 156), (153, 156)], BK1)
    a.poly([(175, 150), (181, 156), (175, 156)], BK3)
    a.rect(175, 136, 176, 155, RIM)
    for sx in (158, 163, 169):
        a.rect(sx, 141, sx + 1, 153, BK1)
    a.ellipse(151, 131, 178, 142, BK0)
    a.ellipse(152, 131, 177, 141, DIRT2)
    a.ellipse(156, 133, 173, 139, DIRT1)
    a.ellipse(160, 134, 169, 138, DIRT2)
    a.stamp(SLIPPER, SLIPPER_PAL, 158, 128)
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, 2), (0, -2)):
        a.dot(173 + dx, 126 + dy, GOLD2)

    # ---- canopy: two scalloped leaf layers, hanging lower around the big trees
    def dep(x):
        return 16 + 26 * max(0.0, 1 - min(abs(x - 88), abs(x - 424), abs(x - 8), abs(x - 506)) / 70.0)
    back, front = [], []
    x = -12
    while x < STAGE_W + 14:
        back.append((x, r.randint(0, int(dep(x)) - 4), r.randint(10, 15), r.randint(6, 10)))
        x += r.randint(8, 12)
    x = -8
    while x < STAGE_W + 14:
        front.append((x, r.randint(-4, int(dep(x)) - 12), r.randint(8, 12), r.randint(5, 8)))
        x += r.randint(9, 14)
    foliage(a, back, (FOL0, FOL0, FOL1, FOL2))
    foliage(a, front, (FOL0, FOL1, FOL2, FOL3))

    # ---- hanging vines and swags
    for vx, ln in ((30, 44), (58, 52), (118, 40), (160, 26), (198, 18), (268, 14), (300, 20),
                   (346, 30), (392, 46), (460, 46), (486, 54)):
        y0 = 6
        ph = vx * 0.7
        for y in range(y0, y0 + ln + int(dep(vx)) - 16):
            x = int(round(vx + 1.6 * math.sin(y / 7.0 + ph)))
            a.dot(x, y, FOL1)
            if y % 5 == 0 and y > 12:
                d = 1 if (y // 5) % 2 else -1
                a.dot(x + d, y, FOL2)
                a.dot(x + d * 2, y - 1, FOL3)
    for (x0, y0), (x1, y1), sag in (((108, 30), (232, 24), 14), ((236, 20), (332, 22), 8), ((338, 26), (404, 36), 10)):
        for x in range(x0, x1 + 1):
            t = (x - x0) / float(x1 - x0)
            y = int(round(y0 + (y1 - y0) * t + sag * 4 * t * (1 - t)))
            a.dot(x, y, FOL1)
            if x % 6 == 0:
                a.dot(x, y + 1, FOL2)
                a.dot(x + 1, y + 2, FOL3)

    # ---- glowing mushrooms
    for mx, my, mw, mh in ((122, 160, 8, 5), (132, 163, 6, 3), (113, 163, 4, 2), (182, 158, 6, 4), (189, 160, 4, 2),
                           (394, 161, 8, 5), (384, 164, 6, 3), (456, 162, 6, 4), (58, 162, 8, 4), (48, 164, 4, 3),
                           (146, 158, 4, 3), (466, 164, 4, 2)):
        mushroom(a, mx, my, mw, mh)

    # ---- fallen leaves + pebbles, scaled with depth
    for _ in range(70):
        x, y = r.randrange(STAGE_W), r.randrange(GROUND_Y + 8, STAGE_H - 3)
        if 170 < y < 206 and r.random() < 0.6:
            continue
        c = r.choice([BU3, MOSS2, FOL2, ORA1, GOLD1, BU3, DIRT2])
        if y < 168:
            a.rect(x, y, x + 2, y + 1, c)
        elif y < 190:
            a.rect(x, y, x + 2, y + 1, c)
            a.rect(x + 1, y + 1, x + 3, y + 2, c)
        else:
            a.rect(x, y, x + 3, y + 1, c)
            a.rect(x + 1, y + 1, x + 4, y + 2, c)
            a.dot(x + 4, y + 2, BK1)

    # ---- foreground grass along the bottom edge
    for x in range(0, STAGE_W, 2):
        env = 0.5 + 0.5 * math.sin(x / 23.0) * math.sin(x / 7.0 + 1)
        h = int(2 + 6 * env * _hash(x, 5) + 2 * _hash(x, 9))
        a.rect(x, STAGE_H - h, x + 1, STAGE_H, FOL1 if _hash(x, 3) < 0.6 else FOL0)
        a.dot(x, STAGE_H - h, FOL2)
        if h > 5:
            a.dot(x + 1, STAGE_H - h - 1, FOL2)

    # ---- eyes in the undergrowth (the Wolf) + fireflies
    for ex, ey, d in ((36, 138, 1), (476, 139, -1)):
        a.ellipse(ex - 7, ey - 5, ex + 8, ey + 7, FOL0)
        a.poly([(ex - 6, ey - 2), (ex - 6, ey - 12), (ex - 2, ey - 4)], FOL0)        # tall ears
        a.poly([(ex + 2, ey - 4), (ex + 6, ey - 12), (ex + 7, ey - 2)], FOL0)
        a.poly([(ex - 3, ey + 3), (ex + 3, ey + 3), (ex + d * 2 + 2, ey + 11), (ex + d * 2 - 2, ey + 11)], FOL0)   # muzzle
        a.rect(ex - 4, ey, ex - 2, ey + 1, GOLD1)
        a.dot(ex - 2, ey + 1, GOLD1)
        a.rect(ex + 3, ey, ex + 5, ey + 1, GOLD1)
        a.dot(ex + 3, ey + 1, GOLD1)
        a.rect(ex + d * 2 - 1, ey + 9, ex + d * 2 + 2, ey + 10, BK2)                   # nose
    for i, (fx, fy) in enumerate(((144, 112), (198, 92), (270, 108), (304, 96), (340, 118), (46, 110), (468, 104),
                                  (170, 66), (288, 52), (382, 92), (24, 84), (492, 78), (214, 128), (60, 132),
                                  (446, 128), (112, 120), (318, 134), (250, 140))):
        firefly(a, fx, fy, big=i % 3 == 0)
    return f.im, a.im
