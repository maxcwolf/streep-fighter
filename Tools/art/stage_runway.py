"""RUNWAY MAGAZINE - New York City.  Miranda Priestly's stage."""
from bg import Art, skyline
from stages import FAR_W, STAGE_H, STAGE_W, WALL_Y, floor_checker, shade


def build():
    # ---- FAR: dusk Manhattan skyline (seen through the glass, scrolls slower)
    f = Art(FAR_W, STAGE_H)
    f.vgrad(0, 0, FAR_W, 146, ["#24246c", "#4c3090", "#a04090", "#e8705c", "#f8c070", "#fce8a0"])
    skyline(f, 0, FAR_W, 146, "#8c5ca4", seed=3, hmin=30, hmax=70, wmin=10, wmax=20)
    skyline(f, 0, FAR_W, 146, "#4c3484", lit="#f8d868", seed=23, hmin=18, hmax=52)
    for (x0, y0, x1) in ((96, 66, 110), (99, 48, 107), (101, 36, 105)):   # Empire State
        f.rect(x0, y0, x1, 146, "#342460")
    f.rect(103, 22, 104, 36, "#342460")
    for wy in range(52, 144, 4):
        for wx in (98, 101, 104, 107):
            if (wx + wy) % 3:
                f.dot(wx, wy, "#f8d868")
    skyline(f, 0, FAR_W, 146, "#281c54", lit="#f8e890", seed=43, hmin=8, hmax=30, lit_chance=0.45)
    f.rect(0, 146, FAR_W, STAGE_H, "#281c54")

    # ---- MAIN: the office (glass bays are transparent holes)
    a = Art(STAGE_W, STAGE_H, mode="RGBA")
    a.rect(0, 0, STAGE_W, STAGE_H, "#e9e5f5")
    for bx0, bx1 in ((10, 142), (370, 502)):
        a.clear(bx0, 12, bx1, 142)
        # mullions
        for mx in (bx0 + 44, bx0 + 88):
            a.rect(mx, 12, mx + 2, 142, "#3c3858")
        a.rect(bx0, 60, bx1, 62, "#3c3858")
        a.frame(bx0 - 2, 10, bx1 + 2, 144, "#3c3858", 2)
        # glass glare
        for gx in (bx0 + 8, bx0 + 98):
            for i in range(26):
                a.dot(gx + i // 2, 20 + i, "#fcf4dc")
                a.dot(gx + 4 + i // 2, 20 + i, "#fcf4dc")
    # ---- ceiling soffit + downlights
    a.rect(0, 0, STAGE_W, 8, "#b4b0d0")
    a.rect(0, 8, STAGE_W, 10, "#7c78a4")
    for lx in range(24, STAGE_W, 58):
        a.rect(lx, 3, lx + 10, 6, "#fcf8d8")
        a.rect(lx + 1, 6, lx + 9, 7, "#f8d868")

    # ---- centre wall: logo + framed covers
    a.vgrad(152, 10, 360, 150, ["#f4f0fc", "#e9e5f5", "#d0cce8"])
    a.rect(148, 10, 152, 150, "#b4b0d0")
    a.rect(360, 10, 364, 150, "#b4b0d0")
    a.text((256, 44), "RUNWAY", "#d8243c", bold=True, scale=3, spacing=3, align="center", shadow="#8c1830")
    covers = [("#f04868", "#fcd8b8", "#281c3c"), ("#28a8c8", "#fcd8b8", "#f8d868"),
              ("#f8c838", "#c88868", "#d8243c"), ("#7c4cc0", "#fcd8b8", "#fcfcfc")]
    for i, (bgc, skin, hair) in enumerate(covers):
        x = 170 + i * 46
        a.rect(x - 2, 72, x + 32, 118, "#281c3c")
        a.rect(x - 1, 73, x + 31, 117, "#fcfcfc")
        a.rect(x + 1, 75, x + 29, 115, bgc)
        a.text((x + 4, 77), "RUNWAY", "#fcfcfc", tiny=True)   # masthead (3x5 face: 23px wide)
        a.ellipse(x + 9, 86, x + 21, 100, skin)         # cover model
        a.rect(x + 8, 84, x + 22, 90, hair)
        a.rect(x + 7, 88, x + 10, 102, hair)
        a.rect(x + 6, 102, x + 24, 115, hair if i % 2 else "#281c3c")
        a.rect(x + 11, 92, x + 13, 93, "#281c3c")
        a.rect(x + 16, 92, x + 18, 93, "#281c3c")
        a.rect(x + 13, 97, x + 17, 98, "#c02848")
    # sill under the glass
    for x0, x1 in ((0, 148), (364, STAGE_W)):
        a.rect(x0, 142, x1, 150, "#c8c4e0")
        a.rect(x0, 142, x1, 143, "#fcfcfc")
    for px_ in (0, 142, 364, 502):
        a.vgrad(px_, 10, px_ + 10 if px_ in (0, 502) else px_ + 6, 150, ["#f4f0fc", "#c8c4e0"])

    # ---- clothing rack (left)
    a.rect(20, 78, 22, 150, "#585478")
    a.rect(124, 78, 126, 150, "#585478")
    a.rect(18, 76, 128, 79, "#9c98c0")
    a.rect(18, 76, 128, 77, "#fcfcfc")
    garments = ["#d8243c", "#28a8c8", "#f8c838", "#1c7c50", "#f08cb4", "#fcfcfc", "#7c4cc0", "#281c3c", "#e87830"]
    for i, gc in enumerate(garments):
        x = 26 + i * 11
        ln = 44 + (i * 7) % 18
        a.rect(x + 3, 79, x + 4, 83, "#585478")
        a.poly([(x + 3, 82), (x + 8, 86), (x + 9, 86 + ln), (x - 1, 86 + ln), (x - 1, 86)], gc)
        a.rect(x + 6, 87, x + 8, 86 + ln, shade(gc))
        a.rect(x - 1, 86 + ln, x + 9, 87 + ln, "#281c3c")
        a.line([(x - 1, 86), (x - 1, 86 + ln)], "#281c3c")

    # ---- Miranda's desk (right)
    a.rect(392, 122, 494, 127, "#fcfcfc")
    a.rect(392, 127, 494, 129, "#9c98c0")
    a.rect(398, 129, 404, 150, "#c8c4e0")
    a.rect(482, 129, 488, 150, "#c8c4e0")
    a.rect(404, 129, 482, 150, "#dcd8ec")
    a.rect(404, 129, 482, 131, "#9c98c0")
    a.rect(426, 108, 448, 122, "#281c3c")          # laptop
    a.rect(428, 110, 446, 120, "#58c8e8")
    a.rect(422, 121, 452, 123, "#585478")
    a.rect(468, 112, 476, 122, "#28a8c8")          # vase + orchids
    for ox, oy in ((466, 100), (472, 94), (478, 102), (470, 106), (476, 108)):
        a.rect(ox, oy, ox + 3, oy + 3, "#fcfcfc")
        a.dot(ox + 1, oy + 1, "#f08cb4")
    a.line([(472, 112), (472, 98)], "#1c7c50")
    a.rect(400, 116, 418, 122, "#d8243c")          # "the Book"
    a.rect(400, 116, 418, 117, "#f8889c")

    # ---- floor: polished checker, darker toward the wall
    floor_checker(a, WALL_Y, STAGE_H, "#d4d0ec", "#aca8d0")
    a.dither(0, WALL_Y, STAGE_W, WALL_Y + 10, "#7c78a4", 0.5)
    a.dither(0, WALL_Y + 10, STAGE_W, WALL_Y + 22, "#7c78a4", 0.25)
    for x0, x1 in ((10, 142), (370, 502)):          # window light pooling on the tiles
        a.dither(x0 + 6, WALL_Y + 2, x1 - 6, WALL_Y + 18, "#fce8a0", 0.3)
    a.rect(0, WALL_Y, STAGE_W, WALL_Y + 2, "#3c3858")
    return f.im, a.im
