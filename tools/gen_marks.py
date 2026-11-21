"""More minimal Graphite Blue wallpapers with invented marks + wordmarks.
usage: gen_marks.py OUT SCENE   (SCENE: strata | umbra | meridian | northline)
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT, SCENE = sys.argv[1], sys.argv[2]
W, H = 3840, 2400
SS = 3
FONT = "/usr/share/fonts/TTF/DejaVuSans-ExtraLight.ttf"
BASE = np.array([0.028, 0.032, 0.045], np.float32)
PALE = np.array([0.80, 0.84, 0.90], np.float32)
BLUE = np.array([0.44, 0.68, 1.0], np.float32)
LIGHT = np.array([0.85, 0.92, 1.0], np.float32)


def canvas(cx, cy, spread=0.28):
    Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.hypot((X - cx) / W, (Y - cy) / H)
    rv = np.hypot((X - W / 2) / W, (Y - H / 2) / H)
    img = BASE + (np.exp(-(r / spread) ** 2) * 0.05)[..., None] * np.array([0.35, 0.5, 0.8], np.float32)
    return img * (1 - 0.5 * rv ** 2)[..., None]


def layers(box):
    S = box * SS
    g, b = Image.new("L", (S, S), 0), Image.new("L", (S, S), 0)
    return S, g, b, ImageDraw.Draw(g), ImageDraw.Draw(b)


def place(img, g, b, box, cx, cy, grey_level=0.55, glow_amt=0.35):
    g = np.asarray(g.resize((box, box), Image.LANCZOS), np.float32) / 255
    bi = b.resize((box, box), Image.LANCZOS)
    bl = np.asarray(bi, np.float32) / 255
    glow = np.asarray(bi.filter(ImageFilter.GaussianBlur(16)), np.float32) / 255 * 0.9 \
        + np.asarray(bi.filter(ImageFilter.GaussianBlur(90)), np.float32) / 255 * 1.4
    ox, oy = int(cx - box / 2), int(cy - box / 2)
    sl = (slice(oy, oy + box), slice(ox, ox + box))
    img[sl] += glow[..., None] * BLUE * glow_amt
    img[sl] = img[sl] * (1 - g[..., None]) + g[..., None] * PALE * grey_level
    img[sl] = img[sl] * (1 - bl[..., None]) + bl[..., None] * LIGHT


def wordmark(img, text, x, y, size=46, track=34, align="center", alpha=0.45):
    font = ImageFont.truetype(FONT, size * SS)
    tr = track * SS
    widths = [font.getlength(ch) for ch in text]
    tw = int(sum(widths) + tr * (len(text) - 1))
    tl = Image.new("L", (tw + 20 * SS, int(size * 1.7) * SS), 0)
    d = ImageDraw.Draw(tl)
    px = 10 * SS
    for ch, w in zip(text, widths):
        d.text((px, 0), ch, font=font, fill=255)
        px += w + tr
    tl = tl.resize((tl.width // SS, tl.height // SS), Image.LANCZOS)
    t = np.asarray(tl, np.float32) / 255
    if align == "center":
        x = int(x - t.shape[1] / 2)
    ts = (slice(int(y), int(y) + t.shape[0]), slice(int(x), int(x) + t.shape[1]))
    img[ts] = img[ts] * (1 - t[..., None] * alpha) + t[..., None] * PALE * alpha


def save(img):
    rng = np.random.default_rng(len(SCENE))
    img = np.clip(img + rng.normal(0, 0.007, (H, W, 1)).astype(np.float32), 0, 1)
    Image.fromarray((img * 255 + 0.5).astype(np.uint8), "RGB").save(OUT)


def strata():
    # three stacked bars, the lowest one is the light
    cx, cy, box = W / 2, H * 0.45, 900
    img = canvas(cx, cy)
    S, g, b, dg, db = layers(box)
    c, h, gap = S // 2, 14 * SS, 64 * SS
    for i, half in enumerate([150, 220, 290]):
        y = c - gap + i * gap
        rect = [c - half * SS, y - h // 2, c + half * SS, y + h // 2]
        (db if i == 2 else dg).rounded_rectangle(rect, radius=h // 2, fill=255)
    place(img, g, b, box, cx, cy)
    wordmark(img, "STRATA", cx, cy + 190)
    save(img)


def umbra():
    # eclipse: a faint ring with a thin crescent of light on its edge
    cx, cy, box = W / 2, H * 0.45, 1000
    img = canvas(cx, cy, 0.22)
    S, g, b, dg, db = layers(box)
    c, R = S // 2, 270 * SS
    dg.ellipse([c - R, c - R, c + R, c + R], outline=255, width=4 * SS)
    db.ellipse([c - R, c - R, c + R, c + R], fill=255)
    dx, dy = -16 * SS, 10 * SS
    db.ellipse([c - R + dx, c - R + dy, c + R + dx, c + R + dy], fill=0)
    place(img, g, b, box, cx, cy, grey_level=0.22, glow_amt=0.6)
    wordmark(img, "UMBRA", cx, cy + 420)
    save(img)


def meridian():
    # rounded triangle outline, a point of light at its apex
    cx, cy, box = W / 2, H * 0.45, 900
    img = canvas(cx, cy)
    S, g, b, dg, db = layers(box)
    c, R = S // 2, 280 * SS
    pts = [(c + R * np.cos(a), c + 40 * SS + R * np.sin(a)) for a in np.radians([-90, 30, 150])]
    dg.line(pts + [pts[0]], fill=255, width=14 * SS, joint="curve")
    for x, y in pts:
        dg.ellipse([x - 7 * SS, y - 7 * SS, x + 7 * SS, y + 7 * SS], fill=255)
    ax, ay = pts[0]
    d = 24 * SS
    db.ellipse([ax - d, ay - d, ax + d, ay + d], fill=255)
    place(img, g, b, box, cx, cy)
    wordmark(img, "MERIDIAN", cx, cy + 330)
    save(img)


def northline():
    # corner lockup: rounded square split by a vertical line of light, name beside it
    box = 420
    cx, cy = 300 + box / 2, H - 300 - box / 2
    img = canvas(W * 0.25, H * 0.75, 0.35)
    S, g, b, dg, db = layers(box)
    c, half, w = S // 2, 130 * SS, 8 * SS
    dg.rounded_rectangle([c - half, c - half, c + half, c + half], radius=36 * SS, outline=255, width=w)
    db.rounded_rectangle([c + 30 * SS - w // 2, c - half - 40 * SS, c + 30 * SS + w // 2, c + half + 40 * SS],
                         radius=w // 2, fill=255)
    place(img, g, b, box, cx, cy, glow_amt=0.3)
    wordmark(img, "NORTHLINE", cx + 200, cy - 30, size=40, track=26, align="left")
    save(img)


{"strata": strata, "umbra": umbra, "meridian": meridian, "northline": northline}[SCENE]()
