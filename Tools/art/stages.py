"""Stage conventions + shared helpers.

Every stage lives in its own module  stage_<key>.py  exposing

    build() -> (far, main)

  far   RGB  image  FAR_W  x STAGE_H   distant layer, scrolls at half speed
  main  RGBA image  STAGE_W x STAGE_H  walls / props / floor; transparent
                                       wherever the far layer should show

The screen is 384x216 and the camera pans across the 512px main layer.
Fighters are ~96px tall and stand with their feet on y = FLOOR_Y.
"""
import importlib

from px import rgb

SCREEN_W = 384
STAGE_W, STAGE_H = 512, 216
FAR_W = SCREEN_W + (STAGE_W - SCREEN_W) // 2   # 448: half-speed parallax
WALL_Y = 150      # typical line where the back wall meets the floor
FLOOR_Y = 200     # fighters' feet

KEYS = ["runway", "kitchen", "parliament", "forest", "villa", "church"]


def floor_checker(a, y0, y1, c1, c2, vx=256, vy=110, depth=420.0, cols=7.0):
    """Perspective checkerboard floor converging on (vx, vy)."""
    for y in range(y0, y1):
        d = y - vy
        row = int(depth / d)
        for x in range(a.w):
            col = int((x - vx) / d * cols + 1000)
            a.p[x, y] = a.c(c1 if (row + col) & 1 else c2)


def floor_planks(a, y0, y1, cols_, seam, vx=256, vy=110, cols=5.0, depth=420.0, stagger=True):
    """Perspective floorboards running toward the camera."""
    for y in range(y0, y1):
        d = y - vy
        row = int(depth / d)
        for x in range(a.w):
            u = (x - vx) / d * cols + 1000
            board = int(u)
            a.p[x, y] = a.c(seam if (u - board) < 0.06 * (1 + 20.0 / d) else cols_[(board * 7 + (row if stagger else 0)) % len(cols_)])


def shade(c, k=0.7):
    r, g, b = rgb(c)
    return (int(r * k), int(g * k * 0.95), min(255, int(b * k * 1.12)))


def build(key):
    return importlib.import_module("stage_" + key).build()
