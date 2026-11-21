"""Umbra theme art: eclipse-themed minimal wallpapers + plymouth unlock logo.
usage: gen_umbra.py OUTDIR [scale]
"""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUTDIR = sys.argv[1]
SC = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
W, H = int(3840 * SC), int(2400 * SC)
FONT = "/usr/share/fonts/TTF/DejaVuSans-ExtraLight.ttf"
SS = 3

BASE = np.array([0.024, 0.028, 0.042], np.float32)
DISC = np.array([0.010, 0.011, 0.016], np.float32)
SILVER = np.array([0.80, 0.85, 0.93], np.float32)
ICE = np.array([0.62, 0.76, 1.0], np.float32)
LIGHT = np.array([0.90, 0.94, 1.0], np.float32)

Y, X = np.mgrid[0:H, 0:W].astype(np.float32)


def c(v, col):
    return v[..., None] * col


def ring_noise(theta, seed, kmax=90, smooth=1.1):
    rng = np.random.default_rng(seed)
    n = np.zeros_like(theta)
    for k in range(1, kmax):
        n += rng.normal() / k ** smooth * np.sin(k * theta + rng.uniform(0, 6.283))
    return (n - n.min()) / (n.max() - n.min())


def canvas(cx, cy, spread=0.3, amt=0.045):
    r = np.hypot((X - cx) / W, (Y - cy) / H)
    rv = np.hypot((X - W / 2) / W, (Y - H / 2) / H)
    img = BASE + c(np.exp(-(r / spread) ** 2) * amt, np.array([0.35, 0.5, 0.85], np.float32))
    return img * (1 - 0.5 * rv ** 2)[..., None]


def eclipse(img, cx, cy, R, seed, corona=1.0, crescent=None, diamond=None, rim=0.5):
    """Dark disc with a streaky corona. crescent=(dx,dy) lights one edge; diamond=angle adds a bead."""
    dx, dy = X - cx, Y - cy
    r = np.hypot(dx, dy)
    th = np.arctan2(dy, dx)
    out = np.clip(r - R, 0, None)
    streak = ring_noise(th, seed)
    fine = ring_noise(th, seed + 1, 300, 0.7)
    L = R * (0.10 + 0.35 * streak ** 1.5) * (0.8 + 0.4 * fine)
    halo = (np.exp(-out / L) * 0.55 + np.exp(-out / (R * 0.9)) * 0.12) * corona
    inside = np.clip(R - r + 1, 0, 1)
    img += c(halo * (1 - inside), ICE * 0.5 + SILVER * 0.15)
    img[:] = img * (1 - inside[..., None]) + c(inside, DISC)
    img += c(np.exp(-((r - R) / (2.2 * SC)) ** 2) * rim, SILVER)
    if crescent is not None:
        ox, oy = crescent
        r2 = np.hypot(dx + ox, dy + oy)
        cres = (r < R) * (r2 > R)
        cres = cres.astype(np.float32) * np.clip((r2 - R) / 2.0, 0, 1)
        img += c(cres * 0.95, LIGHT)
        side = np.clip(np.cos(th - np.arctan2(-oy, -ox)), 0, 1) ** 2
        img += c((np.exp(-out / (R * 0.06)) * side * 0.6 + np.exp(-out / (R * 0.4)) * side * 0.15) * (1 - inside), ICE)
    if diamond is not None:
        bx, by = cx + R * np.cos(diamond), cy + R * np.sin(diamond)
        d = np.hypot(X - bx, Y - by)
        img += c(np.exp(-(d / (10 * SC)) ** 2) * 1.2 + np.exp(-d / (70 * SC)) * 0.35 + np.exp(-d / (400 * SC)) * 0.08, LIGHT)
        # faint horizontal flare
        img += c(np.exp(-np.abs(Y - by) / (2.5 * SC)) * np.exp(-np.abs(X - bx) / (380 * SC)) * 0.15, ICE)


