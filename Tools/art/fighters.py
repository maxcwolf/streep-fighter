"""Costumes: each fighter turns solved joints into shaded sprite layers.

Depth order (z): far arm 10 < far leg 20 < near leg 30 < back hair 35 <
skirt 38 < torso 40 < collar 50 < head 60 < near arm 70 < held prop 74.
Pose flags move an arm: front_f brings the far arm forward (66), back_n tucks
the near arm behind the head (54) for overhead holds.
"""
from PIL import Image

import px
from px import Ramp
from rig import add, lerp, mul, norm, perp, rot, sub

SKIN = Ramp("#f0b68c", hi="#ffd9b4", sh1="#cc8664", sh2="#9c5a4e", line="#57282e")
GOLD = "#f6c637"

# build.py flips this to bake the second-player colours used in mirror matches
ALT = False


def _pick(main, alt):
    return alt if ALT else main


def _hand_centre(J, side, out=2.8):
    return add(J["ha_" + side], mul(norm(sub(J["ha_" + side], J["el_" + side])), out * J["s"]))


def _hand_dir(J, side):
    return norm(sub(J["ha_" + side], J["el_" + side]))


# ------------------------------------------------------------ shared pieces
def _limbs(fr, J, leg, shoe, sleeve, hand=SKIN, cuff=None, thick=1.0, fore=None, shin=None, claws=False):
    """Both arms + both legs with the standard depth order."""
    s = J["s"] * thick
    for side, z_arm, z_leg, dark in (("f", 10, 20, 1), ("n", 70, 30, 0)):
        if J["pose"]["front_f"] and side == "f":
            z_arm = 66
        if J["pose"]["back_n"] and side == "n":
            z_arm = 54                      # raised beside the head: the head overlaps it
        hip, kn, an = J["hip_" + side], J["kn_" + side], J["an_" + side]
        sh, el, ha = J["sh_" + side], J["el_" + side], J["ha_" + side]
        fr.limb(z_leg, hip, kn, an, (5.0 * s, 4.0 * s, 2.6 * s), leg, shin, dark=dark)
        fr.foot(z_leg + 1, J, side, shoe, dark=dark)
        fr.limb(z_arm, sh, el, ha, (4.2 * s, 3.6 * s, 3.1 * s), sleeve, fore, dark=dark)
        d = _hand_dir(J, side)
        if J["pose"]["hand_" + side] == "open" or claws:
            g = fr.group(z_arm + 2, dark=dark, s1=1, s2=0)
            sh_ = fr.shape().capsule(fr.P(add(ha, mul(d, 1.5))), fr.P(add(ha, mul(d, 6.0))), 2.7 * s, 2.0 * s)
            if claws:
                for a in (-28, 0, 28):
                    sh_.capsule(fr.P(add(ha, mul(d, 4.0))), fr.P(add(ha, mul(rot(d, a), 9.0))), 1.0, 0.6)
            g.add(sh_.mask(), hand)
        else:
            fr.disc(z_arm + 2, _hand_centre(J, side), 3.4 * s, hand, dark=dark, s1=1, s2=0)
        if cuff:
            fr.disc(z_arm + 3, lerp(el, ha, 0.84), 3.9 * s, cuff, dark=dark, s1=1, s2=0)


def _skirt_shape(fr, J, sh, length=0.0, r_hip=5.8, r_knee=5.4, r_hem=5.0):
    """Two panels (one per thigh) so kicks and crouches don't balloon.
    length: 0 = hem at the knee, 1 = hem at the ankle."""
    s, P = J["s"], J["P"]
    for k in "fn":
        pts = [(fr.P(add(P, (-4 * s, 1))), r_hip * s), (fr.P(add(P, (4 * s, 1))), r_hip * s),
               (fr.P(J["kn_" + k]), r_knee * s)]
        if length > 0:
            pts.append((fr.P(lerp(J["kn_" + k], J["an_" + k], length)), r_hem * s))
        sh.hull(pts)
    # standing: the cloth hangs as one piece between the legs
    if all(J["kn_" + k][1] < P[1] - 12 * s for k in "fn") and not J["pose"]["rot"]:
        sh.hull([(fr.P(add(P, (-4 * s, 1))), r_hip * s), (fr.P(add(P, (4 * s, 1))), r_hip * s)] +
                [(fr.P(lerp(J["kn_" + k], J["an_" + k], length)), (r_hem if length > 0 else r_knee) * s)
                 for k in "fn"])
    return sh


def _torso_shape(fr, J, sh, chest=7.6, waist=5.4, hips=6.4, shoulder=4.0):
    s = J["s"]
    if hips:
        sh.hull([(fr.P(J["P"]), hips * s), (fr.P(J["W"]), waist * s)])
    sh.hull([(fr.P(J["W"]), waist * s), (fr.P(J["C"]), chest * s),
             (fr.P(J["sh_f"]), shoulder * s), (fr.P(J["sh_n"]), shoulder * s)])
    return sh


def _skirt(fr, J, z, ramp, **kw):
    g = fr.group(z, s1=2, s2=1)
    g.add(_skirt_shape(fr, J, fr.shape(), **kw).mask(), ramp)
    return g


