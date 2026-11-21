"""Procedural Graphite Blue backgrounds: dark, foggy, cool-blue light."""
import sys
import numpy as np
from PIL import Image

W, H = 3840, 2400
SCALE = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
W, H = int(W * SCALE), int(H * SCALE)
OUT = sys.argv[1]

Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
T = Y / H  # 0 top .. 1 bottom
U = X / W

BASE = np.array([0.028, 0.032, 0.045], np.float32)
BLUE = np.array([0.44, 0.68, 1.0], np.float32)    # #71aeff
PALE = np.array([0.72, 0.82, 0.95], np.float32)
FOG = np.array([0.20, 0.25, 0.33], np.float32)


def up(a, w, h):
    im = Image.fromarray(np.ascontiguousarray(a, dtype=np.float32))
    return np.asarray(im.resize((w, h), Image.BICUBIC), dtype=np.float32)


def fbm(seed, cx, cy=None, octaves=5, w=W, h=H):
    cy = cy or cx
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for _ in range(octaves):
        gw = max(2, int(w / cx) + 2)
        gh = max(2, int(h / cy) + 2)
        out += amp * up(rng.random((gh, gw)), w, h)
        tot += amp
        amp *= 0.5
        cx, cy = max(cx / 2, 1), max(cy / 2, 1)
    out /= tot
    return (out - out.min()) / (out.max() - out.min() + 1e-6)


def noise1d(seed, cell, octaves=5):
    return fbm(seed, cell, 1, octaves, w=W, h=1)[0]


def blur(a, factor):
    h, w = a.shape[:2]
    if a.ndim == 3:
        return np.stack([blur(a[..., c], factor) for c in range(a.shape[2])], -1)
    small = up(a, max(2, int(w / factor)), max(2, int(h / factor)))
    return up(small, w, h)


def c(v, col):
    return v[..., None] * col


def finish(img, seed):
    rng = np.random.default_rng(seed + 999)
    r2 = ((U - 0.5) * 1.3) ** 2 + (T - 0.5) ** 2
    img = img * (1 - 0.55 * r2)[..., None]
    img = img + rng.normal(0, 0.008, (H, W, 1)).astype(np.float32)
    img = np.clip(img, 0, 1) ** (1 / 1.05)
    Image.fromarray((img * 255 + 0.5).astype(np.uint8), "RGB").save(OUT)


def sky(seed, horizon, glow=0.5, width=0.12):
    img = np.broadcast_to(BASE, (H, W, 3)).copy()
    clouds = fbm(seed, 900 * SCALE, 300 * SCALE)
    img += c(np.exp(-((T - horizon) / width) ** 2) * glow * (0.35 + 0.65 * clouds), BLUE * 0.22)
    img += c(clouds ** 2 * 0.07 * (T < horizon), FOG)
    return img


def layered_ridges(seed=7):
    img = sky(seed, 0.5, glow=0.7)
    for i in range(5):
        y0 = 0.44 + i * 0.1
        amp = 0.06 + 0.035 * i
        ridge = (y0 - amp * noise1d(seed + i, (500 - 60 * i) * SCALE)) * H
        mask = np.clip(Y - ridge[None, :] + 1, 0, 1)
        k = i / 4
        col = FOG * (0.42 * (1 - k) ** 1.6) + BASE * 0.4
        img = img * (1 - mask[..., None]) + c(mask, col)
        if i == 0:
            side = 0.3 + 0.7 * np.exp(-((U - 0.68) / 0.22) ** 2)
            img += c(np.exp(-np.clip(Y - ridge, 0, None) / (5 * SCALE)) * mask * side * 0.55, PALE)
        fog = np.exp(-((T - (y0 + 0.05)) / 0.045) ** 2) * (0.4 + 0.6 * fbm(seed + 20 + i, 700 * SCALE, 90 * SCALE))
        img += c(fog * (0.55 - 0.1 * i), FOG)
    finish(img, seed)


