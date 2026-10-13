"""The pose library: every animation frame, as IK targets (see rig.POSE).

FRAMES is the sheet order - one cell per name, shared by all fighters, so the
game addresses frames by constant index (emitted to SpriteFrames.g.cs).
Units are pixels on the reference body (hip 47 high standing straight,
41 in the fighting stance); taller/shorter fighters scale automatically.
"""

FRAMES = [
    "idle0", "idle1", "idle2", "idle3",
    "walk0", "walk1", "walk2", "walk3", "walk4", "walk5",
    "crouch0", "crouch1",
    "jump0", "jump1", "jump2",
    "punch0", "punch1", "punch2",
    "kick0", "kick1", "kick2",
    "cpunch0", "cpunch1",
    "ckick0", "ckick1",
    "jpunch0", "jkick0",
    "block0", "cblock0",
    "hurt0", "hurt1", "churt0",
    "kd0", "kd1", "kd2",
    "getup0", "getup1",
    "sp0", "sp1", "sp2", "sp3",
    "win0", "win1", "lose0",
]
COLS = 8

STANCE = dict(pelvis=(0, 41), lean=6, twist=0.6, ff=(13, 4), fn=(-12, 4), hf=(11, -3), hn=(8, -7))
CROUCH = dict(pelvis=(-2, 20), lean=16, twist=0.6, ff=(12, 4), fn=(-12, 4), hf=(11, -1), hn=(8, -5),
              head=(-8, 0, 0))
AIR = dict(pelvis=(0, 50), lean=12, twist=0.6, ff=(11, 31), fn=(-1, 27), hf=(9, -5), hn=(5, -9))
FLAT = dict(pelvis=(0, 47), lean=0, twist=0.5, ff=(3, 4), fn=(-3, 4), hf=(4, -26), hn=(-3, -26),
            face="hurt")


def S(**kw):
    return dict(STANCE, **kw)


def C(**kw):
    return dict(CROUCH, **kw)


def A(**kw):
    return dict(AIR, **kw)


