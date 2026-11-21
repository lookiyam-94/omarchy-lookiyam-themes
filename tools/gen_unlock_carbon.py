import math, sys
from PIL import Image, ImageDraw, ImageFont
SS = 4; W, H = 900, 180
a = Image.new("L", (W*SS, H*SS), 0); d = ImageDraw.Draw(a)
cx, cy, s = 90*SS, 96*SS, 58*SS
pts = [(cx + s*math.cos(math.radians(60*k - 30)), cy + s*math.sin(math.radians(60*k - 30))) for k in range(7)]
d.line(pts, fill=150, width=4*SS, joint="curve")
vx, vy = pts[5]; r = 9*SS
d.ellipse([vx-r, vy-r, vx+r, vy+r], fill=255)
font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans-ExtraLight.ttf", 56*SS)
x = 200*SS
for ch in "CARBON":
    d.text((x, 56*SS), ch, font=font, fill=230); x += font.getlength(ch) + 40*SS
img = Image.new("RGBA", (W, H), (255, 214, 196, 0)); img.putalpha(a.resize((W, H), Image.LANCZOS)); img.save(sys.argv[1])
