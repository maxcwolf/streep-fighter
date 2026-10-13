"""5x7 arcade pixel font (bold variant = glyph OR'd with itself shifted 1px)."""
from PIL import Image

G = {
    "A": "01110 10001 10001 11111 10001 10001 10001", "B": "11110 10001 10001 11110 10001 10001 11110",
    "C": "01110 10001 10000 10000 10000 10001 01110", "D": "11110 10001 10001 10001 10001 10001 11110",
    "E": "11111 10000 10000 11110 10000 10000 11111", "F": "11111 10000 10000 11110 10000 10000 10000",
    "G": "01111 10000 10000 10011 10001 10001 01110", "H": "10001 10001 10001 11111 10001 10001 10001",
    "I": "01110 00100 00100 00100 00100 00100 01110", "J": "00111 00010 00010 00010 00010 10010 01100",
    "K": "10001 10010 10100 11000 10100 10010 10001", "L": "10000 10000 10000 10000 10000 10000 11111",
    "M": "10001 11011 10101 10101 10001 10001 10001", "N": "10001 11001 10101 10011 10001 10001 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110", "P": "11110 10001 10001 11110 10000 10000 10000",
    "Q": "01110 10001 10001 10001 10101 10010 01101", "R": "11110 10001 10001 11110 10100 10010 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110", "T": "11111 00100 00100 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110", "V": "10001 10001 10001 10001 10001 01010 00100",
    "W": "10001 10001 10001 10101 10101 11011 10001", "X": "10001 10001 01010 00100 01010 10001 10001",
    "Y": "10001 10001 01010 00100 00100 00100 00100", "Z": "11111 00001 00010 00100 01000 10000 11111",
    "0": "01110 10001 10011 10101 11001 10001 01110", "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00010 00100 01000 11111", "3": "11110 00001 00001 01110 00001 00001 11110",
    "4": "00010 00110 01010 10010 11111 00010 00010", "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110", "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110", "9": "01110 10001 10001 01111 00001 00010 01100",
    " ": "00000 00000 00000 00000 00000 00000 00000", ".": "00000 00000 00000 00000 00000 01000 01000",
    ",": "00000 00000 00000 00000 01100 00100 01000", "!": "00100 00100 00100 00100 00100 00000 00100",
    "?": "01110 10001 00001 00010 00100 00000 00100", "-": "00000 00000 00000 11111 00000 00000 00000",
    "'": "00100 00100 01000 00000 00000 00000 00000", ":": "00000 01100 01100 00000 01100 01100 00000",
    "/": "00001 00001 00010 00100 01000 10000 10000", "(": "00010 00100 01000 01000 01000 00100 00010",
    ")": "01000 00100 00010 00010 00010 00100 01000", "+": "00000 00100 00100 11111 00100 00100 00000",
    "|": "00100 00100 00100 00100 00100 00100 00100", "[": "01110 01000 01000 01000 01000 01000 01110",
    "]": "01110 00010 00010 00010 00010 00010 01110", "<": "00010 00100 01000 10000 01000 00100 00010",
    ">": "01000 00100 00010 00001 00010 00100 01000", "=": "00000 00000 11111 00000 11111 00000 00000",
    "&": "01100 10010 10100 01000 10101 10010 01101", "*": "00000 10101 01110 11111 01110 10101 00000",
    "\"": "01010 01010 10100 00000 00000 00000 00000", "%": "11001 11010 00010 00100 01000 01011 10011",
    "#": "01010 01010 11111 01010 11111 01010 01010", "_": "00000 00000 00000 00000 00000 00000 11111",
}


# 3x5 micro font for signage too small for the 5x7 face
T = {
    "A": "010 101 111 101 101", "B": "110 101 110 101 110", "C": "011 100 100 100 011",
    "D": "110 101 101 101 110", "E": "111 100 110 100 111", "F": "111 100 110 100 100",
    "G": "011 100 101 101 011", "H": "101 101 111 101 101", "I": "111 010 010 010 111",
    "J": "001 001 001 101 010", "K": "101 101 110 101 101", "L": "100 100 100 100 111",
    "M": "101 111 111 101 101", "N": "110 101 101 101 101", "O": "010 101 101 101 010",
    "P": "110 101 110 100 100", "Q": "010 101 101 110 011", "R": "110 101 110 101 101",
    "S": "011 100 010 001 110", "T": "111 010 010 010 010", "U": "101 101 101 101 111",
    "V": "101 101 101 101 010", "W": "101 101 111 111 101", "X": "101 101 010 101 101",
    "Y": "101 101 010 010 010", "Z": "111 001 010 100 111",
    "0": "111 101 101 101 111", "1": "010 110 010 010 111", "2": "110 001 010 100 111",
    "3": "110 001 010 001 110", "4": "101 101 111 001 001", "5": "111 100 110 001 110",
    "6": "011 100 111 101 111", "7": "111 001 010 010 010", "8": "111 101 111 101 111",
    "9": "111 101 111 001 110", " ": "000 000 000 000 000", ".": "000 000 000 000 010",
    "-": "000 000 111 000 000", "!": "010 010 010 000 010", "'": "010 010 000 000 000",
    "?": "110 001 010 000 010", ":": "000 010 000 010 000", "/": "001 001 010 100 100",
    "+": "000 010 111 010 000", ",": "000 000 000 010 100", "&": "010 101 010 101 011",
    "<": "001 010 100 010 001", ">": "100 010 001 010 100",
}


