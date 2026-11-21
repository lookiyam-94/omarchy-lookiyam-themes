"""Graphite unlock.png: open 'G' ring with a blue light bar."""
import sys
from unlock_centre import centre
from PIL import Image, ImageDraw

SS = 4; W, H = 900, 180; K = 2  # output scale
grey = Image.new("L", (W*SS, H*SS), 0); dg = ImageDraw.Draw(grey)
blue = Image.new("L", (W*SS, H*SS), 0); db = ImageDraw.Draw(blue)

# mark: 300 degree ring open on the right, bar from the centre to the opening, dot at the centre
cx, cy, R, stroke = 90*SS, 96*SS, 56*SS, 4*SS
dg.arc([cx-R, cy-R, cx+R, cy+R], start=25, end=335, fill=150, width=stroke)
db.rounded_rectangle([cx, cy - stroke//2, cx + R, cy + stroke//2], radius=stroke//2, fill=255)
r = 7*SS
db.ellipse([cx-r, cy-r, cx+r, cy+r], fill=255)


grey = grey.resize((W*K, H*K), Image.LANCZOS); blue = blue.resize((W*K, H*K), Image.LANCZOS)
pale = Image.new("RGBA", (W*K, H*K), (228, 232, 238, 0)); pale.putalpha(grey)
light = Image.new("RGBA", (W*K, H*K), (143, 191, 255, 0)); light.putalpha(blue)
centre(Image.alpha_composite(pale, light)).save(sys.argv[1])
