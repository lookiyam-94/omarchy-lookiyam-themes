import sys
from PIL import Image, ImageDraw, ImageFont, ImageChops
SS = 4; W, H = 900, 180
a = Image.new("L", (W*SS, H*SS), 0); d = ImageDraw.Draw(a)
cx, cy, R = 90*SS, 90*SS, 56*SS
d.ellipse([cx-R, cy-R, cx+R, cy+R], outline=90, width=3*SS)          # faint ring
cres = Image.new("L", a.size, 0); dc = ImageDraw.Draw(cres)
dc.ellipse([cx-R, cy-R, cx+R, cy+R], fill=255)
dc.ellipse([cx-R-7*SS, cy-R+5*SS, cx+R-7*SS, cy+R+5*SS], fill=0)      # crescent on the right
a = ImageChops.lighter(a, cres)
font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans-ExtraLight.ttf", 64*SS)
x = 200*SS
for ch in "UMBRA":
    d = ImageDraw.Draw(a); d.text((x, 52*SS), ch, font=font, fill=230)
    x += font.getlength(ch) + 40*SS
a = a.resize((W, H), Image.LANCZOS)
img = Image.new("RGBA", (W, H), (214, 228, 255, 0)); img.putalpha(a)
img.save(sys.argv[1])
