import sys
from unlock_centre import centre
from PIL import Image, ImageDraw, ImageFont
SS = 4; W, H = 900, 180
a = Image.new("L", (W*SS, H*SS), 0); d = ImageDraw.Draw(a)
import math
cx, cy, R = 90*SS, 100*SS, 58*SS
pts = [(cx + R*math.cos(math.radians(t)), cy + R*math.sin(math.radians(t))) for t in (-90, 30, 150)]
d.line(pts + [pts[0]], fill=150, width=4*SS, joint="curve")
ax, ay = pts[0]; r = 9*SS
d.ellipse([ax-r, ay-r, ax+r, ay+r], fill=255)
font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans-ExtraLight.ttf", 56*SS)
x = 200*SS
for ch in "MERIDIAN":
    d.text((x, 56*SS), ch, font=font, fill=230); x += font.getlength(ch) + 26*SS
img = Image.new("RGBA", (W, H), (214, 236, 255, 0)); img.putalpha(a.resize((W, H), Image.LANCZOS)); centre(img).save(sys.argv[1])