def _torso(fr, J, z, ramp, **kw):
    g = fr.group(z, hi=2, s1=2, s2=1)
    g.add(_torso_shape(fr, J, fr.shape(), **kw).mask(), ramp)
    return g


def _dress(fr, J, z, ramp, length=0.3, torso=None, skirt=None):
    """Torso + skirt as ONE outlined garment (coats, robes, habits)."""
    g = fr.group(z, hi=2, s1=2, s2=1)
    sh = _skirt_shape(fr, J, fr.shape(), length=length, **(skirt or {}))
    g.add(_torso_shape(fr, J, sh, **(torso or {})).mask(), ramp)
    return g


def _back_hair(fr, J, ramp, length=1.0, r=(7.0, 6.0, 4.5), z=35):
    """Long hair down the back; trails opposite to the pose's `sway`."""
    s, sway = J["s"], J["pose"]["sway"]
    H, N, C = J["H"], J["N"], J["C"]
    back = mul(J["fw"], -1)
    p0 = add(H, mul(back, 4 * s))
    p1 = add(N, add(mul(back, (6 + 3 * sway) * s), mul(J["up"], -3 * s * length)))
    p2 = add(lerp(N, C, length), add(mul(back, (8 + 7 * sway) * s), mul(J["up"], -5 * s * length)))
    g = fr.group(z, hi=1, s1=2, s2=1)
    sh = fr.shape().capsule(fr.P(p0), fr.P(p1), r[0] * s, r[1] * s).capsule(fr.P(p1), fr.P(p2), r[1] * s, r[2] * s)
    g.add(sh.mask(), ramp)
    return g


def _express(rows, face):
    """Heads share one layout: eyes are 'wwe', the mouth is 'mmmm'."""
    if face == "neutral":
        return rows
    out = []
    for r in rows:
        if face == "hurt":
            r = r.replace("wwe", "bbb").replace("twe", "tbb").replace("geg", "gbg")
        out.append(r.replace("mmmm", "mKKm"))
    return out


def _head(fr, J, rows, pal, ofs=(1, 0), z=60):
    w = max(len(r) for r in rows)
    img = px.ascii_bitmap(_express([r.ljust(w, ".") for r in rows], J["pose"]["face"]), pal)
    ang = J["pose"]["rot"]
    if abs(ang) >= 25:
        img = img.rotate(round(ang / 90.0) * 90 if abs(ang) > 70 else ang, Image.NEAREST, expand=True)
    fr.bitmap(z, img, add(J["H"], ofs))


def _face_pal(skin=SKIN, **extra):
    pal = {"o": "#2a2038", "S": skin.base, "h": skin.hi, "s": skin.sh1, "t": skin.sh2,
           "e": "#281c30", "w": "#ffffff", "m": "#b82c4c", "K": "#4c1424", "b": "#5c4858", "r": "#f0947c"}
    pal.update(extra)
    return pal


# ------------------------------------------------------------------ Miranda
MIRANDA_HEAD = [
    ".......ooooooo......",
    "....oooWWWWWWWoo....",
    "...oWWWWWWWWGWWWo...",
    "..oWWWWWWWWGGWWWWo..",
    ".oWWWGWWWWGGWWWWWGo.",
    ".oWWGGWWWGGWWhhGGGo.",
    ".oWGGWWWGGhhSSSSGgo.",
    ".oWGgWWGSbbbSSbbbSo.",
    ".oGGgWGSSwweSSwweSo.",
    ".oGggGsSSSSSSSSSSSo.",
    "..oggYsSSSSSSSSsSSSo",
    "..ogdYsSSSSSSSSssSo.",
    "...oddssSSSmmmmSSo..",
    "....oo.osSSSSSSSo...",
    ".......ossSSSSSo....",
    "........oossssoo....",
    "..........oooo......",
]
MIRANDA_PAL = _face_pal(W="#fbfbff", G="#cfd3e4", g="#9aa0be", d="#666c94", Y=GOLD, b="#7c7890")


def miranda(fr, J):
    s = J["s"]
    coat = _pick(Ramp("#4c4270", hi="#8a80b8", sh1="#322a50", sh2="#1e1834", line="#120d1e"),
                 Ramp("#a8283c", hi="#e8647c", sh1="#781c34", sh2="#4c1028", line="#200818"))
    fur = Ramp("#e9e5f0", hi="#ffffff", sh1="#b8b3d0", sh2="#8c86b0", line="#49426a")
    stock = Ramp("#57506a", hi="#8078a0", sh1="#383048", sh2="#241e32", line="#120d1e")
    shoe = Ramp("#2b2436", hi="#6a6288", sh1="#1c1626", sh2="#120d1a", line="#0c0812")
    up, fw, W, N = J["up"], J["fw"], J["W"], J["N"]

    _limbs(fr, J, stock, shoe, coat, cuff=fur)
    g = _dress(fr, J, 40, coat, length=0.12)
    g.detail(fr.line([add(W, mul(fw, -8 * s)), add(W, mul(fw, 8 * s))]), "#0e0a18")
    g.detail(fr.dots([add(W, mul(fw, 2 * s)), add(W, mul(fw, 3 * s))]), GOLD)
    g.detail(fr.line([add(N, mul(fw, 3 * s)), add(W, mul(fw, 1 * s))]), coat.sh2)
    fr.blob(50, [(add(J["sh_f"], mul(up, 2.8 * s)), 4.0 * s), (add(J["sh_n"], mul(up, 2.8 * s)), 4.0 * s),
                 (add(N, mul(up, 0.5 * s)), 4.6 * s)], fur, s1=1, s2=1)
    _head(fr, J, MIRANDA_HEAD, MIRANDA_PAL)


