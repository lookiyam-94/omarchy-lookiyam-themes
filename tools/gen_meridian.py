"""Meridian theme art: geometric triangle wallpapers with an apex point of light.
usage: gen_meridian.py OUTDIR [scale]
"""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUTDIR = sys.argv[1]
SC = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
W, H = int(3840 * SC), int(2400 * SC)
SS = 2
FONT = "/usr/share/fonts/TTF/DejaVuSans-ExtraLight.ttf"

BASE = np.array([0.030, 0.034, 0.042], np.float32)
SLATE = np.array([0.72, 0.77, 0.84], np.float32)
AZURE = np.array([0.49, 0.78, 1.0], np.float32)    # #7cc8ff
LIGHT = np.array([0.90, 0.96, 1.0], np.float32)


def canvas(cx, cy, spread=0.3, amt=0.04):
    Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.hypot((X - cx) / W, (Y - cy) / H)
    rv = np.hypot((X - W / 2) / W, (Y - H / 2) / H)
    img = BASE + (np.exp(-(r / spread) ** 2) * amt)[..., None] * np.array([0.35, 0.55, 0.85], np.float32)
    return img * (1 - 0.5 * rv ** 2)[..., None]


class Layer:
    """Supersampled grey (line art) + light (glowing) masks over the whole canvas."""
    def __init__(self):
        self.g = Image.new("L", (W * SS, H * SS), 0)
        self.b = Image.new("L", (W * SS, H * SS), 0)
        self.dg, self.db = ImageDraw.Draw(self.g), ImageDraw.Draw(self.b)

    @staticmethod
    def p(*pts):
        return [(x * SS, y * SS) for x, y in pts]

    def tri(self, cx, cy, R, width, light=False, fill=255):
        pts = [(cx + R * np.cos(a), cy + R * np.sin(a)) for a in np.radians([-90, 30, 150])]
        d = self.db if light else self.dg
        d.line(self.p(*pts, pts[0]), fill=fill, width=int(width * SS * SC), joint="curve")
        r = width * SC / 2
        for x, y in pts:
            d.ellipse(self.p((x - r, y - r), (x + r, y + r)), fill=fill)
        return pts

    def dot(self, x, y, r, light=True, fill=255):
        d = self.db if light else self.dg
        d.ellipse(self.p((x - r, y - r), (x + r, y + r)), fill=fill)

    def composite(self, img, grey_level=0.5, glow=0.35):
        g = np.asarray(self.g.resize((W, H), Image.LANCZOS), np.float32) / 255
        bi = self.b.resize((W, H), Image.LANCZOS)
        bl = np.asarray(bi, np.float32) / 255
        small = bi.resize((W // 4, H // 4), Image.BILINEAR)
        gl = np.asarray(bi.filter(ImageFilter.GaussianBlur(14 * SC)), np.float32) / 255 * 0.9
        gl += np.asarray(small.filter(ImageFilter.GaussianBlur(22 * SC)).resize((W, H), Image.BICUBIC), np.float32) / 255 * 1.6
        img += gl[..., None] * AZURE * glow
        img[:] = img * (1 - g[..., None]) + g[..., None] * SLATE * grey_level
        img[:] = img * (1 - bl[..., None]) + bl[..., None] * LIGHT


def beam(img, x, y0, y1, amt=0.5):
    """Thin vertical meridian line of light, fading away from its brightest point y0."""
    Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
    core = np.exp(-((X - x) / (1.6 * SC)) ** 2) + 0.25 * np.exp(-np.abs(X - x) / (30 * SC))
    span = np.clip((Y - min(y0, y1)) / max(1, abs(y1 - y0)), 0, 1)
    fade = np.exp(-np.abs(Y - y0) / (abs(y1 - y0) * 0.45 + 1)) * (span > 0) * (Y <= max(y0, y1))
    img += (core * fade * amt)[..., None] * AZURE


def wordmark(img, text, x, y, size=46, track=34, align="center", alpha=0.45):
    size, track = size * SC, track * SC
    font = ImageFont.truetype(FONT, int(size * 3))
    tr = track * 3
    widths = [font.getlength(ch) for ch in text]
    tl = Image.new("L", (int(sum(widths) + tr * (len(text) - 1)) + 60, int(size * 1.7 * 3)), 0)
    d = ImageDraw.Draw(tl)
    px = 30
    for ch, w in zip(text, widths):
        d.text((px, 0), ch, font=font, fill=255)
        px += w + tr
    tl = tl.resize((tl.width // 3, tl.height // 3), Image.LANCZOS)
    t = np.asarray(tl, np.float32) / 255
    if align == "center":
        x = x - t.shape[1] / 2
    ts = (slice(int(y), int(y) + t.shape[0]), slice(int(x), int(x) + t.shape[1]))
    img[ts] = img[ts] * (1 - t[..., None] * alpha) + t[..., None] * SLATE * alpha


def save(img, name, seed=0):
    rng = np.random.default_rng(seed)
    img = np.clip(img + rng.normal(0, 0.007, (H, W, 1)).astype(np.float32), 0, 1)
    Image.fromarray((img * 255 + 0.5).astype(np.uint8), "RGB").save(os.path.join(OUTDIR, name))


S = SC

# 01: the mark — triangle outline, point of light at the apex, wordmark
cx, cy = W / 2, H * 0.47
img = canvas(cx, cy)
L = Layer()
pts = L.tri(cx, cy, 280 * S, 14)
L.dot(*pts[0], 24 * S)
L.composite(img, 0.55)
wordmark(img, "MERIDIAN", cx, cy + 290 * S)
save(img, "01-meridian.png", 1)

# 02: zenith — thin triangle, light at the apex sends a meridian line up the sky
cx, cy = W / 2, H * 0.62
img = canvas(cx, H * 0.35, 0.35, 0.03)
L = Layer()
pts = L.tri(cx, cy, 520 * S, 5)
L.dot(*pts[0], 12 * S)
beam(img, pts[0][0], pts[0][1], 0, 0.55)
L.composite(img, 0.35, 0.4)
save(img, "02-zenith.png", 2)

# 03: nested — concentric triangles stepping down in brightness toward the centre light
cx, cy = W / 2, H * 0.5
img = canvas(cx, cy, 0.3, 0.035)
L = Layer()
for i, R in enumerate([700, 560, 430, 310, 200]):
    L.tri(cx, cy + 0 * S, R * S, 4, fill=int(255 * (0.35 + 0.15 * i)))
L.dot(cx, cy, 14 * S)
L.composite(img, 0.45, 0.45)
save(img, "03-nested.png", 3)

# 04: lattice — faint triangular grid of points, one of them lit
img = canvas(W * 0.64, H * 0.38, 0.3, 0.03)
L = Layer()
step = 170 * S
rows = int(H / (step * 0.866)) + 2
for j in range(rows):
    y = j * step * 0.866
    off = (j % 2) * step / 2
    for i in range(int(W / step) + 2):
        L.dot(i * step + off - step / 2, y, 3.2 * S, light=False, fill=150)
lx = round((W * 0.64 + step / 2) / step) * step - step / 2
lj = round(H * 0.38 / (step * 0.866))
ly = lj * step * 0.866
lx += (lj % 2) * step / 2
L.dot(lx, ly, 11 * S)
L.composite(img, 0.35, 0.55)
save(img, "04-lattice.png", 4)

# 05: peak — a huge triangle rising from the bottom edge, light at its summit
cx = W * 0.5
apex_y = H * 0.42
img = canvas(cx, apex_y, 0.35, 0.035)
L = Layer()
half = (H - apex_y) * 1.25
L.dg.line(L.p((cx - half, H + 20), (cx, apex_y), (cx + half, H + 20)), fill=210, width=int(6 * SS * S), joint="curve")
L.dot(cx, apex_y, 15 * S)
beam(img, cx, apex_y, 0, 0.3)
L.composite(img, 0.45, 0.5)
save(img, "05-peak.png", 5)

# 06: corner lockup — small mark with the name beside it, bottom left
cx, cy = 300 * S + 120 * S, H - 300 * S - 110 * S
img = canvas(W * 0.2, H * 0.8, 0.35, 0.035)
L = Layer()
pts = L.tri(cx, cy, 110 * S, 7)
L.dot(*pts[0], 11 * S)
L.composite(img, 0.55, 0.3)
wordmark(img, "MERIDIAN", cx + 190 * S, cy - 25 * S, size=40, track=26, align="left")
save(img, "06-meridian-corner.png", 6)
