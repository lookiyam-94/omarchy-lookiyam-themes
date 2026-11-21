import sys
from unlock_centre import centre
from PIL import Image, ImageDraw
SS = 4; W, H = 900, 180; K = 2  # output scale
a = Image.new("L", (W*SS, H*SS), 0); d = ImageDraw.Draw(a)
import math
cx, cy, R = 90*SS, 100*SS, 58*SS
pts = [(cx + R*math.cos(math.radians(t)), cy + R*math.sin(math.radians(t))) for t in (-90, 30, 150)]
d.line(pts + [pts[0]], fill=150, width=4*SS, joint="curve")
ax, ay = pts[0]; r = 9*SS
d.ellipse([ax-r, ay-r, ax+r, ay+r], fill=255)
img = Image.new("RGBA", (W*K, H*K), (214, 236, 255, 0)); img.putalpha(a.resize((W*K, H*K), Image.LANCZOS)); centre(img).save(sys.argv[1])
