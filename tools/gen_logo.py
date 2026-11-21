"""Minimal Graphite Blue wallpaper with an invented 'G' mark + wordmark."""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = sys.argv[1]
W, H = 3840, 2400
SS = 3  # supersampling for the logo layer
FONT = "/usr/share/fonts/TTF/DejaVuSans-ExtraLight.ttf"

# --- background: near-black with a soft cool falloff, vignette, grain
Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
cx, cy = W / 2, H * 0.46
r = np.hypot((X - cx) / W, (Y - cy) / H)
base = np.array([0.028, 0.032, 0.045], np.float32)
img = base + (np.exp(-(r / 0.28) ** 2) * 0.05)[..., None] * np.array([0.35, 0.5, 0.8], np.float32)
img *= (1 - 0.5 * r ** 2)[..., None]

# --- logo drawn white-on-black at SS x, as two masks: grey stroke + blue light bar
box = 900
S = box * SS
grey = Image.new("L", (S, S), 0)
blue = Image.new("L", (S, S), 0)
dg, db = ImageDraw.Draw(grey), ImageDraw.Draw(blue)
R = 300 * SS
stroke = 14 * SS
c0 = S // 2
# open ring: 300 degree arc, gap on the right (a "G" without being any real logo)
dg.arc([c0 - R, c0 - R, c0 + R, c0 + R], start=25, end=335, fill=255, width=stroke)
# light bar from the centre to the ring's lower opening
db.rounded_rectangle([c0, c0 - stroke // 2, c0 + R, c0 + stroke // 2], radius=stroke // 2, fill=255)
# small blue dot at the centre
d = 22 * SS
db.ellipse([c0 - d, c0 - d, c0 + d, c0 + d], fill=255)

grey = np.asarray(grey.resize((box, box), Image.LANCZOS), np.float32) / 255
blue_im = blue.resize((box, box), Image.LANCZOS)
blue = np.asarray(blue_im, np.float32) / 255
glow = (np.asarray(blue_im.filter(ImageFilter.GaussianBlur(18)), np.float32) / 255) * 0.9 \
     + (np.asarray(blue_im.filter(ImageFilter.GaussianBlur(90)), np.float32) / 255) * 1.4

ox, oy = int(cx - box / 2), int(cy - box / 2)
sl = (slice(oy, oy + box), slice(ox, ox + box))
PALE = np.array([0.80, 0.84, 0.90], np.float32)
BLUE = np.array([0.44, 0.68, 1.0], np.float32)
LIGHT = np.array([0.85, 0.92, 1.0], np.float32)
img[sl] += glow[..., None] * BLUE * 0.35
img[sl] = img[sl] * (1 - grey[..., None]) + grey[..., None] * PALE * 0.55
img[sl] = img[sl] * (1 - blue[..., None]) + blue[..., None] * LIGHT

# --- wordmark: thin, widely tracked
text = "GRAPHITE"
font = ImageFont.truetype(FONT, 46 * SS)
track = 34 * SS
widths = [font.getlength(ch) for ch in text]
tw = int(sum(widths) + track * (len(text) - 1))
th = 80 * SS
tl = Image.new("L", (tw + 20 * SS, th), 0)
dt = ImageDraw.Draw(tl)
x = 10 * SS
for ch, w in zip(text, widths):
    dt.text((x, 0), ch, font=font, fill=255)
    x += w + track
tl = tl.resize((tl.width // SS, tl.height // SS), Image.LANCZOS)
t = np.asarray(tl, np.float32) / 255
ty = int(cy + 300 + 170)
tx = int(cx - t.shape[1] / 2)
ts = (slice(ty, ty + t.shape[0]), slice(tx, tx + t.shape[1]))
img[ts] = img[ts] * (1 - t[..., None] * 0.6) + t[..., None] * PALE * 0.6 * 0.75

# --- finish
rng = np.random.default_rng(11)
img += rng.normal(0, 0.007, (H, W, 1)).astype(np.float32)
img = np.clip(img, 0, 1)
Image.fromarray((img * 255 + 0.5).astype(np.uint8), "RGB").save(OUT)
