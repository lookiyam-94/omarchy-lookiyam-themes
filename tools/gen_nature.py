"""Build the five nature theme marks, wallpapers and previews.

Usage: python tools/gen_nature.py SOURCE_DIR
SOURCE_DIR contains lichen.png, vesper.png, tidal.png, bramble.png, rime.png.
The photographs are generated separately; this script crops them to 3840x2400.
"""
from pathlib import Path
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1] / "themes"
SRC = Path(sys.argv[1])
W, H = 3840, 2400
FONT = "/usr/share/fonts/TTF/DejaVuSans-ExtraLight.ttf"

THEMES = {
    "lichen": {"base": "#0b100e", "accent": "#9bbd88", "pale": "#d9e4d3", "photo": "moss-covered forest"},
    "vesper": {"base": "#100d15", "accent": "#b6a0d6", "pale": "#e6deef", "photo": "violet heathland twilight"},
    "tidal": {"base": "#091213", "accent": "#75c5bd", "pale": "#d3e9e5", "photo": "teal tidal coast"},
    "bramble": {"base": "#140d12", "accent": "#c791a9", "pale": "#eadbe2", "photo": "berry hedgerow"},
    "rime": {"base": "#0c1013", "accent": "#b9cbd2", "pale": "#e3ebee", "photo": "frosted winter woodland"},
}


def rgb(h):
    return tuple(bytes.fromhex(h[1:]))


def mark(name, size, color, width):
    """Transparent mark in its own square; all marks share line weight."""
    layer = Image.new("RGBA", (size, size))
    d = ImageDraw.Draw(layer)
    s = size / 300
    def p(xy):
        return [(int(x*s), int(y*s)) for x, y in xy]
    c = rgb(color) + (235,)
    faint = rgb(color) + (115,)
    if name == "lichen":
        # Three growing fronds around a small luminous spore.
        for flip in (-1, 1):
            d.arc((int((55 if flip < 0 else 115)*s), 38*s, int((185 if flip < 0 else 245)*s), 270*s), 20 if flip < 0 else 160, 200 if flip < 0 else 340, fill=c, width=width)
        d.line(p([(150, 242), (150, 72)]), fill=faint, width=width)
        for y, off in [(105, 38), (145, 53), (185, 38)]:
            d.line(p([(150, y), (150-off, y-25)]), fill=faint, width=width)
            d.line(p([(150, y+10), (150+off, y-15)]), fill=faint, width=width)
        d.ellipse((139*s, 55*s, 161*s, 77*s), fill=c)
    elif name == "vesper":
        d.arc((35*s, 35*s, 265*s, 265*s), 45, 315, fill=faint, width=width)
        d.arc((52*s, 38*s, 245*s, 252*s), 65, 285, fill=c, width=width)
        d.line(p([(72, 205), (150, 157), (228, 205)]), fill=c, width=width)
        d.ellipse((145*s, 96*s, 155*s, 106*s), fill=c)
    elif name == "tidal":
        for y, ext in [(100, 0), (150, 30), (200, 0)]:
            d.arc(((45+ext)*s, (y-32)*s, (255-ext)*s, (y+32)*s), 180, 360, fill=c if y == 150 else faint, width=width)
            d.arc(((45+ext)*s, (y-32)*s, (255-ext)*s, (y+32)*s), 0, 180, fill=faint, width=width)
        d.ellipse((143*s, 136*s, 157*s, 150*s), fill=c)
    elif name == "bramble":
        d.line(p([(78, 239), (149, 147), (218, 61)]), fill=faint, width=width)
        for x, y, side in [(105, 207, -1), (175, 116, 1), (204, 77, -1)]:
            d.arc(((x-42)*s, (y-38)*s, (x+42)*s, (y+38)*s), 225 if side < 0 else 15, 45 if side < 0 else 195, fill=c, width=width)
        for x, y, r in [(116, 137, 16), (145, 157, 18), (161, 129, 16)]:
            d.ellipse(((x-r)*s, (y-r)*s, (x+r)*s, (y+r)*s), outline=c, width=width)
        d.ellipse((139*s, 151*s, 151*s, 163*s), fill=c)
    elif name == "rime":
        d.line(p([(150, 35), (150, 265)]), fill=c, width=width)
        d.line(p([(50, 92), (250, 208)]), fill=c, width=width)
        d.line(p([(50, 208), (250, 92)]), fill=c, width=width)
        for a, b in [((150, 55), (124, 79)), ((150, 55), (176, 79)), ((150, 245), (124, 221)), ((150, 245), (176, 221))]:
            d.line(p([a, b]), fill=faint, width=width)
        d.ellipse((141*s, 141*s, 159*s, 159*s), fill=c)
    return layer


