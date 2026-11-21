import math, sys
from unlock_centre import centre
from PIL import Image, ImageDraw
SS = 4; W, H = 900, 180; K = 2  # output scale
a = Image.new("L", (W*SS, H*SS), 0); d = ImageDraw.Draw(a)
cx, cy, s = 90*SS, 96*SS, 58*SS
pts = [(cx + s*math.cos(math.radians(60*k - 30)), cy + s*math.sin(math.radians(60*k - 30))) for k in range(7)]
d.line(pts, fill=150, width=4*SS, joint="curve")
vx, vy = pts[5]; r = 9*SS
d.ellipse([vx-r, vy-r, vx+r, vy+r], fill=255)
img = Image.new("RGBA", (W*K, H*K), (255, 214, 196, 0)); img.putalpha(a.resize((W*K, H*K), Image.LANCZOS)); centre(img).save(sys.argv[1])