MIRANDA_POSES = {
    # "That's all." - glide in, backhand slap, dismissive flick
    "sp0": dict(pelvis=(-3, 42), lean=-4, twist=0.3, hf=(8, -8), hn=(11, 1), hand_n="open"),
    "sp1": dict(pelvis=(4, 38), lean=20, twist=0.7, ff=(18, 4), fn=(-16, 5), fan=-25, hf=(9, -9), hn=(11, -4),
                hand_n="open", face="attack"),
    "sp2": dict(pelvis=(6, 40), lean=12, twist=-0.5, ff=(18, 4), fn=(-14, 4), hf=(-4, -10), hn=(26.5, 3),
                hand_n="open", head=(-6, 0, 0), face="attack"),
    "sp3": dict(pelvis=(2, 43), lean=0, twist=0.2, ff=(12, 4), fn=(-10, 4), hf=(4, -14), hn=(19, -1),
                hand_n="open", head=(8, 0, 0)),
    "win0": dict(pelvis=(0, 46), lean=-2, twist=0.8, ff=(6, 4), fn=(-7, 4), hf=(3, -16), ef=1, hn=(17, -14),
                 hand_n="open", head=(8, 0, 0)),
    "win1": dict(pelvis=(0, 46), lean=-2, twist=0.8, ff=(6, 4), fn=(-7, 4), hf=(3, -16), ef=1, hn=(22, -11),
                 hand_n="open", head=(8, 0, 0)),
}


# -------------------------------------------------------------------- Julia
JULIA_HEAD = [
    ".....oo.ooo.oo......",
    "...ooBBoBBBoBBoo....",
    "..oBBLBBBLBBBLBBo...",
    ".oBLBBBBLBBBBBLBBo..",
    ".oBBBkBBBBkBBBBBLo..",
    "oBLBBBBBBhhhhBBkBBo.",
    "oBBBkBBhhSSSSSSBBBo.",
    "oBkBBBSbbbSSSbbbSBo.",
    ".oBBkSSwweSSSwweSo..",
    ".oBkBsSSSSSSSSSSSo..",
    ".oBBksSSrSSSSSsSSSo.",
    "..oBksSrrSSSSSssSo..",
    "..oo.sSSSmmmmmSSo...",
    ".....osSSSSSSSSo....",
    "......ossSSSSSo.....",
    ".......oossssoo.....",
    ".........oooo.......",
]
JULIA_PAL = _face_pal(B="#8c5030", L="#b87848", k="#5c2c20", b="#5c2c20", m="#d0384c")


def julia(fr, J):
    s = J["s"]
    blouse = _pick(Ramp("#3c8cd8", hi="#84c4fc", sh1="#2860a8", sh2="#1c3c78", line="#101c48"),
                   Ramp("#d8486c", hi="#fc90a8", sh1="#a03058", sh2="#6c1c44", line="#300c24"))
    skirt = _pick(Ramp("#285c94", hi="#4c8cc8", sh1="#1c4070", sh2="#142850", line="#0c1434"),
                  Ramp("#7c2c50", hi="#b05078", sh1="#581c3c", sh2="#38102c", line="#1c0818"))
    apron = Ramp("#f4f0e4", hi="#ffffff", sh1="#c4c0d0", sh2="#9490b4", line="#4c4870")
    hose = Ramp("#e0a880", hi="#f8cca4", sh1="#b47860", sh2="#84504c", line="#44242c")
    shoe = Ramp("#6c3c24", hi="#a86c44", sh1="#4c2418", sh2="#341410", line="#1c0c0c")
    up, fw, W, N, P, C = J["up"], J["fw"], J["W"], J["N"], J["P"], J["C"]

    _limbs(fr, J, hose, shoe, blouse, fore=SKIN, thick=1.02)
    _skirt(fr, J, 38, skirt, r_knee=5.8)
    _torso(fr, J, 40, blouse, chest=8.0, waist=6.0, hips=6.8)
    # apron: bib + skirt panel on the front of the body
    ga = fr.group(44, hi=1, s1=1, s2=1)
    front = [(fr.P(add(C, mul(fw, 2.5 * s))), 4.6 * s), (fr.P(add(W, mul(fw, 2.5 * s))), 4.6 * s),
             (fr.P(add(P, mul(fw, 2.5 * s))), 5.4 * s)]
    sh = fr.shape().hull(front)
    k = "f" if J["kn_f"][0] > J["kn_n"][0] else "n"
    if not J["pose"]["rot"] and J["kn_" + k][1] < P[1] - 8 * s:      # hangs to the knee when upright
        sh.hull([front[1], front[2], (fr.P(add(J["kn_" + k], mul(up, 2 * s))), 4.6 * s)])
    ga.add(sh.mask(), apron)
    ga.detail(fr.line([add(W, mul(fw, -2 * s)), add(W, mul(fw, 7 * s))]), apron.sh2)
    # pearls
    fr.group(52, outline=False).detail(
        fr.dots([add(N, add(mul(fw, (x - 0.5) * s), mul(up, y * s))) for x, y in
                 ((-3, -1), (-1, -3), (1, -4), (3, -3), (5, -1))]), "#fcfcfc", clip=False)
    if J["pose"]["prop"] == "pot":
        _pot(fr, _hand_centre(J, "n", 6), 76)
    _head(fr, J, JULIA_HEAD, JULIA_PAL, ofs=(1, 0))