def still_lake(seed=8):
    th = 0.6
    s = sky(seed, th, glow=1.5, width=0.1)
    s += c(np.exp(-((T - th) / 0.006) ** 2) * 0.9 * np.exp(-((U - 0.55) / 0.35) ** 2), BLUE)
    shore = (th - 0.012 * noise1d(seed + 3, 300 * SCALE) * np.clip((0.4 - U[0]) / 0.4, 0, 1)) * H
    smask = ((Y > shore[None, :]) & (T < th)).astype(np.float32)
    s = s * (1 - 0.85 * smask[..., None])
    rows = np.clip((2 * th * H - Y).astype(int), 0, H - 1)
    wob = (np.sin(Y / (6 * SCALE) + fbm(seed + 5, 200 * SCALE, 30 * SCALE) * 8) * 6 * SCALE).astype(int)
    cols = np.clip(X.astype(int) + wob, 0, W - 1)
    refl = s[rows, cols]
    streak = fbm(seed + 6, 600 * SCALE, 5 * SCALE, 4)
    fall = np.exp(-np.clip(T - th, 0, None) / 0.22)
    water = refl * (0.35 + 1.1 * streak * fall)[..., None] + BASE * 0.5
    img = np.where((T > th)[..., None], water, s)
    finish(img, seed)


def halo(seed=9):
    tf = 0.8
    tex = fbm(seed, 260 * SCALE, octaves=6)
    wall = np.broadcast_to(BASE * 0.9, (H, W, 3)) + c(tex * 0.02, FOG)
    cx, cy, R = 0.6 * W, 0.44 * H, 0.23 * H
    d = np.abs(np.hypot(X - cx, Y - cy) - R)
    ring = np.exp(-(d / (2.5 * SCALE)) ** 2) * 0.95
    glow = np.exp(-d / (35 * SCALE)) * 0.3 + np.exp(-d / (260 * SCALE)) * 0.12
    wall = wall + c(ring, PALE) + c(glow, BLUE)
    wall = wall * (1 + 2.5 * glow)[..., None] * 0.9 + c(ring, PALE) * 0.1
    rows = np.clip((2 * tf * H - Y).astype(int), 0, H - 1)
    refl = blur(wall[rows, X.astype(int)], 10)
    floor_tex = fbm(seed + 2, 900 * SCALE, 60 * SCALE)
    floor = refl * (0.35 * np.exp(-(T - tf) / 0.15))[..., None] + c(0.5 + 0.5 * floor_tex, BASE * 0.7)
    img = np.where((T > tf)[..., None], floor, wall)
    img += c(np.exp(-((T - tf) * H / (2 * SCALE)) ** 2) * 0.06, FOG)
    finish(img, seed)


def night_stars(seed=10):
    img = np.broadcast_to(BASE * 0.8, (H, W, 3)).copy()
    img += c(np.exp(-((T - 0.78) / 0.18) ** 2) * 0.12, BLUE * 0.5)
    u = (X * 0.8 - Y * 0.6) / W
    band = np.exp(-((u - 0.25) / 0.09) ** 2) * fbm(seed, 300 * SCALE, octaves=6) ** 1.5
    img += c(band * 0.3, FOG + BLUE * 0.1)
    rng = np.random.default_rng(seed)
    n = int(3200 * SCALE ** 2)
    sx = rng.integers(2, W - 2, n)
    sy = rng.integers(2, H - 2, n)
    sb = np.minimum(rng.pareto(2.2, n) * 0.1 + 0.03, 0.5)
    near_band = np.exp(-(((sx * 0.8 - sy * 0.6) / W - 0.25) / 0.12) ** 2)
    sb *= 0.6 + 0.8 * near_band
    star = np.zeros((H, W), np.float32)
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            np.add.at(star, (sy + dy, sx + dx), sb * np.exp(-(dx * dx + dy * dy) / 1.2))
    img += c(np.clip(star, 0, 1.2) * np.clip((0.82 - T) / 0.2, 0, 1), PALE)
    ridge = (0.8 - 0.07 * noise1d(seed + 1, 1400 * SCALE, 3) - 0.04 * np.exp(-((U[0] - 0.7) / 0.25) ** 2)) * H
    mask = np.clip(Y - ridge[None, :] + 1, 0, 1)
    img = img * (1 - mask[..., None]) + c(mask, BASE * 0.35)
    rim = np.exp(-np.clip(Y - ridge, 0, None) / (4 * SCALE)) * mask * np.exp(-((U - 0.7) / 0.3) ** 2)
    img += c(rim * 0.5, PALE)
    finish(img, seed)


SCENES = {"07": layered_ridges, "08": still_lake, "09": halo, "10": night_stars}
SCENES[sys.argv[3]]()
