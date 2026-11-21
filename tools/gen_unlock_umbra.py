import sys
from unlock_centre import centre
from PIL import Image, ImageDraw, ImageChops
SS = 4; W, H = 900, 180; K = 2  # output scale
a = Image.new("L", (W*SS, H*SS), 0); d = ImageDraw.Draw(a)
cx, cy, R = 90*SS, 90*SS, 56*SS
d.ellipse([cx-R, cy-R, cx+R, cy+R], outline=90, width=3*SS)          # faint ring
cres = Image.new("L", a.size, 0); dc = ImageDraw.Draw(cres)
dc.ellipse([cx-R, cy-R, cx+R, cy+R], fill=255)
dc.ellipse([cx-R-7*SS, cy-R+5*SS, cx+R-7*SS, cy+R+5*SS], fill=0)      # crescent on the right
a = ImageChops.lighter(a, cres)
a = a.resize((W*K, H*K), Image.LANCZOS)
img = Image.new("RGBA", (W*K, H*K), (214, 228, 255, 0)); img.putalpha(a)
centre(img).save(sys.argv[1])
