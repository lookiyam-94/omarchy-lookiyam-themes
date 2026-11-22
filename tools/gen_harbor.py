"""Build Harbor's vector wallpapers, logo, preview and unlock mark.

The mark is plain SVG line art: two open breakwaters, a pale quay line, and
one gold harbor light. Every wallpaper here is SVG on a flat navy (no
gradients, so no banding), rendered with rsvg-convert and finished with faint
zero-mean grain. The harbor photographs (02-06) are left untouched.

Run from the repository root:
    uv run --with numpy --with pillow python tools/gen_harbor.py
Requires rsvg-convert.
"""

from math import pi, sin
from pathlib import Path
import random
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from unlock_centre import centre  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "themes" / "harbor"
FONT = "/usr/share/fonts/TTF/DejaVuSans-ExtraLight.ttf"
W, H = 1920, 1200          # design units; rendered at 2x
SCALE = 2

BASE = "#17243a"
PALE = "#dce2de"
GOLD = "#d9bd83"
WORD = "#b0bfc9"

# The mark in its 400x320 box.
LINES = "M45 250 V68 H148 M355 250 V68 H252"
QUAY = "M82 277 H318"
LIGHT = (200, 68, 10)
BOX = (45, 58, 355, 277)            # bounds of the mark, strokes aside

LOGO = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 320" width="400" height="320">
  <title>Harbor</title>
  <g fill="none" stroke="{PALE}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
    <path d="{LINES}"/>
    <path d="{QUAY}" opacity="0.6"/>
  </g>
  <circle cx="{LIGHT[0]}" cy="{LIGHT[1]}" r="{LIGHT[2]}" fill="{GOLD}"/>
