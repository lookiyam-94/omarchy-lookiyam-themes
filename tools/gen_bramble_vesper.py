"""Bramble and Vesper: SVG marks, six wallpapers each, unlock image and lock card.

    uv run --with numpy --with pillow python tools/gen_bramble_vesper.py            # full size
    uv run --with numpy --with pillow python tools/gen_bramble_vesper.py 0.25 /tmp/x  # quarter-size previews

Each mark is written as themes/<theme>/logo.svg. It has two groups: "line"
(thin pale strokes) and "light" (the theme's single point of light). The
groups are rendered separately with rsvg-convert so the light can glow, like
the Graphite mark. 02-<theme>-nature.png is a photograph and is left alone.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1] / "themes"
SCALE = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
PREVIEW_DIR = Path(sys.argv[2]) if len(sys.argv) > 2 else None
W, H = int(3840 * SCALE), int(2400 * SCALE)
FONT = "/usr/share/fonts/TTF/DejaVuSans-ExtraLight.ttf"

Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
T, U = Y / H, X / W


def hexf(h):
    return np.array([int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)], np.float32)


THEMES = {
    "bramble": {
        "base": "#140d12", "accent": "#c791a9", "pale": "#eadbe2",
        "card": "#0a0609", "text": "#e6dde1", "placeholder": "#9a8a92",
        "error": "#e0868d", "seed": 30,
    },
    "vesper": {
        "base": "#100d15", "accent": "#b6a0d6", "pale": "#e6deef",
        "card": "#08060b", "text": "#e2dde9", "placeholder": "#938aa0",
        "error": "#d4868d", "seed": 40,
    },
}

# ---------------------------------------------------------------- marks (SVG)
# 300x300 canvas. Both marks are built so their outline box is centred on
# (150, 150): that is what makes them sit in the middle of the screen.

MARKS = {
    # An arching, thorned cane with one blackberry hanging from its tip.
    "bramble": {
        "line": """
    <path d="M66 262 C 62 160, 128 78, 190 92 C 228 101, 240 138, 232 172"/>
    <path d="M66 206 L 52 196"/>
    <path d="M82 148 L 70 134"/>
    <path d="M116 104 L 110 88"/>
    <path d="M166 88 L 168 72"/>
    <path d="M214 106 L 226 94"/>
    <path d="M70 232 C 92 212, 120 214, 132 230 C 112 248, 86 248, 70 232 Z"/>""",
        "light": """
    <circle cx="232" cy="192" r="7"/>
    <circle cx="220" cy="203" r="7"/>
    <circle cx="244" cy="203" r="7"/>
    <circle cx="232" cy="214" r="7"/>
    <circle cx="221" cy="226" r="6"/>
    <circle cx="243" cy="226" r="6"/>
    <circle cx="232" cy="237" r="5"/>""",
        "light_mode": "fill",
    },
    # The evening star above a sun half set behind the horizon.
    "vesper": {
        "line": """
    <path d="M62 190 A 88 88 0 0 1 238 190"/>
    <path d="M96 214 L 204 214"/>
    <path d="M124 236 L 176 236"/>""",
        "light": """
    <path d="M30 190 L 270 190"/>
    <circle cx="232" cy="72" r="8" class="fill"/>""",
        "light_mode": "stroke",
    },
}

STROKE = 4


def svg(name, line_col, light_col, only=None):
    m = MARKS[name]
    line = (f'<g fill="none" stroke="{line_col}" stroke-width="{STROKE}" '
            f'stroke-linecap="round" stroke-linejoin="round">{m["line"]}\n  </g>')
    if m["light_mode"] == "fill":
        light = f'<g fill="{light_col}">{m["light"]}\n  </g>'
    else:
        light = (f'<g fill="none" stroke="{light_col}" stroke-width="{STROKE + 1}" '
                 f'stroke-linecap="round">{m["light"]}\n  </g>')
    light = light.replace('class="fill"', f'fill="{light_col}" stroke="none"')
    dx, dy = OFFSETS.get(name, (0, 0))
    line = f'<g transform="translate({dx} {dy})">{line}</g>'
    light = f'<g transform="translate({dx} {dy})">{light}</g>'
    parts = {"line": line, "light": light}
    body = "\n  ".join(parts[k] for k in (only or ("line", "light")))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" '
            f'width="300" height="300">\n  <title>{name.title()}</title>\n  {body}\n</svg>\n')


OFFSETS = {}


def centre_marks():
    """Shift each mark so its outline box is centred in the 300x300 canvas."""
    for name in MARKS:
        a = render(svg(name, "#fff", "#fff"), 1200)
        x0, y0, x1, y1 = Image.fromarray((a > 0.02).astype(np.uint8) * 255).getbbox()
        OFFSETS[name] = (round(150 - (x0 + x1) / 8, 2), round(150 - (y0 + y1) / 8, 2))


def render(svg_text, size):
    """Alpha mask of an SVG at size x size pixels, 0..1."""
    with tempfile.TemporaryDirectory() as d:
        src, dst = os.path.join(d, "m.svg"), os.path.join(d, "m.png")
        Path(src).write_text(svg_text)
        subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size), "-o", dst, src], check=True)
        return np.asarray(Image.open(dst).convert("RGBA").getchannel("A"), np.float32) / 255


def masks(name, size):
    return (render(svg(name, "#fff", "#fff", ["line"]), size),
            render(svg(name, "#fff", "#fff", ["light"]), size))


def gblur(a, radius):
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(radius)), np.float32) / 255


# ---------------------------------------------------------------- painting

def c(v, col):
    return v[..., None] * col


def up(a, w, h):
    return np.asarray(Image.fromarray(np.ascontiguousarray(a, np.float32)).resize((w, h), Image.BICUBIC), np.float32)


def fbm(seed, cx, cy=None, octaves=5, w=None, h=None):
    w, h = w or W, h or H
    cy = cy or cx
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp = tot = 0.0
    amp = 1.0
    for _ in range(octaves):
        out += amp * up(rng.random((max(2, int(h / cy) + 2), max(2, int(w / cx) + 2))), w, h)
        tot += amp
        amp *= 0.5
        cx, cy = max(cx / 2, 1), max(cy / 2, 1)
    out /= tot
    return (out - out.min()) / (out.max() - out.min() + 1e-6)


def noise1d(seed, cell, octaves=4):
    return fbm(seed, cell, 1, octaves, w=W, h=1)[0]


def canvas(spec, cx=0.5, cy=0.5, spread=0.3, amt=0.045):
    base = hexf(spec["base"]) * 0.55
    r = np.hypot((X / W - cx), (Y / H - cy))
    return base + c(np.exp(-(r / spread) ** 2) * amt, hexf(spec["accent"]) * 0.6)


def finish(img, seed):
    rng = np.random.default_rng(seed + 999)
    r2 = ((U - 0.5) * 1.3) ** 2 + (T - 0.5) ** 2
    img = img * (1 - 0.5 * r2)[..., None]
    img = img + rng.normal(0, 0.007, (H, W, 1)).astype(np.float32)
    img = np.clip(img, 0, 1)
    return Image.fromarray((img * 255 + 0.5).astype(np.uint8), "RGB")


def place_mark(img, spec, name, cx, cy, size, grey=0.6, glow=1.0):
    """Composite the mark with its outline box centred on (cx, cy)."""
    size = max(8, int(size))
    line, light = masks(name, size)
    box = Image.fromarray(((line + light) > 0.02).astype(np.uint8) * 255).getbbox()
    ox = int(cx - (box[0] + box[2]) / 2)
    oy = int(cy - (box[1] + box[3]) / 2)
    pale, acc = hexf(spec["pale"]), hexf(spec["accent"])
    bright = np.clip(acc * 1.15 + 0.08, 0, 1)
    halo = gblur(light, size * 0.02) * 0.8 + gblur(light, size * 0.1) * 1.3
    ys = slice(max(oy, 0), min(oy + size, H))
    xs = slice(max(ox, 0), min(ox + size, W))
    my = slice(ys.start - oy, ys.stop - oy)
    mx = slice(xs.start - ox, xs.stop - ox)
    sl = img[ys, xs]
    sl += c(halo[my, mx], acc) * 0.35 * glow
    l, g = light[my, mx][..., None], line[my, mx][..., None]
    sl[:] = sl * (1 - g) + g * pale * grey
    sl[:] = sl * (1 - l) + l * bright
    place_mark.bottom = oy + box[3]
    return img


def wordmark(img, spec, text, x, y, size, track, align="center", alpha=0.5):
    font = ImageFont.truetype(FONT, max(6, int(size * SCALE)))
    track = track * SCALE
    widths = [font.getlength(ch) for ch in text]
    tw = int(sum(widths) + track * (len(text) - 1)) + 4
    layer = Image.new("L", (tw, int(size * SCALE * 1.4)), 0)
    d = ImageDraw.Draw(layer)
    px = 0.0
    for ch, w in zip(text, widths):
        d.text((px, 0), ch, font=font, fill=255)
        px += w + track
    t = np.asarray(layer, np.float32) / 255
    x0 = int(x - tw / 2) if align == "center" else int(x)
    y0 = int(y)
    sl = img[y0:y0 + t.shape[0], x0:x0 + t.shape[1]]
    a = t[:sl.shape[0], :sl.shape[1], None] * alpha
    sl[:] = sl * (1 - a) + a * hexf(spec["pale"])
    return img


# ---------------------------------------------------------------- wallpapers

def w_mark(name, spec):
    """01: the mark alone in the middle of the screen, name below."""
    img = canvas(spec, 0.5, 0.5, 0.26, 0.05)
    size = 760 * SCALE
    img = place_mark(img, spec, name, W / 2, H / 2, size)
    wordmark(img, spec, name.upper(), W / 2, place_mark.bottom + 150 * SCALE, 46, 34, alpha=0.45)
    return finish(img, spec["seed"] + 1)


def w_corner(name, spec):
    """Small lockup in the lower-left corner, like Graphite's corner."""
    img = canvas(spec, 0.2, 0.8, 0.35, 0.03)
    cx, cy = 300 * SCALE, H - 300 * SCALE
    img = place_mark(img, spec, name, cx, cy, 260 * SCALE, glow=0.8)
    wordmark(img, spec, name.upper(), cx + 140 * SCALE, cy - 22 * SCALE, 34, 26, align="left", alpha=0.4)
    return finish(img, spec["seed"] + 6)


