"""2D fighter skeleton: pose (IK targets) -> joints -> costume layers -> frame.

Rig space: origin on the ground under the fighter, +x = facing direction,
+y = up, units = pixels at 1x.  "f" limbs are the far/lead side (drawn behind
the torso), "n" limbs the near/rear side (drawn in front) - the classic
SF2 three-quarter stance with the chest opened toward the camera.
"""
import math

import px

CELL = (144, 128)   # every frame is one cell of this size
ORG = (56, 121)     # rig origin inside the cell (ground line under the hips)

BODY = dict(ank=4.0, shin=21.0, thigh=22.0, abd=11.0, chest=17.0, neck=3.0, head=7.5,
            upper=14.0, fore=13.0, hipw=4.0, shw=8.0, foot=8.0, scale=1.0)

POSE = dict(
    pelvis=(0, 41), lean=6, curl=0, twist=0.6, head=(0, 0, 0),
    hf=(11, -3), hn=(8, -7), ef=-1, en=-1,          # hands rel. to their shoulder
    ff=(13, 4), fn=(-12, 4), faf=0, fan=0, kf=1, kn=1,  # ankles (absolute), foot angles
    face="neutral", rot=0, pivot=None, ofs=(0, 0),
    hand_f="fist", hand_n="fist", sway=0.0, front_f=False, back_n=False, prop=None,
)


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def mul(a, k):
    return (a[0] * k, a[1] * k)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def rot(v, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return (v[0] * c - v[1] * s, v[0] * s + v[1] * c)


def norm(v):
    d = math.hypot(v[0], v[1]) or 1e-6
    return (v[0] / d, v[1] / d)


def perp(v):
    return (-v[1], v[0])


def ik(a, c, l1, l2, bend):
    """Two-bone IK.  Returns (mid joint, clamped end)."""
    dx, dy = c[0] - a[0], c[1] - a[1]
    d = math.hypot(dx, dy)
    if d < 1e-6:
        dx, d = 1e-6, 1e-6
    dd = min(max(d, abs(l1 - l2) + 0.05), l1 + l2 - 0.05)
    ux, uy = dx / d, dy / d
    end = (a[0] + ux * dd, a[1] + uy * dd)
    x = (l1 * l1 - l2 * l2 + dd * dd) / (2 * dd)
    h = math.sqrt(max(l1 * l1 - x * x, 0.0))
    return (a[0] + ux * x - uy * h * bend, a[1] + uy * x + ux * h * bend), end


def solve(body, pose):
    p = dict(POSE)
    p.update(pose)
    b = dict(BODY)
    b.update(body)
    s = b["scale"]
    L = lambda k: b[k] * s
    J = {}
    P = mul(p["pelvis"], s)
    up_a = rot((0, 1), -p["lean"])
    W = add(P, mul(up_a, L("abd")))
    up_c = rot((0, 1), -(p["lean"] + p["curl"]))
    fw_c = rot(up_c, -90)
    N = add(W, mul(up_c, L("chest")))
    t = p["twist"]
    tilt, hdx, hdy = p["head"]
    up_h = rot(up_c, -tilt)
    J.update(P=P, W=W, N=N, C=add(W, mul(up_c, L("chest") * 0.55)),
             H=add(add(N, mul(up_h, L("neck") + L("head"))), (hdx, hdy)))
    for side, sg in (("f", 1), ("n", -1)):
        sh = add(add(N, mul(fw_c, L("shw") * t * sg)), mul(up_c, -2.5 * s))
        hip = add(P, (L("hipw") * t * sg, 0))
        el, ha = ik(sh, add(sh, mul(p["h" + side], s)), L("upper"), L("fore"), p["e" + side])
        kn, an = ik(hip, mul(p["f" + side], s), L("thigh"), L("shin"), p["k" + side])
        fa = p["fa" + side]
        J["sh_" + side], J["hip_" + side] = sh, hip
        J["el_" + side], J["ha_" + side] = el, ha
        J["kn_" + side], J["an_" + side] = kn, an
        J["heel_" + side] = add(an, rot((-1.5 * s, -(L("ank") - 2.0)), fa))
        J["toe_" + side] = add(an, rot((L("foot") - 1.5, -(L("ank") - 1.6)), fa))
    if p["rot"]:
        piv = p["pivot"] or J["P"]
        for k in list(J):
            J[k] = add(piv, rot(sub(J[k], piv), p["rot"]))
        up_c, fw_c, up_h = rot(up_c, p["rot"]), rot(fw_c, p["rot"]), rot(up_h, p["rot"])
    if p["ofs"] != (0, 0):
        for k in list(J):
            J[k] = add(J[k], mul(p["ofs"], s))
    J.update(up=up_c, fw=fw_c, up_h=up_h, pose=p, body=b, s=s)
    return J


class Frame:
    """Collects costume layers for one cell and renders them."""

    def __init__(self, size=CELL, org=ORG):
        self.size, self.org, self.layers = size, org, []

    def P(self, pt):
        return (self.org[0] + pt[0], self.org[1] - pt[1])

    def shape(self):
        return px.Shape(self.size)

    def group(self, z, **kw):
        g = px.Group(z, **kw)
        self.layers.append(g)
        return g

    def bitmap(self, z, img, centre):
        """Stamp img centred on rig point `centre`."""
        c = self.P(centre)
        self.layers.append(px.Bitmap(z, img, (c[0] - img.width / 2.0, c[1] - img.height / 2.0)))

    def render(self):
        return px.render(self.size, self.layers)

    # ---- reusable costume pieces -------------------------------------
    def limb(self, z, a, b, c, radii, upper, lower=None, dark=0, hi=1, s1=1, s2=1):
        """Two-segment limb a->b->c.  radii = (ra, rb, rc)."""
        ra, rb, rc = radii
        g = self.group(z, hi=hi, s1=s1, s2=s2, dark=dark)
        g.add(self.shape().capsule(self.P(a), self.P(b), ra, rb).mask(), upper)
        g.add(self.shape().capsule(self.P(b), self.P(c), rb, rc).mask(), lower or upper)
        return g

    def blob(self, z, circles, ramp, **kw):
        g = self.group(z, **kw)
        g.add(self.shape().hull([(self.P(c), r) for c, r in circles]).mask(), ramp)
        return g

    def disc(self, z, c, r, ramp, **kw):
        g = self.group(z, **kw)
        g.add(self.shape().circle(self.P(c), r).mask(), ramp)
        return g

    def foot(self, z, J, side, ramp, dark=0, heel=0.0):
        s = J["s"]
        g = self.group(z, hi=1, s1=1, s2=0, dark=dark)
        sh = self.shape().capsule(self.P(J["heel_" + side]), self.P(J["toe_" + side]), 2.3 * s, 1.7 * s)
        sh.circle(self.P(J["an_" + side]), 2.2 * s)
        g.add(sh.mask(), ramp)
        return g

    def line(self, pts, width=1):
        return px.line_mask(self.size, [self.P(p) for p in pts], width)

    def dots(self, pts):
        return px.dot_mask(self.size, [self.P(p) for p in pts])