def _pot(fr, c, z):
    pot = Ramp("#e87830", hi="#fcb060", sh1="#b04c20", sh2="#783018", line="#3c1410")
    g = fr.group(z, s1=2, s2=1)
    g.add(fr.shape().poly([fr.P(add(c, d)) for d in ((-6, 4), (6, 4), (5, -5), (-5, -5))]).mask(), pot)
    g.add(fr.shape().poly([fr.P(add(c, d)) for d in ((-7, 6), (7, 6), (7, 4), (-7, 4))]).mask(), pot.darker())
    g.add(fr.shape().poly([fr.P(add(c, d)) for d in ((6, 2), (10, 2), (10, 0), (6, 0))]).mask(), pot.darker())


JULIA_POSES = {
    # "Bon appetit!" - heave the stockpot overhead and lob it
    "sp0": dict(pelvis=(-3, 41), lean=-10, twist=0.3, hf=(8, -4), hn=(-6, 22), prop="pot", back_n=True,
                head=(6, 0, 0)),
    "sp1": dict(pelvis=(0, 41), lean=2, twist=0.5, hf=(10, -6), hn=(6, 25), prop="pot", back_n=True, face="attack"),
    "sp2": dict(pelvis=(5, 39), lean=18, twist=-0.4, ff=(17, 4), fn=(-14, 4), hf=(-13, -21), hn=(26.5, 0),
                hand_n="open", head=(-8, 0, 0), face="attack"),
    "sp3": dict(pelvis=(3, 40), lean=12, twist=0.2, ff=(15, 4), fn=(-13, 4), hf=(4, -10), hn=(18, -10),
                hand_n="open"),
    "win0": dict(pelvis=(0, 46), lean=0, twist=0.9, ff=(7, 4), fn=(-7, 4), hf=(12, 18), hn=(-12, 18),
                 en=1, hand_f="open", hand_n="open", face="attack"),
    "win1": dict(pelvis=(0, 45), lean=0, twist=0.9, ff=(7, 4), fn=(-7, 4), hf=(14, 21), hn=(-14, 21),
                 en=1, hand_f="open", hand_n="open", face="attack"),
}


# ----------------------------------------------------------------- Thatcher
THATCHER_HEAD = [
    "......ooooooooo.....",
    "....ooLLLLLLLLLoo...",
    "..ooLLLLLHHLLLLLLo..",
    ".oLLLLHHLLLLLHHLLLo.",
    ".oLLHHLLLLLHHHHLLLo.",
    "oLLHHHLLLHHHHHHHLLLo",
    "oLHHHHHHHHHhhhHHHHLo",
    "oHHHkHHHHhhSSSShHHHo",
    "oHHkkHHSbbbSSbbbSHo.",
    "oHHkkHSSwweSSwweSo..",
    "oHHkkHsSSSSSSSSSSo..",
    ".oHkkPsSSSSSSSsSSSo.",
    ".okkkksSSSSSSSssSo..",
    "..okkssSSSmmmmSSo...",
    "...oo.osSSSSSSSo....",
    "......ossSSSSSo.....",
    ".......oossssoo.....",
    ".........oooo.......",
]
THATCHER_PAL = _face_pal(L="#f0cc7c", H="#cc9444", k="#8c5c2c", m="#c03848", b="#8c5c2c", P="#fcfcfc")


