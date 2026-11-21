import sys
from unlock_centre import centre
from PIL import Image, ImageDraw
which, out = sys.argv[1], sys.argv[2]
SS = 4; W, H = 900, 180; K = 2  # output scale
grey = Image.new("L", (W*SS, H*SS), 0); lit = Image.new("L", (W*SS, H*SS), 0)
dg, dl = ImageDraw.Draw(grey), ImageDraw.Draw(lit)
cx, cy = 90*SS, 90*SS
if which == "strata":
    for i, half in enumerate([36, 54, 72]):
        y = cy - 18*SS + i*18*SS
        (dl if i == 2 else dg).rounded_rectangle([cx-half*SS, y-2*SS, cx+half*SS, y+2*SS], radius=2*SS, fill=255 if i == 2 else 150)
    col = (246, 226, 196)
else:
    h = 44*SS
    dg.rounded_rectangle([cx-h, cy-h, cx+h, cy+h], radius=12*SS, outline=150, width=3*SS)
    lx = cx + 10*SS
    dl.rounded_rectangle([lx-2*SS, cy-h-14*SS, lx+2*SS, cy+h+14*SS], radius=2*SS, fill=255)
    col = (210, 250, 232)
from PIL import ImageChops
a = ImageChops.lighter(grey, lit).resize((W*K, H*K), Image.LANCZOS)
img = Image.new("RGBA", (W*K, H*K), col + (0,)); img.putalpha(a); centre(img).save(out)
