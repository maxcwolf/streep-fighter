"""Small effect sprites: hit sparks, dust, projectiles, the mesh shadow.
Each returns a horizontal strip of equally sized frames."""
import math

from PIL import Image

from bg import Art


def _star(a, cx, cy, r_out, r_in, n, col, phase=0.0):
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        t = phase + math.pi * i / n
        pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    a.poly(pts, col)


def _strip(frames):
    w, h = frames[0].size
    out = Image.new("RGBA", (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        out.paste(f, (i * w, 0))
    return out


def hitspark():
    fr = []
    for i in range(4):
        a = Art(32, 32, mode="RGBA")
        if i == 0:
            _star(a, 16, 16, 7, 2.5, 4, "#f87800")
            _star(a, 16, 16, 5, 2, 4, "#fcfcfc")
        elif i == 1:
            _star(a, 16, 16, 15, 5, 8, "#f83800", 0.2)
            _star(a, 16, 16, 13, 4.5, 8, "#fcd800", 0.2)
            _star(a, 16, 16, 8, 3, 8, "#fcfcfc", 0.2)
        elif i == 2:
            _star(a, 16, 16, 15.5, 8, 8, "#f87800", 0.6)
            _star(a, 16, 16, 13, 7, 8, "#fcd800", 0.6)
            a.ellipse(11, 11, 22, 22, "#fcf8a0")
            a.d.ellipse([12, 12, 19, 19], fill=(0, 0, 0, 0))
        else:
            for k in range(8):
                t = 0.6 + math.pi * k / 4
                x, y = int(16 + 13 * math.cos(t)), int(16 + 13 * math.sin(t))
                a.rect(x - 1, y - 1, x + 1, y + 1, "#fcd800")
                a.dot(int(16 + 8 * math.cos(t + 0.4)), int(16 + 8 * math.sin(t + 0.4)), "#f87800")
        fr.append(a.im)
    return _strip(fr)


def blockspark():
    fr = []
    for i in range(3):
        a = Art(24, 24, mode="RGBA")
        if i == 0:
            _star(a, 12, 12, 6, 2, 4, "#58a8f8")
            _star(a, 12, 12, 4, 1.5, 4, "#fcfcfc")
        elif i == 1:
            _star(a, 12, 12, 11, 3, 4, "#3070e8")
            _star(a, 12, 12, 9, 2.5, 4, "#a8e0fc")
            _star(a, 12, 12, 5, 2, 4, "#fcfcfc", math.pi / 4)
        else:
            for k in range(4):
                t = math.pi * k / 2
                a.rect(int(12 + 9 * math.cos(t)) - 1, int(12 + 9 * math.sin(t)) - 1,
                       int(12 + 9 * math.cos(t)) + 1, int(12 + 9 * math.sin(t)) + 1, "#a8e0fc")
        fr.append(a.im)
    return _strip(fr)


def dust():
    fr = []
    for i in range(4):
        a = Art(32, 16, mode="RGBA")
        spread, r = 3 + i * 3, 5 - i
        for sx in (-1, 1):
            cx, cy = 16 + sx * spread, 12 - i
            a.ellipse(cx - r - 1, cy - r, cx + r + 1, cy + r, "#a89878")
            a.ellipse(cx - r, cy - r, cx + r, cy + r - 1, "#e8dcc0")
            if r > 2:
                a.ellipse(cx - r + 1, cy - r, cx + r - 2, cy + r - 3, "#fcf8e8")
        fr.append(a.im)
    return _strip(fr)


def pot():
    a = Art(20, 20, mode="RGBA")
    a.rect(4, 6, 16, 16, "#3c1410")
    a.rect(5, 7, 15, 15, "#e87830")
    a.rect(5, 7, 8, 15, "#fcb060")
    a.rect(12, 7, 15, 15, "#b04c20")
    a.rect(5, 13, 15, 15, "#b04c20")
    a.rect(3, 4, 17, 7, "#3c1410")
    a.rect(4, 5, 16, 6, "#fcb060")
    a.rect(1, 9, 4, 12, "#3c1410")
    a.rect(16, 9, 19, 12, "#3c1410")
    a.rect(2, 10, 4, 11, "#b04c20")
    a.rect(16, 10, 18, 11, "#b04c20")
    a.rect(8, 2, 12, 4, "#3c1410")
    a.rect(9, 3, 11, 4, "#fcb060")
    return _strip([a.im.rotate(-90 * i) for i in range(4)])


def curse():
    fr = []
    for i in range(4):
        a = Art(24, 24, mode="RGBA")
        r = 7 if i % 2 == 0 else 8
        a.ellipse(12 - r - 1, 12 - r - 1, 12 + r + 1, 12 + r + 1, "#085030")
        a.ellipse(12 - r, 12 - r, 12 + r, 12 + r, "#20b858")
        a.ellipse(12 - r, 12 - r, 12 + r - 2, 12 + r - 2, "#58f878")
        a.ellipse(12 - r + 2, 12 - r + 1, 12 + r - 5, 12 + r - 6, "#e0ffd0")
        a.rect(8, 11, 11, 14, "#085030")          # skull eyes
        a.rect(13, 11, 16, 14, "#085030")
        a.rect(11, 15, 13, 17, "#085030")
        for k in range(5):
            t = i * 0.9 + k * 1.3
            a.dot(int(12 + (r + 3) * math.cos(t)), int(12 + (r + 3) * math.sin(t)), "#e0ffd0")
        fr.append(a.im)
    return _strip(fr)


def shadow():
    """Checker-mesh ellipse: the SNES way to fake a translucent shadow."""
    w, h = 46, 9
    a = Art(w, h, mode="RGBA")
    for y in range(h):
        for x in range(w):
            if ((x - w / 2 + 0.5) / (w / 2)) ** 2 + ((y - h / 2 + 0.5) / (h / 2)) ** 2 <= 1 and (x + y) % 2 == 0:
                a.dot(x, y, "#181030")
    return a.im