def wordmark(img, name, y, color):
    font = ImageFont.truetype(FONT, 53)
    text = name.upper()
    track = 34
    widths = [font.getlength(ch) for ch in text]
    total = sum(widths) + track * (len(text)-1)
    x = int((W-total)/2)
    d = ImageDraw.Draw(img)
    for ch, wid in zip(text, widths):
        d.text((x, y), ch, font=font, fill=rgb(color)+(185,))
        x += int(wid+track)


def named_wallpaper(name, spec):
    base = rgb(spec["base"])
    image = Image.new("RGB", (W, H), base)
    glow = Image.new("RGBA", (W, H))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((W//2-650, H//2-750, W//2+650, H//2+550), fill=rgb(spec["accent"])+(35,))
    glow = glow.filter(ImageFilter.GaussianBlur(310))
    image = Image.alpha_composite(image.convert("RGBA"), glow)
    m = mark(name, 600, spec["accent"], 4)
    halo = m.filter(ImageFilter.GaussianBlur(28))
    halo.putalpha(halo.getchannel("A").point(lambda a: a//3))
    image.alpha_composite(halo, (1620, 650))
    image.alpha_composite(m, (1620, 650))
    wordmark(image, name, 1340, spec["pale"])
    return image.convert("RGB")


def palette(spec):
    a, b = spec["accent"], spec["base"]
    return f'''mode                     = "dark"

accent                   = "{a}"
selection                = "#252b2d"
muted                    = "#67737a"

background               = "{b}"
dark_background          = "#090b0d"
darker_background        = "#060809"
lighter_background       = "#1b2224"

foreground               = "#d4dddc"
dark_foreground          = "#899997"
light_foreground         = "#c0d0cc"
bright_foreground        = "#f0f4f1"

hyprland_active_border   = "rgba({a[1:]}ee) rgba(d4dddcaa) 45deg"
hyprland_inactive_border = "rgba(283033aa)"

red                      = "#d4868d"
yellow                   = "#d8c18a"
orange                   = "#d7a17d"
green                    = "#8fbe9d"
cyan                     = "#82c3bf"
blue                     = "#8fade0"
magenta                  = "#b99ccc"
brown                    = "#a78a76"

bright_red               = "#eba0a5"
bright_yellow            = "#eed7a0"
bright_orange            = "#edb794"
bright_green             = "#a9d7b6"
bright_cyan              = "#9bdbd5"
bright_blue              = "#a9c8f1"
bright_magenta           = "#d4b5e6"
'''


def build(name, spec):
    out = ROOT / name
    bg = out / "backgrounds"
    bg.mkdir(parents=True, exist_ok=True)
    minimal = named_wallpaper(name, spec)
    minimal.save(bg / f"01-{name}.png", optimize=True)
    source = Image.open(SRC / f"{name}.png").convert("RGB")
    target = W/H
    sw, sh = source.size
    if sw/sh > target:
        nw = round(sh*target)
        source = source.crop(((sw-nw)//2, 0, (sw+nw)//2, sh))
    else:
        nh = round(sw/target)
        source = source.crop((0, (sh-nh)//2, sw, (sh+nh)//2))
    source.resize((W,H), Image.Resampling.LANCZOS).save(bg / f"02-{name}-nature.png", optimize=True)
    (out / "colors.toml").write_text(palette(spec))
    (out / "icons.theme").write_text("Yaru-" + {"lichen":"sage", "vesper":"purple", "tidal":"prussiangreen", "bramble":"magenta", "rime":"blue"}[name] + "\n")
    (out / "shell.lock.toml").write_text(f'''# Dark card with the theme accent over the blurred wallpaper.
background       = "#060809"
background-alpha = 0.85
text             = "#d4dddc"
placeholder      = "#899997"
text-error       = "#d4868d"
border           = "{spec['accent']}"
border-active    = "{spec['accent']}"
border-error     = "#d4868d"
border-alpha     = 1.0
selection        = "{spec['accent']}"
selection-alpha  = 0.35
''')
    m = mark(name, 300, spec["pale"], 4)
    box = m.getchannel("A").getbbox()
    m = m.crop(box)
    unlock = Image.new("RGBA", (m.width+60, m.height+60))
    unlock.alpha_composite(m, (30,30))
    unlock.save(out / "unlock.png")
    # Preview artwork is the first wallpaper as displayed on a 16:9 screen.
    minimal.resize((1920, 1200), Image.Resampling.LANCZOS).crop((0,60,1920,1140)).save(out / "preview.png")
    print(name, source.size)


for theme, data in THEMES.items():
    build(theme, data)