POSES = {
    # ---- idle: a breathing bounce on the guard
    "idle0": S(),
    "idle1": S(pelvis=(0, 40), hf=(11, -4), hn=(8, -8)),
    "idle2": S(pelvis=(0, 39), lean=7, hf=(11, -4), hn=(8, -8)),
    "idle3": S(pelvis=(0, 40), hf=(11, -3), hn=(8, -7)),

    # ---- walk: contact / down / passing, both sides.  Guard stays up.
    "walk0": S(pelvis=(0, 41), ff=(14, 4), fn=(-12, 5), fan=-8),
    "walk1": S(pelvis=(0, 40), ff=(8, 4), fn=(-9, 9), fan=-22, hf=(10, -3), hn=(9, -7)),
    "walk2": S(pelvis=(0, 42), ff=(1, 4), fn=(4, 11), fan=-10, hf=(10, -2), hn=(9, -6)),
    "walk3": S(pelvis=(0, 41), ff=(-11, 5), fn=(14, 4), faf=-8),
    "walk4": S(pelvis=(0, 40), ff=(-8, 9), fn=(8, 4), faf=-22, hf=(12, -3), hn=(7, -7)),
    "walk5": S(pelvis=(0, 42), ff=(5, 11), fn=(0, 4), faf=-10, hf=(12, -2), hn=(7, -6)),

    # ---- crouch (crouch0 doubles as pre-jump squat and landing)
    "crouch0": S(pelvis=(-1, 31), lean=11, hf=(11, -2), hn=(8, -6)),
    "crouch1": C(),

    # ---- jump: push-off, tuck at the apex, reach for the floor
    "jump0": S(pelvis=(0, 47), lean=2, ff=(6, 7), fn=(-5, 3), faf=-35, fan=-35, hf=(11, 7), hn=(8, 3)),
    "jump1": A(),
    "jump2": A(pelvis=(0, 48), lean=4, ff=(9, 12), fn=(-6, 8), faf=-20, fan=-20, hf=(14, 3), hn=(10, -2)),

    # ---- standing punch: cock, snap out a long straight, pull back
    "punch0": S(pelvis=(-1, 41), lean=2, twist=0.4, hf=(6, -8), hn=(8, -6)),
    "punch1": S(pelvis=(4, 40), lean=13, twist=0.95, ff=(16, 4), fn=(-13, 4), hf=(26.5, 2), hn=(6, -8),
                head=(-6, 0, 0), face="attack"),
    "punch2": S(pelvis=(2, 40), lean=9, twist=0.8, ff=(15, 4), hf=(17, -1), hn=(5, -7)),

    # ---- standing kick: chamber the rear leg, whip it out high, recoil
    "kick0": S(pelvis=(-2, 44), lean=-4, twist=0.4, ff=(2, 4), fn=(9, 30), fan=-40, hf=(10, -6), hn=(-2, -25)),
    "kick1": S(pelvis=(-3, 45), lean=-19, twist=0.15, ff=(2, 4), fn=(37, 55), fan=28, hf=(13, -7),
               hn=(-15, -21), head=(10, 0, 0), face="attack"),
    "kick2": S(pelvis=(-2, 44), lean=-9, twist=0.3, ff=(2, 4), fn=(18, 32), fan=-25, hf=(11, -6), hn=(-9, -23)),

    # ---- crouching punch
    "cpunch0": C(lean=12, twist=0.4, hf=(6, -7)),
    "cpunch1": C(pelvis=(0, 20), lean=22, twist=0.95, hf=(26.5, 1), hn=(7, -7), head=(-14, 0, 0), face="attack"),

    # ---- crouching kick: a low sweep along the floor
    "ckick0": C(pelvis=(-3, 20), lean=6, fn=(4, 10), fan=-20),
    "ckick1": C(pelvis=(-5, 17), lean=-8, twist=0.2, ff=(5, 4), fn=(38, 5), fan=18, hf=(10, -5),
                hn=(-14, -22), head=(0, 0, 0), face="attack"),

    # ---- jumping attacks
    "jpunch0": A(lean=24, twist=0.95, hf=(22, -15), hn=(2, -8), head=(-12, 0, 0), face="attack"),
    "jkick0": A(pelvis=(-2, 50), lean=-8, twist=0.2, ff=(4, 34), fn=(33, 26), fan=-14, hf=(11, -6),
                hn=(-15, -21), face="attack"),

    # ---- guard
    "block0": S(pelvis=(-2, 41), lean=-3, twist=0.35, hf=(9, 5), hn=(11, 1), head=(8, 0, -1)),
    "cblock0": C(pelvis=(-3, 20), lean=8, twist=0.35, hf=(9, 5), hn=(11, 1), head=(4, 0, -1)),

    # ---- hit reactions
    "hurt0": S(pelvis=(-4, 41), lean=-17, twist=0.4, hf=(15, -10), hn=(-13, -22), head=(-16, -1, 0),
               face="hurt"),
    "hurt1": S(pelvis=(-3, 38), lean=17, curl=14, twist=0.5, hf=(4, -13), hn=(6, -15), head=(12, 0, 0),
               face="hurt"),
    "churt0": C(pelvis=(-4, 20), lean=-4, hf=(14, -8), hn=(-14, -22), head=(-14, -1, 0), face="hurt"),

    # ---- knockdown: blown off the feet, flat on the back, then up
    "kd0": dict(FLAT, lean=-10, ff=(10, 6), fn=(4, 2), hf=(14, 2), hn=(8, 8), rot=48, ofs=(-2, 4),
                head=(-10, 0, 0)),
    "kd1": dict(FLAT, lean=-6, ff=(8, 8), fn=(2, 5), hf=(10, -14), hn=(-2, -20), rot=80, ofs=(0, -24)),
    "kd2": dict(FLAT, ff=(4, 5), fn=(-2, 4), faf=40, fan=40, hf=(2, -24), hn=(-6, -22), rot=90,
                ofs=(0, -41)),
    "getup0": dict(pelvis=(-6, 9), lean=-34, curl=20, twist=0.4, ff=(16, 4), fn=(10, 4), hf=(12, -14),
                   hn=(-14, -23), head=(14, 0, 0), face="hurt"),
    "getup1": C(pelvis=(-2, 24), lean=24, hf=(9, -12), hn=(4, -14), head=(-4, 0, 0)),

    # ---- signature move: generic fallback (each fighter overrides sp0..sp3)
    "sp0": S(pelvis=(-2, 40), lean=0, twist=0.3, hf=(-2, -4), hn=(-6, -2)),
    "sp1": S(pelvis=(3, 39), lean=14, twist=0.9, hf=(24, 0), hn=(20, -6), face="attack"),
    "sp2": S(pelvis=(5, 39), lean=16, twist=1.0, hf=(29, 2), hn=(26, -4), face="attack"),
    "sp3": S(pelvis=(2, 40), lean=10, hf=(16, -2), hn=(12, -6)),

    # ---- round over
    "win0": dict(pelvis=(0, 46), lean=0, twist=0.9, ff=(7, 4), fn=(-7, 4), hf=(3, 22), hn=(-4, -14),
                 face="attack"),
    "win1": dict(pelvis=(0, 45), lean=-2, twist=0.9, ff=(7, 4), fn=(-7, 4), hf=(4, 26), hn=(-4, -14),
                 face="attack"),
    "lose0": dict(pelvis=(-2, 44), lean=22, curl=18, twist=0.5, ff=(6, 4), fn=(-8, 4), hf=(3, -27),
                  hn=(1, -27), head=(18, 0, 0), face="hurt"),
}


def pose(name, overrides=None, modify=None):
    p = dict(POSES[name])
    if overrides and name in overrides:
        p.update(overrides[name])
    if modify:
        p = modify(name, p)
    return p