def thatcher(fr, J):
    s = J["s"]
    suit = _pick(Ramp("#2c50c8", hi="#6c94f8", sh1="#1c3490", sh2="#141e60", line="#0c1038"),
                 Ramp("#c8283c", hi="#f86c78", sh1="#901c34", sh2="#5c1028", line="#28081c"))
    hose = Ramp("#d8a078", hi="#f4c8a0", sh1="#a87058", sh2="#7c4c44", line="#40202c")
    shoe = Ramp("#22203a", hi="#5c5c88", sh1="#16142a", sh2="#0e0c1c", line="#080610")
    bag = Ramp("#3a2c2c", hi="#7c6458", sh1="#261c20", sh2="#181014", line="#0c0808")
    up, fw, W, N = J["up"], J["fw"], J["W"], J["N"]

    _limbs(fr, J, hose, shoe, suit, thick=1.04)
    _skirt(fr, J, 38, suit, r_knee=5.8)
    g = _torso(fr, J, 40, suit, chest=8.2, waist=6.2, hips=None)
    g.add(fr.shape().hull([(fr.P(add(W, mul(fw, -3 * s))), 4.6 * s), (fr.P(add(W, mul(fw, 3 * s))), 4.6 * s),
                           (fr.P(add(lerp(W, J["P"], 0.6), mul(fw, -3.5 * s))), 4.4 * s),
                           (fr.P(add(lerp(W, J["P"], 0.6), mul(fw, 3.5 * s))), 4.4 * s)]).mask(), suit)
    g.detail(fr.line([add(N, mul(fw, 3 * s)), add(W, mul(fw, 2 * s))]), suit.sh2)
    g.detail(fr.dots([add(lerp(N, W, t), mul(fw, 3.5 * s)) for t in (0.45, 0.7, 0.95)]), GOLD)
    # pussy-bow blouse
    fr.blob(50, [(add(N, add(mul(fw, 2 * s), mul(up, -1 * s))), 2.6 * s),
                 (add(N, add(mul(fw, 4 * s), mul(up, -4 * s))), 2.2 * s)],
            Ramp("#f4f0fa", sh1="#b8b4d8", sh2="#8884b4", line="#40407c"), s1=1, s2=0)
    # the handbag hangs from the near hand (and is the Iron Fist)
    d = _hand_dir(J, "n")
    hang = (0, -1) if J["pose"]["prop"] != "swing" else d
    h = add(_hand_centre(J, "n"), mul(hang, 8 * s))
    nrm = perp(hang)
    gb = fr.group(74, s1=2, s2=1)
    gb.add(fr.shape().poly([fr.P(add(h, add(mul(hang, a), mul(nrm, b)))) for a, b in
                            ((-4, -5.5), (-4, 5.5), (5, 6.5), (5, -6.5))]).mask(), bag)
    gb.detail(fr.dots([add(h, mul(hang, -2)), add(h, add(mul(hang, -2), mul(nrm, 1)))]), GOLD)
    _head(fr, J, THATCHER_HEAD, THATCHER_PAL, ofs=(1, 1))


THATCHER_POSES = {
    # "Iron Fist" - wind the handbag right round and bring it down
    "sp0": dict(pelvis=(-3, 41), lean=-8, twist=0.2, hf=(10, -4), hn=(-14, 8), prop="swing", back_n=True),
    "sp1": dict(pelvis=(0, 41), lean=0, twist=0.4, ff=(14, 4), hf=(10, -6), hn=(-4, 25), prop="swing", back_n=True,
                face="attack"),
    "sp2": dict(pelvis=(6, 38), lean=22, twist=-0.5, ff=(19, 4), fn=(-15, 4), hf=(-4, -8), hn=(27, -4),
                prop="swing", head=(-10, 0, 0), face="attack"),
    "sp3": dict(pelvis=(4, 39), lean=16, twist=0.1, ff=(17, 4), fn=(-14, 4), hf=(2, -8), hn=(18, -16),
                prop="swing"),
    "win0": dict(pelvis=(0, 46), lean=-2, twist=0.9, ff=(6, 4), fn=(-7, 4), hf=(2, -16), ef=1, hn=(3, -25)),
    "win1": dict(pelvis=(0, 46), lean=-2, twist=0.9, ff=(6, 4), fn=(-7, 4), hf=(2, -16), ef=1, hn=(3, -25),
                 head=(-6, 0, 0)),
}


# ---------------------------------------------------------------- The Witch
WITCH_SKIN = Ramp("#c8c4b0", hi="#e8e8d0", sh1="#948c98", sh2="#685c78", line="#342c44")
WITCH_HEAD = [
    "...o..oooo.oo..o....",
    "..oVooVVVVoVVooVo...",
    ".oVVVVVvVVVVVvVVo...",
    "oVVvVVVVVVvVVVVVVo..",
    "oVvVVVvVVVVVVVvVVVo.",
    ".oVVvVVVVhhhhVVVvVo.",
    "oVVVVvVhhSSSSSSVVVo.",
    "oVvVVVSbbbSSSbbbSVo.",
    ".oVVvSStweSSStweSo..",
    "oVVvVsSSSSSSSSSSSSo.",
    "oVvVVsSSSSSSSSSsSSSo",
    ".oVVvssSSSSSSSsssSSo",
    "oVVvVosSSSmmmmSSSoo.",
    ".oVvVo.osSSSSSSSo...",
    "oVVvo...ossSSSSo....",
    ".ovo.....oosSSo.....",
    "..o........ooo......",
]
WITCH_PAL = _face_pal(WITCH_SKIN, V="#a0b4d8", v="#6c7cb0", b="#342c44", m="#703868", t="#685c78")


