"""Background / UI painting helpers: hard-edged fills, ordered-dither
gradients and ASCII stamps on a plain RGB canvas (no anti-aliasing)."""
import random

from PIL import Image, ImageDraw

import font
from px import rgb

BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


class Art:
    def __init__(self, w, h, fill="#000000", mode="RGB"):
        self.w, self.h = w, h
        f = rgb(fill) if mode == "RGB" else (0, 0, 0, 0)
        self.im = Image.new(mode, (w, h), f)
        self.d = ImageDraw.Draw(self.im)
        self.p = self.im.load()
        self.rgba = mode == "RGBA"

    def c(self, col):
        col = rgb(col)
        return col + (255,) if self.rgba else col

    def clear(self, x0, y0, x1, y1):
        """Punch a transparent hole (RGBA canvases) so the far layer shows."""
        if self.rgba and x1 > x0 and y1 > y0:
            self.d.rectangle([x0, y0, x1 - 1, y1 - 1], fill=(0, 0, 0, 0))

    def clear_poly(self, pts):
        if self.rgba:
            self.d.polygon([(int(x), int(y)) for x, y in pts], fill=(0, 0, 0, 0))

    def rect(self, x0, y0, x1, y1, col):
        if x1 > x0 and y1 > y0:
            self.d.rectangle([x0, y0, x1 - 1, y1 - 1], fill=self.c(col))

    def frame(self, x0, y0, x1, y1, col, t=1):
        for i in range(t):
            self.d.rectangle([x0 + i, y0 + i, x1 - 1 - i, y1 - 1 - i], outline=self.c(col))

    def dot(self, x, y, col):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.p[x, y] = self.c(col)

    def line(self, pts, col, width=1):
        self.d.line([(int(x), int(y)) for x, y in pts], fill=self.c(col), width=width)

    def poly(self, pts, col):
        self.d.polygon([(int(x), int(y)) for x, y in pts], fill=self.c(col))

    def ellipse(self, x0, y0, x1, y1, col):
        self.d.ellipse([x0, y0, x1 - 1, y1 - 1], fill=self.c(col))

    def vgrad(self, x0, y0, x1, y1, cols):
        """Vertical gradient through `cols`, Bayer-dithered between steps."""
        cols = [self.c(c) for c in cols]
        n, h = len(cols) - 1, max(y1 - y0 - 1, 1)
        for y in range(max(y0, 0), min(y1, self.h)):
            t = (y - y0) / h * n
            i = min(int(t), n - 1)
            f = t - i
            for x in range(max(x0, 0), min(x1, self.w)):
                self.p[x, y] = cols[i + 1] if f * 16 > BAYER[y & 3][x & 3] + 0.5 else cols[i]

    def hgrad(self, x0, y0, x1, y1, cols):
        cols = [self.c(c) for c in cols]
        n, w = len(cols) - 1, max(x1 - x0 - 1, 1)
        for x in range(max(x0, 0), min(x1, self.w)):
            t = (x - x0) / w * n
            i = min(int(t), n - 1)
            f = t - i
            for y in range(max(y0, 0), min(y1, self.h)):
                self.p[x, y] = cols[i + 1] if f * 16 > BAYER[y & 3][x & 3] + 0.5 else cols[i]

    def dither(self, x0, y0, x1, y1, col, level):
        """Overlay `col` on level (0..1) of the pixels, Bayer pattern."""
        col = self.c(col)
        for y in range(max(y0, 0), min(y1, self.h)):
            for x in range(max(x0, 0), min(x1, self.w)):
                if level * 16 > BAYER[y & 3][x & 3] + 0.5:
                    self.p[x, y] = col

    def stamp(self, rows, pal, x, y, flip=False):
        for j, row in enumerate(rows):
            if flip:
                row = row[::-1]
            for i, ch in enumerate(row):
                if ch not in ". ":
                    self.dot(x + i, y + j, pal[ch])

    def text(self, xy, s, col, **kw):
        for k in ("shadow", "outline"):
            if kw.get(k):
                kw[k] = rgb(kw[k])
        if kw.get("gradient"):
            kw["gradient"] = [rgb(c) for c in kw["gradient"]]
        return font.draw(self.im, xy, s, rgb(col), **kw)

    def paste(self, img, xy):
        if img.mode == "RGBA":
            self.im.paste(img, xy, img)
        else:
            self.im.paste(img, xy)


def skyline(a, x0, x1, base_y, col, lit=None, seed=1, hmin=14, hmax=60, wmin=8, wmax=22, lit_chance=0.3):
    """Row of flat skyscraper silhouettes with optional lit windows."""
    r = random.Random(seed)
    x = x0 - r.randint(0, 6)
    while x < x1:
        w, h = r.randint(wmin, wmax), r.randint(hmin, hmax)
        a.rect(max(x, x0), base_y - h, min(x + w, x1), base_y, col)
        if r.random() < 0.3 and w > 10:      # setback / antenna
            a.rect(max(x + 3, x0), base_y - h - 5, min(x + w - 3, x1), base_y - h, col)
            if x0 <= x + w // 2 < x1:
                a.rect(x + w // 2, base_y - h - 12, x + w // 2 + 1, base_y - h - 5, col)
        if lit:
            for wy in range(base_y - h + 3, base_y - 2, 4):
                for wx in range(x + 2, x + w - 2, 3):
                    if x0 <= wx < x1 and r.random() < lit_chance:
                        a.dot(wx, wy, lit)
                        a.dot(wx, wy + 1, lit)
        x += w + r.randint(0, 3)
