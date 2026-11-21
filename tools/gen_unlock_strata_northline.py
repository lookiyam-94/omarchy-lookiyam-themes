import sys
from PIL import Image, ImageDraw, ImageFont
which, out = sys.argv[1], sys.argv[2]
SS = 4; W, H = 900, 180
grey = Image.new("L", (W*SS, H*SS), 0); lit = Image.new("L", (W*SS, H*SS), 0)
dg, dl = ImageDraw.Draw(grey), ImageDraw.Draw(lit)
cx, cy = 90*SS, 90*SS
if which == "strata":
    for i, half in enumerate([36, 54, 72]):
        y = cy - 18*SS + i*18*SS
        (dl if i == 2 else dg).rounded_rectangle([cx-half*SS, y-2*SS, cx+half*SS, y+2*SS], radius=2*SS, fill=255 if i == 2 else 150)
    text, col, track = "STRATA", (246, 226, 196), 40
else:
    h = 44*SS
    dg.rounded_rectangle([cx-h, cy-h, cx+h, cy+h], radius=12*SS, outline=150, width=3*SS)
    lx = cx + 10*SS
    dl.rounded_rectangle([lx-2*SS, cy-h-14*SS, lx+2*SS, cy+h+14*SS], radius=2*SS, fill=255)
    text, col, track = "NORTHLINE", (210, 250, 232), 22
font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans-ExtraLight.ttf", 56*SS)
x = 200*SS
for ch in text:
    dg.text((x, 56*SS), ch, font=font, fill=230); x += font.getlength(ch) + track*SS
from PIL import ImageChops
a = ImageChops.lighter(grey, lit).resize((W, H), Image.LANCZOS)
img = Image.new("RGBA", (W, H), col + (0,)); img.putalpha(a); img.save(out)
