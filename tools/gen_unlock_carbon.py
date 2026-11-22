"""Draw Carbon's steel hexagon and orange light for the unlock screen."""

import math
import sys
from PIL import Image, ImageDraw
from unlock_centre import centre

SS = 4
im = Image.new("RGBA", (360 * SS, 360 * SS))
d = ImageDraw.Draw(im)
cx = cy = 180 * SS
r = 130 * SS
pts = [(cx + r * math.cos(math.radians(60*k-30)),
        cy + r * math.sin(math.radians(60*k-30))) for k in range(7)]
d.line(pts, fill=(184, 194, 201, 190), width=5 * SS, joint="curve")
x, y = pts[5]
d.ellipse((x-10*SS, y-10*SS, x+10*SS, y+10*SS), fill=(255, 134, 26, 255))
im = im.resize((360, 360), Image.Resampling.LANCZOS)
centre(im).save(sys.argv[1])
