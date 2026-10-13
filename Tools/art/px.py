"""Tiny pixel-art rasteriser used by every generator in this folder.

Everything is drawn as 1-bit masks (supersampled, then thresholded so edges
land on whole pixels), shaded with a 4-tone ramp by "how close is this pixel
to the lit / shadowed edge of its shape", and wrapped in a 1px dark outline.
That is the SNES/CPS-era sprite recipe: flat ramps, hard bands, no gradients,
no anti-aliasing.  PIL only - no numpy.
"""
import colorsys
import math

from PIL import Image, ImageChops, ImageDraw

SS = 4  # supersample factor for shape edges


# ---------------------------------------------------------------- colour
def rgb(h):
    if isinstance(h, tuple):
        return h
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hsv_shift(c, dh, sm, vm):
    h, s, v = colorsys.rgb_to_hsv(c[0] / 255, c[1] / 255, c[2] / 255)
    h = (h + dh / 360.0) % 1.0
    s = max(0.0, min(1.0, s * sm))
    v = max(0.0, min(1.0, v * vm))
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (round(r * 255), round(g * 255), round(b * 255))


def _toward(c, target_h, amt):
    """Rotate hue toward target_h (degrees) by at most amt degrees."""
    h, s, v = colorsys.rgb_to_hsv(c[0] / 255, c[1] / 255, c[2] / 255)
    hd = h * 360
    diff = ((target_h - hd + 180) % 360) - 180
    step = max(-amt, min(amt, diff))
    return _hsv_shift(c, step, 1, 1)


class Ramp:
    """hi / base / sh1 / sh2 / line.  Shadows drift cool, highlights warm."""

    def __init__(self, base, hi=None, sh1=None, sh2=None, line=None):
        b = rgb(base)
        self.base = b
        self.hi = rgb(hi) if hi else _hsv_shift(_toward(b, 55, 10), 0, 0.78, 1.22)
        self.sh1 = rgb(sh1) if sh1 else _hsv_shift(_toward(b, 265, 10), 0, 1.12, 0.74)
        self.sh2 = rgb(sh2) if sh2 else _hsv_shift(_toward(b, 265, 18), 0, 1.18, 0.52)
        self.line = rgb(line) if line else _hsv_shift(_toward(b, 265, 24), 0, 1.2, 0.26)

    def tones(self, dark=0):
        t = [self.hi, self.base, self.sh1, self.sh2, self.sh2]
        return t[dark:dark + 4]

    def darker(self):
        return Ramp(self.sh1, hi=self.base, sh1=self.sh2,
                    sh2=_hsv_shift(self.sh2, 0, 1.0, 0.8), line=self.line)


INK = (22, 14, 30)  # outer contour - never pure black on a SNES sprite


# ---------------------------------------------------------------- masks
def m_and(a, b):
    return ImageChops.darker(a, b)


def m_or(a, b):
    return ImageChops.lighter(a, b)


def m_not(a):
    return ImageChops.invert(a)


def m_sub(a, b):
    return ImageChops.darker(a, ImageChops.invert(b))


def at(m, dx, dy):
    """Mask whose pixel (x,y) is m[x+dx, y+dy] (False outside)."""
    out = Image.new("L", m.size, 0)
    out.paste(m, (-dx, -dy))
    return out


def dilate(m, diag=False):
    out = m
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        out = m_or(out, at(m, dx, dy))
    if diag:
        for dx, dy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            out = m_or(out, at(m, dx, dy))
    return out


def erode(m):
    out = m
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        out = m_and(out, at(m, dx, dy))
    return out


def empty(size):
    return Image.new("L", size, 0)


class Shape:
    """Accumulates primitives at SSx then resolves to a crisp 1x mask."""

    def __init__(self, size):
        self.size = size
        self.im = Image.new("L", (size[0] * SS, size[1] * SS), 0)
        self.d = ImageDraw.Draw(self.im)

    def circle(self, c, r, fill=255):
        if r <= 0:
            return self
        self.d.ellipse([(c[0] - r) * SS, (c[1] - r) * SS,
                        (c[0] + r) * SS, (c[1] + r) * SS], fill=fill)
        return self

    def ellipse(self, c, rx, ry, ang=0.0, fill=255):
        pts = []
        ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        for i in range(40):
            t = 2 * math.pi * i / 40
            x, y = rx * math.cos(t), ry * math.sin(t)
            pts.append((c[0] + x * ca - y * sa, c[1] + x * sa + y * ca))
        return self.poly(pts, fill)

    def poly(self, pts, fill=255):
        if len(pts) >= 3:
            self.d.polygon([(x * SS, y * SS) for x, y in pts], fill=fill)
        return self

    def capsule(self, p0, p1, r0, r1=None, fill=255):
        r1 = r0 if r1 is None else r1
        self.circle(p0, r0, fill)
        self.circle(p1, r1, fill)
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        ln = math.hypot(dx, dy)
        if ln > 1e-6:
            nx, ny = -dy / ln, dx / ln
            self.poly([(p0[0] + nx * r0, p0[1] + ny * r0), (p1[0] + nx * r1, p1[1] + ny * r1),
                       (p1[0] - nx * r1, p1[1] - ny * r1), (p0[0] - nx * r0, p0[1] - ny * r0)], fill)
        return self

    def hull(self, circles, fill=255):
        """Convex hull of a set of (centre, radius) circles."""
        pts = []
        for c, r in circles:
            for i in range(20):
                t = 2 * math.pi * i / 20
                pts.append((c[0] + r * math.cos(t), c[1] + r * math.sin(t)))
        return self.poly(convex_hull(pts), fill)

    def cut(self):
        """Following primitives erase instead of add (use via fill=0)."""
        return self

    def mask(self):
        return self.im.resize(self.size, Image.BOX).point(lambda v: 255 if v >= 128 else 0)


