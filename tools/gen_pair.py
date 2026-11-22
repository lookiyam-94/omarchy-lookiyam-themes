"""Strata (amber, horizontal layers) and Northline (mint, vertical lines) theme art.
usage: gen_pair.py strata|northline OUTDIR [scale]
"""
import math
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

THEME, OUTDIR = sys.argv[1], sys.argv[2]
SC = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
W, H = int(3840 * SC), int(2400 * SC)
SS = 2
FONT = "/usr/share/fonts/TTF/DejaVuSans-ExtraLight.ttf"

PAL = {
    "strata": dict(base=(0.036, 0.032, 0.028), grey=(0.84, 0.80, 0.74),
                   accent=(0.95, 0.68, 0.40), light=(1.0, 0.93, 0.82), tint=(0.85, 0.6, 0.35)),
    "northline": dict(base=(0.022, 0.030, 0.036), grey=(0.78, 0.85, 0.88),
                      accent=(0.43, 0.91, 0.72), light=(0.88, 1.0, 0.95), tint=(0.3, 0.75, 0.6)),
    "carbon": dict(base=(0.068, 0.073, 0.078), grey=(0.72, 0.76, 0.79),
                   accent=(1.0, 0.525, 0.102), light=(1.0, 0.65, 0.25), tint=(0.60, 0.25, 0.04), glow=1.5),
    "graphite": dict(base=(0.028, 0.032, 0.045), grey=(0.80, 0.84, 0.90),
                     accent=(0.44, 0.68, 1.0), light=(0.85, 0.92, 1.0), tint=(0.35, 0.5, 0.8)),
}[THEME]
BASE, GREY, ACCENT, LIGHT, TINT = (np.array(PAL[k], np.float32) for k in ("base", "grey", "accent", "light", "tint"))
Y, X = np.mgrid[0:H, 0:W].astype(np.float32)


def c(v, col):
    return v[..., None] * col


def up(a, w, h):
    return np.asarray(Image.fromarray(np.ascontiguousarray(a, np.float32)).resize((w, h), Image.BICUBIC), np.float32)


def fbm(seed, cx, cy, octaves=5, w=W, h=H):
    rng = np.random.default_rng(seed)
    out, amp, tot = np.zeros((h, w), np.float32), 1.0, 0.0
    for _ in range(octaves):
        out += amp * up(rng.random((max(2, int(h / cy) + 2), max(2, int(w / cx) + 2))), w, h)
        tot += amp
        amp *= 0.5
        cx, cy = max(cx / 2, 1), max(cy / 2, 1)
    out /= tot
    return (out - out.min()) / (out.max() - out.min() + 1e-6)


def noise1d(seed, cell, octaves=4):
    return fbm(seed, cell, 1, octaves, w=W, h=1)[0]


def canvas(cx, cy, spread=0.3, amt=0.04):
    r = np.hypot((X - cx) / W, (Y - cy) / H)
    rv = np.hypot((X - W / 2) / W, (Y - H / 2) / H)
    img = BASE + c(np.exp(-(r / spread) ** 2) * amt, TINT)
    return img * (1 - 0.5 * rv ** 2)[..., None]