def glyph(ch, bold=False, tiny=False):
    if tiny:
        rows = T.get(ch.upper(), T["?"]).split()
        im = Image.new("L", (3, 5), 0)
        p = im.load()
        for y, r in enumerate(rows):
            for x, b in enumerate(r):
                if b == "1":
                    p[x, y] = 255
        return im
    rows = G.get(ch.upper(), G["?"]).split()
    w = 6 if bold else 5
    im = Image.new("L", (w, 7), 0)
    p = im.load()
    for y, r in enumerate(rows):
        for x, b in enumerate(r):
            if b == "1":
                p[x, y] = 255
                if bold:
                    p[x + 1, y] = 255
    return im


def measure(text, bold=False, scale=1, spacing=1, tiny=False):
    w = 3 if tiny else (6 if bold else 5)
    return (len(text) * (w + spacing) - spacing) * scale, (5 if tiny else 7) * scale


def text_mask(text, bold=False, scale=1, spacing=1, tiny=False):
    w, h = measure(text, bold, 1, spacing, tiny)
    im = Image.new("L", (max(w, 1), h), 0)
    x = 0
    for ch in text:
        g = glyph(ch, bold, tiny)
        im.paste(g, (x, 0))
        x += g.width + spacing
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    return im


def draw(img, xy, text, colour, shadow=None, outline=None, bold=False, scale=1, spacing=1, align="left",
         gradient=None, tiny=False):
    """Draw text on an RGB(A) image.  gradient = list of colours top->bottom."""
    m = text_mask(text, bold, scale, spacing, tiny)
    x, y = xy
    if align == "center":
        x -= m.width // 2
    elif align == "right":
        x -= m.width
    def stamp(dx, dy, c):
        img.paste(tuple(c) + ((255,) if img.mode == "RGBA" else ()), (x + dx, y + dy), m)
    if outline:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    stamp(dx, dy, outline)
        if shadow:
            for dx in (0, 1, 2):
                stamp(dx, 2, shadow)
    elif shadow:
        stamp(1, 1, shadow)
    if gradient:
        n = len(gradient)
        for i, c in enumerate(gradient):
            y0, y1 = m.height * i // n, m.height * (i + 1) // n
            band = Image.new("L", m.size, 0)
            band.paste(m.crop((0, y0, m.width, y1)), (0, y0))
            img.paste(tuple(c) + ((255,) if img.mode == "RGBA" else ()), (x, y), band)
    else:
        stamp(0, 0, colour)
    return m.width


# ------------------------------------------------------------- BMFont export
def export_bmfont(path_base, face, bold=False, scale=1, fill=(255, 255, 255), outline=None, shadow=None,
                  gradient=None, chars=None, tiny=False):
    """Bake a Godot-importable bitmap font: <path_base>.png + <path_base>.fnt.
    Lower-case codes map onto the upper-case glyphs."""
    import os
    table = T if tiny else G
    chars = chars or sorted(table)
    pad = 1 if outline else 0
    extra = 1 if shadow else 0
    gw, gh = measure("A", bold, scale, tiny=tiny)
    cw, ch = gw + pad * 2 + extra, gh + pad * 2 + extra
    cols = 16
    rows = (len(chars) + cols - 1) // cols
    img = Image.new("RGBA", (cols * cw, rows * ch), (0, 0, 0, 0))
    lines = []
    adv = gw + pad + scale
    for i, c in enumerate(chars):
        x, y = (i % cols) * cw, (i // cols) * ch
        draw(img, (x + pad, y + pad), c, fill, bold=bold, scale=scale, outline=outline,
             shadow=shadow, gradient=gradient, tiny=tiny)
        codes = {ord(c)}
        if c.isalpha():
            codes.add(ord(c.lower()))
        for code in sorted(codes):
            lines.append("char id=%d x=%d y=%d width=%d height=%d xoffset=%d yoffset=0 xadvance=%d page=0 chnl=15"
                         % (code, x, y, cw, ch, -pad, adv if c != " " else gw))
    img.save(path_base + ".png")
    name = os.path.basename(path_base)
    with open(path_base + ".fnt", "w") as f:
        f.write('info face="%s" size=%d bold=0 italic=0 charset="" unicode=1 stretchH=100 smooth=0 aa=1 '
                'padding=0,0,0,0 spacing=0,0\n' % (face, ch))
        f.write("common lineHeight=%d base=%d scaleW=%d scaleH=%d pages=1 packed=0\n"
                % (ch + scale, gh + pad, img.width, img.height))
        f.write('page id=0 file="%s.png"\n' % name)
        f.write("chars count=%d\n" % len(lines))
        f.write("\n".join(lines) + "\n")