def rim_curve(spec, seed, y_left, y_right, bulge, peak_u, light_u):
    """A single dark slope lit along its top edge (Graphite's black dune)."""
    img = canvas(spec, 0.6, 0.35, 0.5, 0.025)
    edge = (y_left + (y_right - y_left) * U[0] - bulge * np.exp(-((U[0] - peak_u) / 0.32) ** 2)) * H
    edge += noise1d(seed, 900 * SCALE, 3) * 10 * SCALE
    below = np.clip(Y - edge[None, :] + 1, 0, 1)
    sand = hexf(spec["base"]) * 0.32 + c(fbm(seed + 1, 500 * SCALE, 60 * SCALE) * 0.012, hexf(spec["pale"]))
    img = img * (1 - below[..., None]) + sand * below[..., None]
    depth = np.clip(Y - edge[None, :], 0, None)
    along = np.exp(-((U - light_u) / 0.28) ** 2)
    img += c(np.exp(-depth / (3 * SCALE)) * below * along * 0.55, hexf(spec["pale"]))
    img += c(np.exp(-depth / (60 * SCALE)) * below * along * 0.05, hexf(spec["accent"]))
    return img


def bramble_thorn(spec):
    """One thorned stem rising from the bottom edge to a lit berry."""
    s = spec
    img = canvas(s, 0.62, 0.3, 0.35, 0.03)
    pale, acc = hexf(s["pale"]), hexf(s["accent"])
    k = SCALE
    layer = Image.new("L", (W * 2, H * 2), 0)
    d = ImageDraw.Draw(layer)
    pts = []
    for t in np.linspace(0, 1, 400):
        # cubic from the lower-left edge up to the berry
        p0, p1, p2, p3 = np.array([1500, 2400]), np.array([1700, 1500]), np.array([2600, 1500]), np.array([2380, 720])
        p = (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3
        pts.append(tuple(p * 2 * k))
    d.line(pts, fill=255, width=max(1, int(6 * k)), joint="curve")
    for i, side in [(90, 1), (170, -1), (250, 1), (320, -1)]:
        (x0, y0), (x1, y1) = pts[i], pts[i + 4]
        tx, ty = x1 - x0, y1 - y0
        n = np.hypot(tx, ty)
        nx, ny = -ty / n * side, tx / n * side
        tip = (x0 + nx * 46 * k - tx / n * 28 * k, y0 + ny * 46 * k - ty / n * 28 * k)
        d.line([pts[i], tip], fill=255, width=max(1, int(5 * k)))
    line = np.asarray(layer.resize((W, H), Image.LANCZOS), np.float32) / 255
    bx, by, br = 2380 * k, 690 * k, 34 * k
    berry = np.clip(br - np.hypot(X - bx, Y - by) + 1, 0, 1)
    img = img * (1 - line[..., None] * 0.55) + c(line * 0.55, pale * 0.8)
    rr = np.hypot(X - bx, Y - by)
    img += c(np.exp(-rr / (60 * k)) * 0.35 + np.exp(-rr / (400 * k)) * 0.08, acc)
    img = img * (1 - berry[..., None]) + c(berry, np.clip(acc * 1.15 + 0.08, 0, 1))
    return finish(img, s["seed"] + 3)


def bramble_moon(spec):
    """A low berry moon over a dark, thorny hedgerow."""
    s = spec
    k = SCALE
    acc, pale = hexf(s["accent"]), hexf(s["pale"])
    img = canvas(s, 0.5, 0.55, 0.45, 0.03)
    mx, my, mr = 0.36 * W, 0.5 * H, 120 * k
    r = np.hypot(X - mx, Y - my)
    disc = np.clip(mr - r + 1, 0, 1)
    tex = fbm(s["seed"] + 7, 120 * k, octaves=4)
    img += c(np.exp(-np.clip(r - mr, 0, None) / (90 * k)) * 0.1 + np.exp(-np.clip(r - mr, 0, None) / (600 * k)) * 0.04, acc)
    img = img * (1 - disc[..., None]) + c(disc * (0.5 + 0.08 * tex), acc * 0.8 + pale * 0.2)
    top = (0.72 - 0.05 * noise1d(s["seed"], 1200 * k, 3)) * H
    spikes = noise1d(s["seed"] + 2, 18 * k, 2)
    top = top - (spikes ** 6) * 70 * k
    hedge = np.clip(Y - top[None, :] + 1, 0, 1)
    img = img * (1 - hedge[..., None]) + c(hedge, hexf(s["base"]) * 0.25)
    rim = np.exp(-np.clip(Y - top, 0, None) / (3 * k)) * hedge * np.exp(-((U - 0.36) / 0.22) ** 2)
    img += c(rim * 0.3, pale)
    return finish(img, s["seed"] + 4)


def vesper_star(spec):
    """The evening star alone over a flat, dark horizon."""
    s = spec
    k = SCALE
    acc, pale = hexf(s["accent"]), hexf(s["pale"])
    img = np.broadcast_to(hexf(s["base"]) * 0.5, (H, W, 3)).copy()
    hz = 0.74
    img += c(np.exp(-((T - hz) / 0.16) ** 2) * 0.10 * (T < hz), acc)
    img += c(np.exp(-((T - hz) / 0.025) ** 2) * 0.12 * (T < hz), pale * 0.6 + acc * 0.4)
    clouds = fbm(s["seed"], 1400 * k, 120 * k)
    img += c(np.exp(-((T - 0.62) / 0.06) ** 2) * clouds ** 3 * 0.05, pale)
    sx, sy = 0.67 * W, 0.27 * H
    r = np.hypot(X - sx, Y - sy)
    img += c(np.exp(-(r / (5 * k)) ** 2) * 1.2, pale)
    img += c(np.exp(-r / (26 * k)) * 0.4 + np.exp(-r / (260 * k)) * 0.06, acc)
    flare = (np.exp(-np.abs(Y - sy) / (1.2 * k)) * np.exp(-np.abs(X - sx) / (120 * k))
             + np.exp(-np.abs(X - sx) / (1.2 * k)) * np.exp(-np.abs(Y - sy) / (120 * k)))
    img += c(flare * 0.25, pale)
    land = np.clip(Y - hz * H + 1 + noise1d(s["seed"] + 1, 1600 * k, 3) * 6 * k, 0, 1)
    img = img * (1 - land[..., None]) + c(land, hexf(s["base"]) * 0.2)
    return finish(img, s["seed"] + 3)


def vesper_lake(spec):
    """Still water and one thin line of violet light on the horizon."""
    s = spec
    k = SCALE
    acc, pale = hexf(s["accent"]), hexf(s["pale"])
    hz = 0.58
    sky = np.broadcast_to(hexf(s["base"]) * 0.5, (H, W, 3)).copy()
    sky += c(np.exp(-((T - hz) / 0.09) ** 2) * 0.14 * (0.5 + 0.5 * fbm(s["seed"], 900 * k, 200 * k)), acc)
    line = np.exp(-((T - hz) * H / (2.5 * k)) ** 2) * np.exp(-((U - 0.5) / 0.3) ** 2)
    sky += c(line * 0.9, pale * 0.5 + acc * 0.5)
    rows = np.clip((2 * hz * H - Y).astype(int), 0, H - 1)
    wob = (np.sin(Y / (5 * k) + fbm(s["seed"] + 5, 200 * k, 30 * k) * 8) * 5 * k).astype(int)
    cols = np.clip(X.astype(int) + wob, 0, W - 1)
    refl = sky[rows, cols]
    streak = fbm(s["seed"] + 6, 600 * k, 5 * k, 4)
    fall = np.exp(-np.clip(T - hz, 0, None) / 0.2)
    water = refl * (0.3 + 0.9 * streak * fall)[..., None] + hexf(s["base"]) * 0.2
    img = np.where((T > hz)[..., None], water, sky)
    return finish(img, s["seed"] + 4)


WALLPAPERS = {
    "bramble": [
        ("01-bramble", w_mark),
        ("03-thorn", lambda n, s: bramble_thorn(s)),
        ("04-berry-moon", lambda n, s: bramble_moon(s)),
        ("05-dusk-slope", lambda n, s: finish(rim_curve(s, s["seed"] + 5, 0.66, 0.78, 0.12, 0.3, 0.32), s["seed"] + 5)),
        ("06-bramble-corner", w_corner),
    ],
    "vesper": [
        ("01-vesper", w_mark),
        ("03-evening-star", lambda n, s: vesper_star(s)),
        ("04-still-dusk", lambda n, s: vesper_lake(s)),
        ("05-violet-dune", lambda n, s: finish(rim_curve(s, s["seed"] + 5, 0.8, 0.62, 0.1, 0.65, 0.62), s["seed"] + 5)),
        ("06-vesper-corner", w_corner),
    ],
}


# ---------------------------------------------------------------- lock screen

def lock_toml(name, s):
    return f'''# Lock screen password card. The wallpaper stays behind it, blurred.
# A near-black {name.title()} card with a thin border in the theme's one point
# of light, which turns soft red after a wrong password.
background       = "{s['card']}"
background-alpha = 0.85
text             = "{s['text']}"
placeholder      = "{s['placeholder']}"
text-error       = "{s['error']}"
border           = "{s['accent']}"
border-active    = "{s['accent']}"
border-error     = "{s['error']}"
border-alpha     = 1.0
selection        = "{s['accent']}"
selection-alpha  = 0.35
'''


def unlock_png(name, s):
    """The mark alone for the boot unlock screen, trimmed and evenly padded."""
    size = 300
    line, light = masks(name, size)
    pale = np.array([int(s["pale"][i:i + 2], 16) for i in (1, 3, 5)], np.float32)
    acc = np.array([int(s["accent"][i:i + 2], 16) for i in (1, 3, 5)], np.float32)
    a = np.clip(line * 0.62 + light, 0, 1)
    w = np.where(a > 0, light / np.maximum(a, 1e-6), 0)[..., None]
    rgb = pale * (1 - w) + acc * w
    img = Image.fromarray(np.dstack([rgb, a * 255]).astype(np.uint8), "RGBA")
    sys.path.insert(0, str(Path(__file__).parent))
    from unlock_centre import centre
    return centre(img)


def main():
    centre_marks()
    for name, spec in THEMES.items():
        out = ROOT / name
        bg = out / "backgrounds"
        target = PREVIEW_DIR / name if PREVIEW_DIR else bg
        target.mkdir(parents=True, exist_ok=True)
        if not PREVIEW_DIR:
            (out / "logo.svg").write_text(svg(name, spec["pale"], spec["accent"]))
            for old in bg.glob("*.png"):
                if "-nature" not in old.name:
                    old.unlink()
        first = None
        for fname, fn in WALLPAPERS[name]:
            im = fn(name, spec)
            im.save(target / f"{fname}.png", optimize=not PREVIEW_DIR)
            first = first or im
            print(name, fname, im.size, flush=True)
        if not PREVIEW_DIR:
            first.resize((1920, 1200), Image.LANCZOS).crop((0, 60, 1920, 1140)).save(out / "preview.png")
            (out / "shell.lock.toml").write_text(lock_toml(name, spec))
            unlock_png(name, spec).save(out / "unlock.png")
        else:
            unlock_png(name, spec).save(target / "unlock.png")


if __name__ == "__main__":
    main()
