#!/usr/bin/env python3
"""Draw one ripe strawberry, extreme close-up, on dark slate.

Build-time composer only (PIL). The graded program is main.py, which
merely copies the pre-drawn entry.png.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFilter

W = H = 1024
OUT = "entry.png"
CX = 512  # berry centre x


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def catmull_rom(points, samples=24):
    """Smooth closed curve through control points."""
    pts = points + [points[0]]
    out = []
    n = len(points)
    for i in range(n):
        p0 = pts[(i - 1) % n]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n]
        for s in range(samples):
            t = s / samples
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t
                       + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                       + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t
                       + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                       + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    return out


def body_outline():
    ctrl = [
        (512, 296), (372, 302), (272, 400), (250, 540), (300, 690),
        (382, 812), (466, 872), (512, 892), (558, 872), (642, 812),
        (724, 690), (774, 540), (752, 400), (652, 302),
    ]
    return catmull_rom(ctrl)


def half_width_at(y, outline):
    """Body half-width at height y, from the outline points."""
    xs = [x for (x, yy) in outline if abs(yy - y) < 14]
    if not xs:
        return 0
    return (max(xs) - min(xs)) / 2.0


def make_gradient():
    """Small radial-ish red gradient, upscaled; highlight upper-left."""
    s = 256
    hi = (0.38, 0.30)  # highlight position (fraction)
    top = (238, 74, 62)
    mid = (206, 32, 34)
    bot = (132, 8, 14)
    px = []
    for yy in range(s):
        fy = yy / (s - 1)
        for xx in range(s):
            fx = xx / (s - 1)
            d = math.hypot(fx - hi[0], (fy - hi[1]) * 1.15)
            glow = max(0.0, 1.0 - d / 0.85)
            base = lerp(mid, bot, min(1.0, fy * 1.15))
            c = lerp(base, top, glow * glow * 0.85)
            px.append(c)
    g = Image.new("RGB", (s, s))
    g.putdata(px)
    return g.resize((W, H), Image.BICUBIC)


def main():
    rng = random.Random(20261122)
    img = Image.new("RGB", (W, H), (16, 19, 26))
    d = ImageDraw.Draw(img)

    # --- backdrop: soft warm glow behind the berry, dark vignette ---
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([180, 180, 844, 980], fill=(52, 40, 38))
    glow = glow.filter(ImageFilter.GaussianBlur(140))
    img = Image.blend(img, Image.blend(img, glow, 0.55), 1.0)
    d = ImageDraw.Draw(img)

    outline = body_outline()

    # --- contact shadow ---
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([320, 856, 704, 930], fill=(0, 0, 0, 185))
    sh = sh.filter(ImageFilter.GaussianBlur(20))
    img.paste(Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)

    # --- berry body: gradient clipped to the outline mask ---
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.polygon(outline, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(2))
    grad = make_gradient()
    img.paste(grad, (0, 0), mask)
    d = ImageDraw.Draw(img)

    # --- gloss: soft highlight upper-left, clipped to body ---
    gloss = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdr = ImageDraw.Draw(gloss)
    gdr.ellipse([300, 330, 520, 520], fill=(255, 225, 205, 55))
    gdr.ellipse([330, 360, 460, 480], fill=(255, 240, 225, 70))
    gloss = gloss.filter(ImageFilter.GaussianBlur(28))
    body_mask = mask.point(lambda v: v)
    img.paste(Image.alpha_composite(img.convert("RGBA"), gloss).convert("RGB"),
              (0, 0), body_mask)
    d = ImageDraw.Draw(img)

    # --- achenes (seeds): arched rows following the body curve ---
    for row_y in range(388, 830, 44):
        hw = half_width_at(row_y, outline)
        if hw < 40:
            continue
        # arc sag: rows bow downward toward the edges
        span = hw - 30
        n = max(2, int(span / 54))
        for i in range(n):
            fx = -1.0 + 2.0 * (i + 0.5) / n
            x = CX + fx * span + rng.uniform(-6, 6)
            y = row_y + 20 * fx * fx + rng.uniform(-4, 4)
            r = rng.uniform(0.85, 1.15)
            # pit shadow, then the pale seed
            d.ellipse([x - 8 * r, y - 5 * r, x + 8 * r, y + 11 * r], fill=(128, 18, 22))
            d.ellipse([x - 6 * r, y - 8 * r, x + 6 * r, y + 8 * r], fill=(246, 232, 184))
            d.ellipse([x - 3 * r, y - 6 * r, x + 3 * r, y + 1 * r], fill=(252, 242, 205))

    # --- dew drops: glistening beads on the skin ---
    dew = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dew)
    spots = [(430, 470, 13), (600, 430, 9), (660, 640, 12), (392, 640, 8),
             (560, 730, 10), (470, 800, 7), (690, 520, 7), (350, 560, 6)]
    for (x, y, r) in spots:
        dd.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 70))
        dd.ellipse([x - r * 0.45, y - r * 0.55, x + r * 0.1, y - r * 0.05],
                   fill=(255, 255, 255, 200))
    dew = dew.filter(ImageFilter.GaussianBlur(1.2))
    img.paste(Image.alpha_composite(img.convert("RGBA"), dew).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)

    # --- calyx: pointed green leaves fanning from the top ---
    leaf_green = (34, 128, 52)
    leaf_light = (74, 178, 84)
    leaves = [
        [(512, 306), (408, 262), (466, 302)],
        [(512, 306), (446, 236), (510, 292)],
        [(512, 306), (512, 224), (560, 292)],
        [(512, 306), (578, 240), (544, 302)],
        [(512, 306), (618, 266), (560, 306)],
    ]
    for leaf in leaves:
        d.polygon(leaf, fill=leaf_green)
    d.polygon([(512, 306), (452, 244), (512, 292)], fill=leaf_light)
    # centre knot
    d.ellipse([498, 288, 526, 314], fill=(26, 104, 44))
    # stem
    d.rounded_rectangle([503, 196, 521, 296], radius=8, fill=(52, 138, 62))
    d.line([(508, 200), (508, 292)], fill=(96, 196, 104), width=3)

    # --- vignette: darken the corners ---
    vig = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vig)
    vd.ellipse([-260, -260, W + 260, H + 260], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(180))
    black = Image.new("RGB", (W, H), (6, 8, 12))
    img = Image.composite(img, black, vig)

    img.save(OUT, "PNG")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
