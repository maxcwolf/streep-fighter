"""Pose audit: measure every arm and leg in every frame against anatomy.

    python3 Tools/art/audit.py [out.png]

Prints one line per problem and, if a path is given, saves a contact sheet of
the flagged frames with the offending limb traced in red.

The fighters face +x.  With the upper arm as u and the forearm as f, an
elbow seen side-on can only fold one way: cross(u, f) >= 0.  Knees fold the
other way.  When the chest is turned to the camera (twist >= 0.75) an arm held
out to the side may fold up or down (cheers, hands on hips), so an elbow that
points away from the body is allowed either bend.
"""
import math
import sys

from PIL import Image, ImageDraw

import anims
import font
import rig
import sheet
from fighters import FIGHTERS
from rig import norm, sub


def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def audit_pose(key, name):
    spec = FIGHTERS[key]
    p = anims.pose(name, spec.get("poses"), spec.get("modify"))
    J = rig.solve(spec["body"], p)
    b, s, up, fw = J["body"], J["s"], J["up"], J["fw"]
    pose = J["pose"]
    spinning = pose["twist"] < -0.8          # mid-pirouette: no side-on reading of the arms
    frontal = pose["twist"] >= 0.75
    lying = abs(pose["rot"]) >= 70
    out = []

    for side in "fn":
        sh, el, ha = J["sh_" + side], J["el_" + side], J["ha_" + side]
        u, f = norm(sub(el, sh)), norm(sub(ha, el))
        flex = cross(u, f)
        inner = math.degrees(math.acos(max(-1.0, min(1.0, -dot(u, f)))))   # 180 = straight
        want = math.hypot(*pose["h" + side]) * s
        reach = (b["upper"] + b["fore"]) * s
        el_up, el_fw = dot(sub(el, sh), up), dot(sub(el, sh), fw)
        ha_drop = dot(sub(ha, el), up)
        ha_fw = dot(sub(ha, sh), fw)
        arm = "far arm" if side == "f" else "near arm"

        outward = el_fw > 2 * s if side == "f" else el_fw < -2 * s
        sideways = frontal and outward       # held out to the side, chest to camera
        if spinning:
            pass
        elif flex < -0.12 and inner < 165 and not sideways:
            out.append((arm, side, "elbow bends backwards (%d deg the wrong way)" % round(180 - inner)))
        elif el_up > 3 * s and ha_drop < -6 * s and el_fw < -2 * s and not sideways:
            out.append((arm, side, "chicken wing: elbow hiked up behind, forearm dangling"))
        elif el_fw < -10 * s and ha_fw < -6 * s and inner < 125 and not sideways and not lying:
            out.append((arm, side, "arm folded behind the back"))
        if want > reach + 1.5:
            out.append((arm, side, "target %.0fpx out of reach: arm locked dead straight" % (want - reach)))
        if inner < 32:
            out.append((arm, side, "elbow folded shut (%d deg)" % round(inner)))
        # far arm is drawn behind the torso: a hand parked on the chest simply vanishes
        if side == "f" and not pose["front_f"]:
            rel = sub(ha, J["C"])
            if abs(dot(rel, fw)) < 4.5 * s and abs(dot(rel, up)) < 9 * s:
                out.append((arm, side, "hand hidden behind the torso"))

    for side in "fn":
        hip, kn, an = J["hip_" + side], J["kn_" + side], J["an_" + side]
        t, c = norm(sub(kn, hip)), norm(sub(an, kn))
        inner = math.degrees(math.acos(max(-1.0, min(1.0, -dot(t, c)))))
        if cross(t, c) > 0.12 and inner < 165:
            out.append(("far leg" if side == "f" else "near leg", "k" + side,
                        "knee bends backwards (%d deg the wrong way)" % round(180 - inner)))
    return J, out


def run(out_png=None):
    flagged, seen = [], {}
    for key in FIGHTERS:
        for name in anims.FRAMES:
            J, problems = audit_pose(key, name)
            if not problems:
                continue
            sig = (name, tuple(problems))
            if sig in seen:                  # same pose, same faults: report once for the whole cast
                seen[sig].append(key)
                continue
            seen[sig] = [key]
            flagged.append((key, name, J, problems, seen[sig]))

    for key, name, _J, problems, who in flagged:
        cast = "all" if len(who) == len(FIGHTERS) else ",".join(who)
        for limb, _side, msg in problems:
            print("%-8s %-22s %-9s %s" % (name, cast, limb, msg))
    print("%d flagged frames, %d problems" % (len(flagged), sum(len(f[3]) for f in flagged)))

    if out_png and flagged:
        cw, ch = rig.CELL
        cols = min(6, len(flagged))
        rows = (len(flagged) + cols - 1) // cols
        im = Image.new("RGBA", (cw * cols, ch * rows), (96, 104, 128, 255))
        d = ImageDraw.Draw(im)
        for i, (key, name, J, problems, _who) in enumerate(flagged):
            x, y = (i % cols) * cw, (i // cols) * ch
            im.alpha_composite(sheet.render_frame(key, name), (x, y))
            P = lambda pt: (x + rig.ORG[0] + pt[0], y + rig.ORG[1] - pt[1])
            for _limb, side, _msg in problems:
                pts = ([J["hip_" + side[1]], J["kn_" + side[1]], J["an_" + side[1]]] if side[0] == "k"
                       else [J["sh_" + side], J["el_" + side], J["ha_" + side]])
                d.line([P(q) for q in pts], fill=(255, 40, 40, 255), width=1)
            font.draw(im, (x + 2, y + 2), "%s %s" % (key[:3], name), (255, 255, 255), shadow=(0, 0, 0))
        im.resize((im.width * 3, im.height * 3), Image.NEAREST).save(out_png)
    return flagged


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else None)
