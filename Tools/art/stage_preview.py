"""Preview a stage with two fighters and the HUD safe-area, zoomed 3x.

    python3 Tools/art/stage_preview.py <key> <out.png> [camera_x 0..128]

Also writes <out>_full.png (the whole 512px main layer over the far layer).
"""
import sys

from PIL import Image

import os

import stages

CELL, ORG = (144, 128), (56, 121)      # sprite cell + feet origin (see rig.py)
REF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ref")


def composite(far, main, cam):
    out = far.crop((cam // 2, 0, cam // 2 + stages.SCREEN_W, stages.STAGE_H)).convert("RGBA")
    out.alpha_composite(main.crop((cam, 0, cam + stages.SCREEN_W, stages.STAGE_H)))
    return out


if __name__ == "__main__":
    key, out = sys.argv[1], sys.argv[2]
    cam = int(sys.argv[3]) if len(sys.argv) > 3 else 64
    far, main = stages.build(key)
    assert far.size == (stages.FAR_W, stages.STAGE_H) and far.mode == "RGB", far.size
    assert main.size == (stages.STAGE_W, stages.STAGE_H) and main.mode == "RGBA", main.size
    scene = composite(far, main, cam)
    # pre-baked stand-in sprites so this tool never depends on the fighter code
    for fn, x, flip in (("preview_p1.png", 150, False), ("preview_p2.png", 236, True)):
        img = Image.open(os.path.join(REF, fn)).convert("RGBA")
        ox = ORG[0]
        if flip:
            img, ox = img.transpose(Image.FLIP_LEFT_RIGHT), CELL[0] - ORG[0]
        scene.alpha_composite(img, (x - ox, stages.FLOOR_Y - ORG[1]))
    scene.resize((scene.width * 3, scene.height * 3), Image.NEAREST).save(out)
    full = Image.new("RGBA", main.size)
    full.paste(far.resize((stages.STAGE_W, stages.STAGE_H), Image.NEAREST))
    full.alpha_composite(main)
    full.resize((full.width * 2, full.height * 2), Image.NEAREST).save(out.replace(".png", "_full.png"))
    print("colours in main:", len(main.convert("RGB").getcolors(100000) or []))