def witch(fr, J):
    s = J["s"]
    robe = _pick(Ramp("#3c5470", hi="#6c94b0", sh1="#283854", sh2="#1a2238", line="#0e1020"),
                 Ramp("#74407c", hi="#b078b8", sh1="#502860", sh2="#341840", line="#180c24"))
    rag = Ramp("#584878", hi="#8c78b0", sh1="#3c2c58", sh2="#281c3c", line="#140c24")
    hair = Ramp("#a0b4d8", hi="#d0e0f8", sh1="#6c7cb0", sh2="#485088", line="#242850")
    foot = Ramp("#2c2438", hi="#5c5470", sh1="#1c1626", sh2="#120e1a", line="#0a0810")
    up, fw, W, N = J["up"], J["fw"], J["W"], J["N"]

    _limbs(fr, J, robe, foot, robe, hand=WITCH_SKIN, claws=True)
    _back_hair(fr, J, hair, length=1.15, r=(8.0, 7.5, 5.5))
    g = _dress(fr, J, 40, robe, length=0.62, skirt=dict(r_hem=6.4, r_knee=6.0))
    # tattered hem: bite notches out of the bottom edge with the outline colour
    if not J["pose"]["rot"]:
        for k in "fn":
            hem = lerp(J["kn_" + k], J["an_" + k], 0.62)
            for dx in (-4, 0, 4):
                g.detail(fr.line([add(hem, (dx * s, -6.5 * s)), add(hem, (dx * s, -3.5 * s))]), robe.line)
    g.detail(fr.line([add(W, mul(fw, -8 * s)), add(W, mul(fw, 8 * s))]), rag.base)
    fr.blob(50, [(add(J["sh_f"], mul(up, 2.0 * s)), 4.2 * s), (add(J["sh_n"], mul(up, 2.0 * s)), 4.6 * s),
                 (add(N, mul(up, -4 * s)), 5.0 * s)], rag, s1=1, s2=1)
    if J["pose"]["prop"] == "curse":
        c = add(lerp(J["ha_f"], J["ha_n"], 0.5), mul(fw, 9 * s))
        orb = Ramp("#58f878", hi="#e0ffd0", sh1="#20b858", sh2="#108848", line="#085030")
        fr.disc(78, c, 5.5 * s, orb, s1=1, s2=1)
        fr.group(79, outline=False).detail(
            fr.dots([add(c, d) for d in ((-9, 4), (8, 7), (10, -5), (-6, -8), (0, 10))]), "#e0ffd0", clip=False)
    _head(fr, J, WITCH_HEAD, WITCH_PAL, ofs=(2, -1))


def witch_modify(name, p):
    """She is permanently hunched, head thrust forward."""
    if not p.get("rot"):
        p["lean"] = p.get("lean", 0) + 7
        p["curl"] = p.get("curl", 0) + 12
        t, dx, dy = p.get("head", (0, 0, 0))
        p["head"] = (t - 14, dx + 1, dy)
    return p


WITCH_POSES = {
    # "Curse of the Woods" - gather the hex, hurl it
    "sp0": dict(pelvis=(-2, 40), lean=-6, twist=0.8, hf=(4, 16), hn=(-6, 18), en=1, sway=0.6),
    "sp1": dict(pelvis=(-1, 39), lean=2, twist=0.8, hf=(15, -7), hn=(11, -6), prop="curse", face="attack"),
    "sp2": dict(pelvis=(4, 38), lean=16, twist=0.9, ff=(17, 4), fn=(-14, 4), hf=(22, 0), hn=(20, -6),
                sway=-0.8, face="attack"),
    "sp3": dict(pelvis=(2, 39), lean=10, twist=0.7, ff=(15, 4), hf=(16, -6), hn=(12, -10), sway=-0.4),
    "win0": dict(pelvis=(0, 44), lean=-6, twist=0.9, ff=(7, 4), fn=(-7, 4), hf=(12, 16), hn=(-10, 18), en=1,
                 face="attack"),
    "win1": dict(pelvis=(0, 43), lean=-8, twist=0.9, ff=(7, 4), fn=(-7, 4), hf=(14, 19), hn=(-12, 21), en=1,
                 face="attack", sway=0.5),
}


# -------------------------------------------------------------------- Donna
DONNA_SKIN = Ramp("#e8a878", hi="#fcd0a0", sh1="#c07858", sh2="#905048", line="#50242c")
DONNA_HEAD = [
    "......oooooooo......",
    "....ooYYYYYYYYoo....",
    "...oYYYLLYYYYYYYo...",
    "..oYYLLYYYYYLLYYYo..",
    ".oYYLYYYYYYLLYYYYYo.",
    ".oYLYYYYYhhhhYYYYYo.",
    ".oYYYYYhhSSSSSSYYyo.",
    "oYYyYYSbbbSSSbbbSYo.",
    "oYYyYSSwweSSSwweSo..",
    "oYyyYsSSSSSSSSSSSo..",
    "oYyyYsSSSSSSSSSsSSo.",
    "oYyyYysSSSSSSSssSo..",
    "oYyyYyssSSmmmmSSo...",
    "oYYyyo.osSSSSSSo....",
    ".oYyyo..ossSSSo.....",
    ".oYYyo...oosso......",
    "..oYyo.....oo.......",
    "..oyo...............",
]
DONNA_PAL = _face_pal(DONNA_SKIN, Y="#f4d050", L="#fcf098", y="#c89428", b="#a0702c", m="#e0506c")


