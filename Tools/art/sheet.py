"""Fighter sprite sheets.

    python3 Tools/art/sheet.py contact <fighter> <out.png> [zoom] [frame-prefix]
"""
import sys

from PIL import Image, ImageDraw

import anims
import font
import rig
from fighters import FIGHTERS


def render_frame(key, name):
    spec = FIGHTERS[key]
    p = anims.pose(name, spec.get("poses"), spec.get("modify"))
    fr = rig.Frame()
    spec["draw"](fr, rig.solve(spec["body"], p))
    return fr.render()


def sheet(key):
    cw, ch = rig.CELL
    rows = (len(anims.FRAMES) + anims.COLS - 1) // anims.COLS
    im = Image.new("RGBA", (cw * anims.COLS, ch * rows), (0, 0, 0, 0))
    for i, name in enumerate(anims.FRAMES):
        im.alpha_composite(render_frame(key, name), ((i % anims.COLS) * cw, (i // anims.COLS) * ch))
    return im


def contact(key, out, zoom=3, prefix=""):
    names = [n for n in anims.FRAMES if n.startswith(prefix)]
    cw, ch = rig.CELL
    cols = min(len(names), 6)
    rows = (len(names) + cols - 1) // cols
    im = Image.new("RGBA", (cw * cols, ch * rows), (96, 104, 128, 255))
    d = ImageDraw.Draw(im)
    for i, name in enumerate(names):
        x, y = (i % cols) * cw, (i // cols) * ch
        d.line([(x, y + rig.ORG[1]), (x + cw - 1, y + rig.ORG[1])], fill=(70, 76, 96, 255))
        d.line([(x + rig.ORG[0], y + rig.ORG[1] - 2), (x + rig.ORG[0], y + rig.ORG[1] + 2)], fill=(255, 255, 0, 255))
        im.alpha_composite(render_frame(key, name), (x, y))
        font.draw(im, (x + 2, y + 2), name, (255, 255, 255), shadow=(0, 0, 0))
    im.resize((im.width * zoom, im.height * zoom), Image.NEAREST).save(out)


if __name__ == "__main__":
    if sys.argv[1] == "contact":
        contact(sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 3,
                sys.argv[5] if len(sys.argv) > 5 else "")