def wordmark(img, text, x, y, size=46, track=34, align="center", alpha=0.45):
    size, track = size * SC, track * SC
    font = ImageFont.truetype(FONT, int(size * SS))
    tr = track * SS
    widths = [font.getlength(ch) for ch in text]
    tw = int(sum(widths) + tr * (len(text) - 1))
    tl = Image.new("L", (tw + 20 * SS, int(size * 1.7 * SS)), 0)
    d = ImageDraw.Draw(tl)
    px = 10 * SS
    for ch, w in zip(text, widths):
        d.text((px, 0), ch, font=font, fill=255)
        px += w + tr
    tl = tl.resize((tl.width // SS, tl.height // SS), Image.LANCZOS)
    t = np.asarray(tl, np.float32) / 255
    if align == "center":
        x = x - t.shape[1] / 2
    ts = (slice(int(y), int(y) + t.shape[0]), slice(int(x), int(x) + t.shape[1]))
    img[ts] = img[ts] * (1 - t[..., None] * alpha) + t[..., None] * SILVER * alpha


def save(img, name, seed=0):
    rng = np.random.default_rng(seed)
    img = np.clip(img + rng.normal(0, 0.007, (H, W, 1)).astype(np.float32), 0, 1)
    Image.fromarray((img * 255 + 0.5).astype(np.uint8), "RGB").save(os.path.join(OUTDIR, name))


S = SC
# 01: the mark — thin ring, crescent of light, wordmark
cx, cy = W / 2, H * 0.45
img = canvas(cx, cy, 0.22)
eclipse(img, cx, cy, 270 * S, 1, corona=0.25, crescent=(16 * S, -10 * S), rim=0.12)
wordmark(img, "UMBRA", cx, cy + 420 * S)
save(img, "01-umbra.png", 1)

# 02: totality — centred black disc with a full streaky corona
cx, cy = W / 2, H / 2
img = canvas(cx, cy, 0.35, 0.03)
eclipse(img, cx, cy, 380 * S, 2, corona=1.0, rim=0.35)
save(img, "02-totality.png", 2)

# 03: diamond ring — corona with a single bead of light breaking through
cx, cy = W * 0.58, H * 0.44
img = canvas(cx, cy, 0.3, 0.03)
eclipse(img, cx, cy, 320 * S, 3, corona=0.7, rim=0.3, diamond=np.radians(-38))
save(img, "03-diamond-ring.png", 3)

# 04: horizon — huge disc rising from below, only its upper edge lit
cx, cy = W * 0.5, H * 1.62
img = canvas(W / 2, H, 0.45, 0.04)
eclipse(img, cx, cy, 2100 * S, 4, corona=0.55, crescent=(0, 26 * S), rim=0.25)
save(img, "04-horizon.png", 4)

# 05: phases — a row of five small eclipses, light sweeping across
cy = H * 0.5
img = canvas(W / 2, cy, 0.4, 0.025)
for i, off in enumerate([-22, -12, 0, 12, 22]):
    cx = W / 2 + (i - 2) * 520 * S
    if off == 0:
        eclipse(img, cx, cy, 150 * S, 10 + i, corona=0.9, rim=0.35)
    else:
        eclipse(img, cx, cy, 150 * S, 10 + i, corona=0.12, crescent=(off * S, 0), rim=0.1)
save(img, "05-phases.png", 5)

# 06: corner lockup — small eclipse and name, bottom left
cx, cy = 300 * S + 150 * S, H - 300 * S - 150 * S
img = canvas(W * 0.2, H * 0.8, 0.35, 0.035)
eclipse(img, cx, cy, 110 * S, 6, corona=0.3, crescent=(8 * S, -5 * S), rim=0.12)
wordmark(img, "UMBRA", cx + 220 * S, cy - 30 * S, size=40, track=28, align="left")
save(img, "06-umbra-corner.png", 6)