def donna(fr, J):
    s = J["s"]
    denim = _pick(Ramp("#4878d0", hi="#88b4f8", sh1="#3050a0", sh2="#203470", line="#101840"),
                  Ramp("#e86c9c", hi="#fca8c8", sh1="#b04478", sh2="#782c58", line="#38102c"))
    shirt = Ramp("#f8f4ec", hi="#ffffff", sh1="#c8c4dc", sh2="#9894c0", line="#4c487c")
    boot = Ramp("#a86838", hi="#dc9c5c", sh1="#784424", sh2="#502c1c", line="#281410")
    hair = Ramp("#f4d050", hi="#fcf098", sh1="#c89428", sh2="#946820", line="#4c3018")
    fw, W, P, C = J["fw"], J["W"], J["P"], J["C"]

    _limbs(fr, J, denim, boot, shirt, hand=DONNA_SKIN, fore=DONNA_SKIN, thick=1.02)
    _back_hair(fr, J, hair, length=0.75, r=(7.0, 6.0, 4.0))
    g = _torso(fr, J, 40, shirt, chest=7.6, waist=5.8, hips=6.8)
    # dungaree bib + straps
    bib = fr.shape()
    bib.hull([(fr.P(P), 6.8 * s), (fr.P(W), 5.8 * s)])
    bib.hull([(fr.P(W), 5.8 * s), (fr.P(add(lerp(W, C, 0.7), mul(fw, 1.0 * s))), 5.2 * s)])
    g.add(bib.mask(), denim)
    for k in "fn":
        g.detail(fr.line([J["sh_" + k], add(lerp(W, C, 0.9), mul(fw, (3 if k == "f" else -2) * s))]), denim.sh1)
    g.detail(fr.dots([add(lerp(W, C, 0.85), mul(fw, 3 * s)), add(lerp(W, C, 0.85), mul(fw, -2 * s))]), GOLD)
    _head(fr, J, DONNA_HEAD, DONNA_PAL, ofs=(0, -1))


DONNA_POSES = {
    # "Dancing Queen" - a whirling double spin, then the disco point
    "sp0": dict(pelvis=(0, 42), lean=4, twist=1.0, ff=(10, 4), fn=(-8, 6), fan=-30, hf=(22, 4), hn=(-22, 6),
                hand_f="open", hand_n="open", sway=1.0, face="attack"),
    "sp1": dict(pelvis=(2, 43), lean=0, twist=-1.0, ff=(-6, 6), fn=(8, 4), faf=-30, hf=(-20, 6), hn=(24, 2),
                hand_f="open", hand_n="open", sway=-1.0, face="attack", front_f=True),
    "sp2": dict(pelvis=(3, 42), lean=6, twist=1.0, ff=(12, 4), fn=(-8, 6), fan=-30, hf=(26, 2), hn=(-20, 8),
                hand_f="open", hand_n="open", sway=1.0, face="attack"),
    "sp3": dict(pelvis=(0, 44), lean=-6, twist=0.8, ff=(10, 4), fn=(-10, 4), hf=(9, 25), hn=(-6, -16),
                hand_f="open", sway=0.3, face="attack"),
    "win0": dict(pelvis=(0, 45), lean=-6, twist=0.8, ff=(9, 4), fn=(-9, 4), hf=(11, 24), hn=(-6, -16),
                 hand_f="open", face="attack"),
    "win1": dict(pelvis=(2, 44), lean=4, twist=0.8, ff=(9, 4), fn=(-9, 4), hf=(16, -18), hn=(-10, 22), en=1,
                 hand_n="open", face="attack", sway=0.6),
}


# ----------------------------------------------------------------- Aloysius
ALOYSIUS_SKIN = Ramp("#f0c4a4", hi="#ffe4cc", sh1="#c8947c", sh2="#986860", line="#543038")
ALOYSIUS_HEAD = [
    ".....ooooooooo......",
    "...ooNNNNNNNNNoo....",
    "..oNNnNNNNNNNNNNo...",
    ".oNNnNNNNNNNNNNNNo..",
    ".oNnNNNNNNNNNNNNNNo.",
    "oNNnNNNNNNffffffNNo.",
    "oNnNNNNNffhhSSSSfNo.",
    "oNnNNNNfSbbbSSbbbfo.",
    "oNnNNNNfSgegSSgegSo.",
    "oNNnNNNfsSSSSSSSSSo.",
    ".oNnNNNfsSSSSSSsSSSo",
    ".oNNnNNfsSSSSSSssSo.",
    "..oNnNNNfsSSmmmmSo..",
    "..oNNnNNNffSSSSSo...",
    "...oNNnNNNNffffo....",
    "....ooNNNNNNNNo.....",
    "......oooooooo......",
]
ALOYSIUS_PAL = _face_pal(ALOYSIUS_SKIN, N="#34303f", n="#5c5870", f="#f4f0fa", g="#c8a040", b="#4c3c48",
                         m="#a04450")