</svg>
'''


def mark(cx, cy, s, width):
    """The mark with its box centre at (cx, cy), scaled by s."""
    mx, my = (BOX[0] + BOX[2]) / 2, (BOX[1] + BOX[3]) / 2
    x, y, r = LIGHT
    return (f'<g transform="translate({cx - mx * s:.2f} {cy - my * s:.2f}) scale({s})">'
            f'<g fill="none" stroke="{PALE}" stroke-width="{width / s:.3f}" '
            f'stroke-linecap="round" stroke-linejoin="round" opacity="0.8">'
            f'<path d="{LINES}"/><path d="{QUAY}" opacity="0.6"/></g>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="{GOLD}"/></g>')


def light(x, y, r=10, ring=True):
    out = f'<circle cx="{x}" cy="{y}" r="{r}" fill="{GOLD}"/>'
    if ring:
        out = (f'<circle cx="{x}" cy="{y}" r="{r * 3}" fill="none" stroke="{GOLD}" '
               f'stroke-width="1.5" opacity="0.3"/>') + out
    return out


def reflection(x, y, widths, gap=26, top=0.55):
    """A light's reflection: short gold strokes, narrower and fainter going down."""
    out = []
    for i, w in enumerate(widths):
        o = top * (1 - i / len(widths)) + 0.08
        out.append(f'<path d="M{x - w / 2:.0f} {y + i * gap} H{x + w / 2:.0f}" stroke="{GOLD}" '
                   f'stroke-width="3" stroke-linecap="round" opacity="{o:.2f}"/>')
    return "".join(out)


# --------------------------------------------------------------------------
# Scenes, 1920x1200 units
# --------------------------------------------------------------------------

def pierhead():
    """Northline and Meridian: one light at the end of a pier, its reflection below."""
    return (f'<g fill="none" stroke="{PALE}" stroke-linecap="round" stroke-width="2">'
            '<path d="M0 760 H1920" opacity="0.22"/>'
            '<path d="M1920 734 H1236 V700" opacity="0.7" stroke-width="3"/></g>'
            + light(1236, 682, 9)
            + reflection(1236, 792, [70, 54, 40, 28, 18, 10]))


def tide():
    """Strata: still water drawn as fine lines, one of them catching the light."""
    rng = random.Random("harbor-tide")
    out = [f'<g fill="none" stroke="{PALE}" stroke-linecap="round">']
    gold_row = 15
    for row in range(26):
        y = 330 + row * 22
        phase, amp = rng.uniform(0, 2 * pi), 2.5 + rng.uniform(0, 3)
        pts = " L".join(f"{x} {y + amp * sin(x / 260 + phase):.1f}" for x in range(-20, 1961, 40))
        if row == gold_row:
            out.append(f'</g><path d="M{pts}" fill="none" stroke="{GOLD}" stroke-width="2.5" opacity="0.9"/>'
                       f'<g fill="none" stroke="{PALE}" stroke-linecap="round">')
        else:
            out.append(f'<path d="M{pts}" stroke-width="1.5" opacity="{0.10 + 0.05 * (row % 3 == 0):.2f}"/>')
    out.append("</g>")
    return "".join(out)


def mouth():
    """Carbon-style close crop: the breakwaters huge, the light between them on the water."""
    return (f'<g fill="none" stroke="{PALE}" stroke-linecap="round" stroke-linejoin="round" '
            'stroke-width="3" opacity="0.7">'
            '<path d="M260 1200 V470 H800 M1660 1200 V470 H1120"/></g>'
            + light(960, 470, 12)
            + reflection(960, 540, [90, 70, 52, 36, 22, 12], gap=30))


def night():
    """Graphite and Vesper: a low quay far away, the sky open above, one light."""
    rng = random.Random("harbor-night")
    stars = "".join(
        f'<circle cx="{rng.uniform(40, 1880):.0f}" cy="{rng.uniform(40, 560):.0f}" '
        f'r="{rng.choice([1.1, 1.1, 1.5]):.1f}" fill="{PALE}" opacity="{rng.uniform(0.25, 0.6):.2f}"/>'
        for _ in range(70))
    return (stars
            + f'<g fill="none" stroke="{PALE}" stroke-linecap="round" stroke-width="2">'
            '<path d="M0 866 H560 M760 866 H1920" opacity="0.55"/></g>'
            + light(660, 858, 7)
            + reflection(660, 900, [40, 30, 20, 12], gap=22))


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def render(svg, w, h):
    with tempfile.TemporaryDirectory() as tmp:
        src, dst = Path(tmp) / "in.svg", Path(tmp) / "out.png"
        src.write_text(svg)
        subprocess.run(["rsvg-convert", "-w", str(w), "-h", str(h), "-o", str(dst), str(src)], check=True)
        return Image.open(dst).convert("RGBA")


def wall(body):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
           f'<rect width="{W}" height="{H}" fill="{BASE}"/>{body}</svg>')
    return render(svg, W * SCALE, H * SCALE).convert("RGB")


def word(im, x, y, size=29, tracking=16):
    """Letter-spaced wordmark; (x, y) in design units."""
    text = "HARBOR"
    font = ImageFont.truetype(FONT, size * SCALE)
    d = ImageDraw.Draw(im)
    widths = [d.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * SCALE * (len(text) - 1)
    px = x * SCALE - total / 2
    for ch, width in zip(text, widths):
        d.text((px, y * SCALE), ch, fill=WORD, font=font)
        px += width + tracking * SCALE


def grain(im, seed):
    rng = np.random.default_rng(sum(map(ord, seed)))
    small = rng.normal(0, 1.6, (im.height // 4, im.width // 4)).astype(np.float32)
    noise = np.asarray(Image.fromarray(small, "F").resize(im.size, Image.Resampling.BILINEAR))
    arr = np.asarray(im, dtype=np.float32) + noise[..., None]
    return Image.fromarray(np.clip(arr + 0.5, 0, 255).astype(np.uint8))


def lockup():
    s = 1.25
    im = wall(mark(960, 530, s, 4))
    word(im, 960, 530 + (BOX[3] - BOX[1]) / 2 * s + 92)
    return im


def unlock_preview(logo):
    base = tuple(int(BASE[i:i + 2], 16) for i in (1, 3, 5))
    text = tuple(int(PALE[i:i + 2], 16) for i in (1, 3, 5))
    assets = Path("/usr/share/omarchy/default/plymouth")
    im = Image.new("RGBA", (1920, 1080), base + (255,))
    lx, ly = (1920 - logo.width) // 2, (1080 - logo.height) // 2
    im.alpha_composite(logo, (lx, ly))

    def tinted(file):
        source = Image.open(assets / file).convert("RGBA")
        result = Image.new("RGBA", source.size, text + (0,))
        result.putalpha(source.getchannel("A"))
        return result

    entry = tinted("entry.png")
    ex, ey = (1920 - entry.width) // 2, ly + logo.height + 40
    im.alpha_composite(entry, (ex, ey))
    lock = tinted("lock.png")
    lock = lock.resize((round(84 * entry.height * .8 / 96), round(entry.height * .8)))
    im.alpha_composite(lock, (ex - lock.width - 15, ey + (entry.height - lock.height) // 2))
    bullet = tinted("bullet.png").resize((7, 7))
    for i in range(4):
        im.alpha_composite(bullet, (ex + 20 + i * 12, ey + entry.height // 2 - 4))
    im.convert("RGB").save(OUT / "preview-unlock.png")


def main():
    bg = OUT / "backgrounds"
    bg.mkdir(parents=True, exist_ok=True)
    walls = {
        "01-harbor.png": lockup(),
        "07-pierhead.png": wall(pierhead()),
        "08-still-water.png": wall(tide()),
        "09-harbor-mouth.png": wall(mouth()),
        "10-night-quay.png": wall(night()),
    }
    only = set(sys.argv[1:])
    for file, im in walls.items():
        if not only or file in only:
            grain(im, file).save(bg / file, optimize=True)
            print("wrote", file)
    walls["01-harbor.png"].resize((1920, 1200), Image.Resampling.LANCZOS).crop((0, 60, 1920, 1140)).save(OUT / "preview.png")
    (OUT / "logo.svg").write_text(LOGO)
    logo = centre(render(LOGO, 400, 320))
    logo.save(OUT / "unlock.png")
    unlock_preview(logo)


if __name__ == "__main__":
    main()