class Layer:
    def __init__(self):
        self.g = Image.new("L", (W * SS, H * SS), 0)
        self.b = Image.new("L", (W * SS, H * SS), 0)
        self.dg, self.db = ImageDraw.Draw(self.g), ImageDraw.Draw(self.b)

    def d(self, light):
        return self.db if light else self.dg

    def bar(self, x0, y0, x1, y1, light=False, fill=255):
        r = min(abs(x1 - x0), abs(y1 - y0)) / 2
        self.d(light).rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], radius=r * SS, fill=fill)

    def rrect(self, x0, y0, x1, y1, rad, width, light=False, fill=255):
        self.d(light).rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], radius=rad * SS,
                                        outline=fill, width=max(1, int(width * SS)))

    def poly(self, pts, width, light=False, fill=255):
        self.d(light).line([(x * SS, y * SS) for x, y in pts], fill=fill, width=max(1, int(width * SS)), joint="curve")

    def ring(self, cx, cy, R, width, light=False, fill=255):
        self.d(light).ellipse([(cx - R) * SS, (cy - R) * SS, (cx + R) * SS, (cy + R) * SS], outline=fill,
                              width=max(1, int(width * SS)))

    def arc(self, cx, cy, R, start, end, width, light=False, fill=255):
        self.d(light).arc([(cx - R) * SS, (cy - R) * SS, (cx + R) * SS, (cy + R) * SS], start, end,
                          fill=fill, width=max(1, int(width * SS)))

    def dot(self, x, y, r, light=True, fill=255):
        self.d(light).ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=fill)

    def composite(self, img, grey_level=0.5, glow=0.4):
        g = np.asarray(self.g.resize((W, H), Image.LANCZOS), np.float32) / 255
        bi = self.b.resize((W, H), Image.LANCZOS)
        bl = np.asarray(bi, np.float32) / 255
        small = bi.resize((W // 4, H // 4), Image.BILINEAR)
        gl = np.asarray(bi.filter(ImageFilter.GaussianBlur(14 * SC)), np.float32) / 255 * 0.9
        gl += np.asarray(small.filter(ImageFilter.GaussianBlur(22 * SC)).resize((W, H), Image.BICUBIC), np.float32) / 255 * 1.6
        img += c(gl, ACCENT) * glow * PAL.get("glow", 1.0)
        img[:] = img * (1 - g[..., None]) + c(g, GREY) * grey_level
        img[:] = img * (1 - bl[..., None]) + c(bl, LIGHT)


def wordmark(img, text, x, y, size=46, track=34, align="center", alpha=0.45):
    size, track = size * SC, track * SC
    font = ImageFont.truetype(FONT, max(8, int(size * 3)))
    widths = [font.getlength(ch) for ch in text]
    tl = Image.new("L", (int(sum(widths) + track * 3 * (len(text) - 1)) + 60, int(size * 1.7 * 3)), 0)
    d = ImageDraw.Draw(tl)
    px = 30
    for ch, w in zip(text, widths):
        d.text((px, 0), ch, font=font, fill=255)
        px += w + track * 3
    tl = tl.resize((tl.width // 3, tl.height // 3), Image.LANCZOS)
    t = np.asarray(tl, np.float32) / 255
    if align == "center":
        x = x - t.shape[1] / 2
    ts = (slice(int(y), int(y) + t.shape[0]), slice(int(x), int(x) + t.shape[1]))
    img[ts] = img[ts] * (1 - t[..., None] * alpha) + c(t, GREY) * alpha


def save(img, name, seed=0):
    rng = np.random.default_rng(seed)
    img = np.clip(img + rng.normal(0, 0.007, (H, W, 1)).astype(np.float32), 0, 1)
    Image.fromarray((img * 255 + 0.5).astype(np.uint8), "RGB").save(os.path.join(OUTDIR, name))


S = SC


def strata_mark(L, cx, cy, k=1.0, grey_fill=255):
    h, gap = 14 * S * k, 64 * S * k
    for i, half in enumerate([150, 220, 290]):
        y = cy - gap + i * gap
        L.bar(cx - half * S * k, y - h / 2, cx + half * S * k, y + h / 2, light=(i == 2), fill=grey_fill if i < 2 else 255)


def strata():
    # 01 mark
    cx, cy = W / 2, H * 0.45
    img = canvas(cx, cy)
    L = Layer(); strata_mark(L, cx, cy); L.composite(img, 0.55)
    wordmark(img, "STRATA", cx, cy + 190 * S)
    save(img, "01-strata.png", 1)

    # 02 sediment: full-width contour lines like a rock cross-section, one seam lit
    img = canvas(W * 0.5, H * 0.58, 0.4, 0.03)
    L = Layer()
    xs = np.linspace(-10, W + 10, 500)
    n = len(range(0, 22))
    for i in range(n):
        y0 = H * (0.22 + i * 0.03)
        wav = noise1d(100, 1600 * S, 3) * 120 * S + noise1d(200 + i, 500 * S, 3) * 22 * S
        ys = np.interp(xs, np.arange(W), y0 + wav)
        lit = i == 13
        L.poly(list(zip(xs, ys)), 5 if lit else 2.2, light=lit, fill=255 if lit else int(70 + 60 * math.sin(i * 0.5) ** 2))
    L.composite(img, 0.5, 0.45)
    save(img, "02-sediment.png", 2)

    # 03 stack: a tall centred stack of thin bars, widening downward, lowest lit
    cx = W / 2
    img = canvas(cx, H * 0.7, 0.32, 0.04)
    L = Layer()
    for i in range(11):
        half = (90 + i * 62) * S
        y = H * 0.3 + i * 62 * S
        L.bar(cx - half, y - 4 * S, cx + half, y + 4 * S, light=(i == 10), fill=int(60 + i * 14))
    L.composite(img, 0.6, 0.45)
    save(img, "03-stack.png", 3)

    # 04 dusk: flat bands of land under a warm horizon, a single lit seam at the horizon
    hz = H * 0.56
    img = canvas(W / 2, hz, 0.25, 0.03)
    img += c(np.exp(-((Y - hz) / (H * 0.08)) ** 2) * 0.10, TINT)
    for i, (top, shade) in enumerate([(0.0, 0.020), (0.07, 0.016), (0.16, 0.012), (0.28, 0.008)]):
        yb = hz + top * H + noise1d(40 + i, 1800 * S, 2) * 18 * S * (i + 1)
        m = np.clip(Y - yb[None, :] + 1, 0, 1)
        img[:] = img * (1 - m[..., None]) + c(m, np.array([shade * 1.2, shade, shade * 0.85], np.float32) * 1.4)
        img += c(np.exp(-np.clip(Y - yb, 0, None) / (3 * S)) * m * (0.12 / (i + 1)), GREY)
    L = Layer(); L.bar(W * 0.08, hz - 2.5 * S, W * 0.92, hz + 2.5 * S, light=True); L.composite(img, 0.5, 0.35)
    save(img, "04-dusk.png", 4)

    # 05 corner lockup
    cx, cy = 300 * S + 150 * S, H - 300 * S - 70 * S
    img = canvas(W * 0.2, H * 0.8, 0.35, 0.035)
    L = Layer(); strata_mark(L, cx, cy, 0.5); L.composite(img, 0.55, 0.3)
    wordmark(img, "STRATA", cx + 200 * S, cy - 25 * S, size=40, track=26, align="left")
    save(img, "05-strata-corner.png", 5)


def north_mark(L, cx, cy, k=1.0, w=8):
    half, lw = 130 * S * k, w * S * k
    L.rrect(cx - half, cy - half, cx + half, cy + half, 36 * S * k, lw)
    lx = cx + 30 * S * k
    L.bar(lx - lw / 2, cy - half - 40 * S * k, lx + lw / 2, cy + half + 40 * S * k, light=True)


def northline():
    # 01 centred mark
    cx, cy = W / 2, H * 0.45
    img = canvas(cx, cy)
    L = Layer(); north_mark(L, cx, cy, 1.6, 7); L.composite(img, 0.55, 0.35)
    wordmark(img, "NORTHLINE", cx, cy + 340 * S)
    save(img, "01-northline.png", 1)

    # 02 corner lockup (the original)
    cx, cy = 300 * S + 210 * S, H - 300 * S - 210 * S
    img = canvas(W * 0.25, H * 0.75, 0.35, 0.035)
    L = Layer(); north_mark(L, cx, cy); L.composite(img, 0.5, 0.3)
    wordmark(img, "NORTHLINE", cx + 200 * S, cy - 30 * S, size=40, track=26, align="left")
    save(img, "02-northline-corner.png", 2)

    # 03 aurora: a quiet vertical curtain of light above a dark horizon
    hz = H * 0.8
    img = canvas(W * 0.55, H * 0.5, 0.4, 0.02)
    u = (X - W * 0.55) / W
    sway = (fbm(8, 1200 * S, 4000 * S, 3) - 0.5) * 0.25
    band = np.exp(-((u - sway) / 0.22) ** 2)
    rays = fbm(9, 18 * S, 900 * S, 4) ** 2
    vert = np.clip((hz - Y) / (H * 0.55), 0, 1) ** 0.6 * np.exp(-np.clip(hz - Y, 0, None) / (H * 0.45))
    img += c(band * rays * vert * 0.95, ACCENT * 0.8)
    img += c(band * vert * 0.1, ACCENT)
    ground = (Y > hz + noise1d(10, 1500 * S, 3)[None, :] * 25 * S).astype(np.float32)
    img[:] = img * (1 - ground[..., None]) + c(ground, BASE * 0.35)
    save(img, "03-aurora.png", 3)

    # 04 pillar: one vertical line of light, reflected in a dark floor
    lx, fl = W * 0.618, H * 0.82
    img = canvas(lx, H * 0.5, 0.3, 0.03)
    core = np.exp(-((X - lx) / (2.0 * S)) ** 2) * 0.95 + np.exp(-np.abs(X - lx) / (40 * S)) * 0.18 + np.exp(-np.abs(X - lx) / (380 * S)) * 0.05
    top_fade = np.clip(Y / (H * 0.25), 0, 1)
    img += c(core * top_fade * (Y < fl), LIGHT * 0.5 + ACCENT * 0.5)
    refl = core * np.exp(-(Y - fl) / (H * 0.07)) * 0.35 * (Y >= fl)
    img += c(refl, ACCENT)
    img += c(np.exp(-((Y - fl) / (1.5 * S)) ** 2) * np.exp(-np.abs(X - lx) / (900 * S)) * 0.25, ACCENT)
    save(img, "04-pillar.png", 4)

    # 05 true north: a thin ring with tick marks, light at north
    cx, cy, R = W / 2, H * 0.5, 420 * S
    img = canvas(cx, cy - R, 0.3, 0.04)
    L = Layer()
    L.ring(cx, cy, R, 3)
    for k in range(72):
        a = math.radians(k * 5 - 90)
        ln = 34 if k % 18 == 0 else (16 if k % 2 == 0 else 8)
        if k == 0:
            continue
        x0, y0 = cx + (R - 6 * S) * math.cos(a), cy + (R - 6 * S) * math.sin(a)
        x1, y1 = cx + (R - (6 + ln) * S) * math.cos(a), cy + (R - (6 + ln) * S) * math.sin(a)
        L.poly([(x0, y0), (x1, y1)], 3 if k % 18 == 0 else 2, fill=200 if k % 18 == 0 else 110)
    L.bar(cx - 3.5 * S, cy - R - 60 * S, cx + 3.5 * S, cy - R + 70 * S, light=True)
    L.composite(img, 0.5, 0.45)
    save(img, "05-true-north.png", 5)

    # 06 meridians: evenly spaced faint vertical lines, one of them lit
    img = canvas(W * 0.5, H * 0.5, 0.45, 0.025)
    L = Layer()
    step = 240 * S
    n = int(W / step) + 1
    off = (W - (n - 1) * step) / 2
    for i in range(n):
        x = off + i * step
        lit = i == n // 2 + 2
        L.bar(x - (3 if lit else 1.2) * S, -10, x + (3 if lit else 1.2) * S, H + 10, light=lit, fill=255 if lit else 70)
    L.composite(img, 0.5, 0.35)
    save(img, "06-meridians.png", 6)


def g_mark(L, cx, cy, R, stroke, gap=25, dot=True, bar=True):
    L.arc(cx, cy, R, gap, 360 - gap, stroke)
    if bar:
        L.bar(cx, cy - stroke / 2, cx + R, cy + stroke / 2, light=True)
    if dot:
        L.dot(cx, cy, stroke * 1.6)


def hexagon(cx, cy, s):
    return [(cx + s * math.cos(math.radians(60 * k - 30)), cy + s * math.sin(math.radians(60 * k - 30))) for k in range(7)]


def graphite():
    # 16 corner lockup
    cx, cy = 300 * S + 130 * S, H - 300 * S - 130 * S
    img = canvas(W * 0.2, H * 0.8, 0.35, 0.035)
    L = Layer(); g_mark(L, cx, cy, 110 * S, 6 * S); L.composite(img, 0.55, 0.3)
    wordmark(img, "GRAPHITE", cx + 190 * S, cy - 25 * S, size=40, track=26, align="left")
    save(img, "16-graphite-corner.png", 16)

    # 17 graphene: faint honeycomb lattice, one cell lit
    s = 120 * S
    lit = (W * 0.62, H * 0.42)
    img = canvas(*lit, 0.3, 0.035)
    L = Layer()
    dx, dy = s * math.sqrt(3), s * 1.5
    best, bd = None, 1e18
    for j in range(-1, int(H / dy) + 2):
        for i in range(-1, int(W / dx) + 2):
            hx, hy = i * dx + (j % 2) * dx / 2, j * dy
            L.poly(hexagon(hx, hy, s), 1.6 * S, fill=80)
            d = (hx - lit[0]) ** 2 + (hy - lit[1]) ** 2
            if d < bd:
                best, bd = (hx, hy), d
    L.poly(hexagon(*best, s), 4.5 * S, light=True)
    L.composite(img, 0.45, 0.45)
    save(img, "17-graphene.png", 17)

    # 18 arc: the G ring at huge scale, bleeding off the left edge, bar of light through the gap
    cx, cy, R = W * 0.28, H * 0.5, H * 0.62
    img = canvas(W * 0.6, cy, 0.3, 0.035)
    L = Layer()
    L.arc(cx, cy, R, 18, 342, 5 * S, fill=170)
    L.bar(cx, cy - 3.5 * S, cx + R * 1.08, cy + 3.5 * S, light=True)
    L.dot(cx, cy, 12 * S)
    L.composite(img, 0.45, 0.45)
    save(img, "18-arc.png", 18)

    # 19 orbits: concentric open rings sharing the gap, a light bar from the centre out
    cx, cy = W / 2, H / 2
    img = canvas(cx, cy, 0.3, 0.04)
    L = Layer()
    for i, R in enumerate([140, 260, 380, 500, 620]):
        L.arc(cx, cy, R * S, 22 - i * 2, 338 + i * 2, 3.2 * S, fill=int(200 - i * 28))
    L.bar(cx, cy - 3 * S, cx + 700 * S, cy + 3 * S, light=True)
    L.dot(cx, cy, 10 * S)
    L.composite(img, 0.5, 0.45)
    save(img, "19-orbits.png", 19)

    # 20 carbon: a single hexagon outline with one vertex glowing
    cx, cy, s = W / 2, H * 0.47, 300 * S
    pts = hexagon(cx, cy, s)
    img = canvas(*pts[5], 0.25, 0.04)
    L = Layer()
    L.poly(pts, 10 * S, fill=230)
    L.dot(*pts[5], 20 * S)
    L.composite(img, 0.5, 0.4)
    wordmark(img, "GRAPHITE", cx, cy + s + 150 * S)
    save(img, "20-carbon.png", 20)


def carbon_mark(L, cx, cy, s, stroke):
    pts = hexagon(cx, cy, s)
    L.poly(pts, stroke, fill=230)
    L.dot(*pts[5], stroke * 2)
    return pts


def carbon():
    # 01 the mark: hexagon, top vertex glowing, wordmark
    cx, cy, s = W / 2, H * 0.47, 300 * S
    img = canvas(cx, cy - s, 0.25, 0.04)
    L = Layer(); carbon_mark(L, cx, cy, s, 10 * S); L.composite(img, 0.5, 0.4)
    wordmark(img, "CARBON", cx, cy + s + 150 * S)
    save(img, "01-carbon.png", 1)

    # 02 corner lockup
    cx, cy = 300 * S + 120 * S, H - 300 * S - 110 * S
    img = canvas(W * 0.2, H * 0.8, 0.35, 0.035)
    L = Layer(); carbon_mark(L, cx, cy, 105 * S, 6 * S); L.composite(img, 0.55, 0.3)
    wordmark(img, "CARBON", cx + 190 * S, cy - 25 * S, size=40, track=26, align="left")
    save(img, "02-carbon-corner.png", 2)

    # 03 lattice: honeycomb, one atom (vertex) lit with its three bonds glowing faintly
    s = 120 * S
    target = (W * 0.6, H * 0.4)
    img = canvas(*target, 0.3, 0.035)
    L = Layer()
    dx, dy = s * math.sqrt(3), s * 1.5
    best, bd = None, 1e18
    for j in range(-1, int(H / dy) + 2):
        for i in range(-1, int(W / dx) + 2):
            hx, hy = i * dx + (j % 2) * dx / 2, j * dy
            pts = hexagon(hx, hy, s)
            L.poly(pts, 1.6 * S, fill=80)
            d = (pts[5][0] - target[0]) ** 2 + (pts[5][1] - target[1]) ** 2
            if d < bd:
                best, bd = pts, d
    v = best[5]
    for q in (best[4], best[0], (v[0], v[1] - s)):
        L.poly([v, q], 3 * S, light=True, fill=150)
    L.dot(*v, 11 * S)
    L.composite(img, 0.45, 0.5)
    save(img, "03-lattice.png", 3)

    # 04 molecule: three fused hexagons, one vertex lit
    s = 230 * S
    cx, cy = W / 2, H * 0.5
    dx = s * math.sqrt(3)
    img = canvas(cx, cy, 0.3, 0.035)
    L = Layer()
    centres = [(cx - dx, cy), (cx, cy), (cx + dx, cy)]
    for hx, hy in centres:
        L.poly(hexagon(hx, hy, s), 6 * S, fill=200)
    lit = hexagon(*centres[2], s)[0]
    L.dot(*lit, 16 * S)
    L.composite(img, 0.45, 0.45)
    save(img, "04-molecule.png", 4)

    # 05 facet: a huge hexagon cropped by the bottom-right corner, one vertex lit
    cx, cy, s = W * 0.86, H * 0.98, H * 0.62
    pts = hexagon(cx, cy, s)
    img = canvas(*pts[4], 0.3, 0.045)
    L = Layer()
    L.poly(pts, 5 * S, fill=180)
    L.dot(*pts[4], 16 * S)
    L.composite(img, 0.45, 0.5)
    save(img, "05-facet.png", 5)

    # 06 spiral: nested hexagons, each smaller and turned a little, glowing vertex at the core
    cx, cy = W / 2, H / 2
    img = canvas(cx, cy, 0.3, 0.04)
    L = Layer()
    s, rot = 760 * S, 0.0
    last = None
    for i in range(9):
        pts = [(cx + s * math.cos(math.radians(60 * k - 30 + rot)), cy + s * math.sin(math.radians(60 * k - 30 + rot))) for k in range(7)]
        L.poly(pts, 3 * S, fill=int(70 + i * 20))
        last = pts
        s *= 0.8
        rot += 9
    L.dot(*last[5], 12 * S)
    L.composite(img, 0.5, 0.45)
    save(img, "06-spiral.png", 6)


{"strata": strata, "northline": northline, "graphite": graphite, "carbon": carbon}[THEME]()