def aloysius(fr, J):
    s = J["s"]
    # mirror match: a white-habited novice
    habit = _pick(Ramp("#34303f", hi="#6c6884", sh1="#221f2c", sh2="#16141e", line="#0a0810"),
                  Ramp("#d8d4e8", hi="#ffffff", sh1="#a8a4c8", sh2="#7c78a4", line="#34305c"))
    cape = _pick(Ramp("#2a2634", hi="#5c5870", sh1="#1c1a26", sh2="#121018", line="#0a0810"),
                 Ramp("#c0bcd8", hi="#f4f0fc", sh1="#9490b8", sh2="#6c6898", line="#34305c"))
    white = Ramp("#f4f0fa", hi="#ffffff", sh1="#bcb8d8", sh2="#8c88b4", line="#44407c")
    shoe = Ramp("#1e1a26", hi="#4c4860", sh1="#14121c", sh2="#0c0a12", line="#060408")
    wood = Ramp("#c89050", hi="#f0c080", sh1="#946030", sh2="#684020", line="#301c10")
    up, fw, N = J["up"], J["fw"], J["N"]

    _limbs(fr, J, habit, shoe, habit, hand=ALOYSIUS_SKIN, thick=1.05)
    _dress(fr, J, 40, habit, length=0.82, skirt=dict(r_hem=6.0, r_knee=6.0), torso=dict(chest=7.8, waist=6.0))
    # shoulder cape + white collar + crucifix
    fr.blob(50, [(add(J["sh_f"], mul(up, 1.0 * s)), 5.0 * s), (add(J["sh_n"], mul(up, 1.0 * s)), 5.4 * s),
                 (add(N, mul(up, -6 * s)), 6.4 * s)], cape, s1=2, s2=1)
    fr.blob(52, [(add(N, add(mul(fw, 1.5 * s), mul(up, -0.5 * s))), 2.6 * s),
                 (add(N, add(mul(fw, 4.0 * s), mul(up, -2.5 * s))), 1.8 * s)], white, s1=1, s2=0)
    cx = add(N, add(mul(fw, 3 * s), mul(up, -9 * s)))
    fr.group(54, outline=False).detail(
        fr.dots([add(cx, d) for d in ((0, 0), (0, 1), (0, -1), (0, -2), (-1, 0), (1, 0))]), GOLD, clip=False)
    # the ruler lives in the far (jabbing) hand
    d = _hand_dir(J, "f")
    base = _hand_centre(J, "f", 1.0)
    tip = add(base, mul(d if J["pose"]["prop"] != "raise" else norm(add(d, mul(up, 0.6))), 17 * s))
    gr = fr.group(13 if not J["pose"]["front_f"] else 68, s1=1, s2=0)
    gr.add(fr.shape().capsule(fr.P(base), fr.P(tip), 1.3, 1.3).mask(), wood)
    pal = _pick(ALOYSIUS_PAL, dict(ALOYSIUS_PAL, N="#d8d4e8", n="#ffffff", f="#a8a4c8"))
    _head(fr, J, ALOYSIUS_HEAD, pal, ofs=(0, 0))


ALOYSIUS_POSES = {
    # "Divine Discipline" - ruler raised to heaven, lunge, crack it down
    "sp0": dict(pelvis=(-3, 42), lean=-8, twist=0.6, hf=(6, 25), hn=(6, -8)),
    "sp1": dict(pelvis=(4, 38), lean=18, twist=0.8, ff=(19, 4), fn=(-16, 5), fan=-25, hf=(12, 22),
                hn=(4, -8), face="attack"),
    "sp2": dict(pelvis=(7, 38), lean=24, twist=1.0, ff=(20, 4), fn=(-15, 4), hf=(26, -6), hn=(2, -10),
                front_f=True, head=(-12, 0, 0), face="attack"),
    "sp3": dict(pelvis=(4, 39), lean=14, twist=0.8, ff=(18, 4), fn=(-14, 4), hf=(18, -14), hn=(4, -9),
                front_f=True),
    "win0": dict(pelvis=(0, 46), lean=0, twist=0.9, ff=(5, 4), fn=(-6, 4), hf=(6, -8), hn=(2, -10)),
    "win1": dict(pelvis=(0, 46), lean=2, twist=0.9, ff=(5, 4), fn=(-6, 4), hf=(6, -8), hn=(2, -10),
                 head=(12, 0, 0)),
}


# sheet order == FighterData index order in the game
FIGHTERS = {
    "miranda": dict(draw=miranda, body=dict(scale=1.0), poses=MIRANDA_POSES),
    "julia": dict(draw=julia, body=dict(scale=1.08, shw=8.4), poses=JULIA_POSES),
    "thatcher": dict(draw=thatcher, body=dict(scale=0.97, shw=8.6), poses=THATCHER_POSES),
    "witch": dict(draw=witch, body=dict(scale=0.97), poses=WITCH_POSES, modify=witch_modify),
    "donna": dict(draw=donna, body=dict(scale=1.0), poses=DONNA_POSES),
    "aloysius": dict(draw=aloysius, body=dict(scale=0.99, shw=8.2), poses=ALOYSIUS_POSES),
}