def convex_hull(points):
    pts = sorted(set((round(x, 3), round(y, 3)) for x, y in points))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def band_masks(m, hi=1, s1=2, s2=1):
    """Split a silhouette into (hi, sh1, sh2) masks.  Light: upper-left."""
    z = empty(m.size)
    mhi = m_and(m, m_not(m_and(at(m, 0, -hi), at(m, -hi, 0)))) if hi else z
    far = s1 + s2
    ms1 = m_and(m, m_not(m_and(m_and(at(m, 0, far), at(m, far, 0)), at(m, far - 1, far - 1)))) if s1 else z
    ms2 = m_and(m, m_not(m_and(at(m, 0, s2), at(m, s2, 0)))) if s2 else z
    return mhi, ms1, ms2


# ---------------------------------------------------------------- layers
class Group:
    """One outlined, shaded sprite part (may mix several materials)."""

    def __init__(self, z, hi=1, s1=2, s2=1, dark=0, line=None, outline=True):
        self.z, self.hi, self.s1, self.s2, self.dark = z, hi, s1, s2, dark
        self.line, self.outline = line, outline
        self.subs = []    # (mask, Ramp)
        self.flat = []    # (mask, colour) painted after shading, clipped to group
        self.free = []    # (mask, colour) painted after shading, unclipped

    def add(self, mask, ramp):
        self.subs.append((mask, ramp))
        return self

    def detail(self, mask, colour, clip=True):
        (self.flat if clip else self.free).append((mask, rgb(colour)))
        return self

    def union(self):
        gm = None
        for m, _ in self.subs:
            gm = m if gm is None else m_or(gm, m)
        return gm

    def paint(self, canvas):
        gm = self.union()
        if gm is None:
            return
        if self.outline:
            line = self.line or self.subs[0][1].line
            canvas.paste(line + (255,), mask=m_sub(dilate(gm), gm))
        mhi, ms1, ms2 = band_masks(gm, self.hi, self.s1, self.s2)
        for m, ramp in self.subs:
            t = ramp.tones(self.dark)
            canvas.paste(t[1] + (255,), mask=m)
            canvas.paste(t[0] + (255,), mask=m_and(m, mhi))
            canvas.paste(t[2] + (255,), mask=m_and(m, ms1))
            canvas.paste(t[3] + (255,), mask=m_and(m, ms2))
        for m, c in self.flat:
            canvas.paste(c + (255,), mask=m_and(m, gm))
        for m, c in self.free:
            canvas.paste(c + (255,), mask=m)


class Bitmap:
    """A hand-pixelled image stamped at a z-depth (heads, props)."""

    def __init__(self, z, img, pos):
        self.z, self.img, self.pos = z, img, (int(round(pos[0])), int(round(pos[1])))

    def paint(self, canvas):
        canvas.alpha_composite(self.img, self.pos) if _inside(canvas, self.img, self.pos) \
            else _safe_composite(canvas, self.img, self.pos)


def _inside(canvas, img, pos):
    return pos[0] >= 0 and pos[1] >= 0 and pos[0] + img.width <= canvas.width \
        and pos[1] + img.height <= canvas.height


def _safe_composite(canvas, img, pos):
    tmp = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    tmp.paste(img, pos)
    canvas.alpha_composite(tmp)


def ascii_bitmap(rows, palette):
    """rows: list[str]; palette: char -> colour ('.' / ' ' transparent)."""
    h, w = len(rows), max(len(r) for r in rows)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = im.load()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in ". ":
                continue
            px[x, y] = rgb(palette[ch]) + (255,)
    return im


def contour(canvas, colour=INK):
    """Recolour every opaque pixel that touches transparency."""
    a = canvas.getchannel("A").point(lambda v: 255 if v else 0)
    canvas.paste(colour + (255,), mask=m_sub(a, erode(a)))
    return canvas


def render(size, layers, ink=INK):
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    for layer in sorted(layers, key=lambda g: g.z):
        layer.paint(canvas)
    return contour(canvas, ink)


def line_mask(size, pts, width=1):
    """Crisp (non-supersampled) polyline."""
    im = Image.new("L", size, 0)
    ImageDraw.Draw(im).line([(int(math.floor(x)), int(math.floor(y))) for x, y in pts], fill=255, width=width)
    return im


def dot_mask(size, pts):
    im = Image.new("L", size, 0)
    px = im.load()
    for x, y in pts:
        xi, yi = int(math.floor(x)), int(math.floor(y))
        if 0 <= xi < size[0] and 0 <= yi < size[1]:
            px[xi, yi] = 255
    return im
