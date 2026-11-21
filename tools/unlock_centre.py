"""Trim an unlock.png to its visible pixels and pad it evenly.

Plymouth centres the whole image, so any empty margin on one side pushes the
mark off centre. Every gen_unlock_*.py passes its image through centre().
"""
from PIL import Image

PAD = 30


def centre(img: Image.Image, pad: int = PAD) -> Image.Image:
    box = img.getchannel("A").getbbox()
    mark = img.crop(box)
    out = Image.new("RGBA", (mark.width + 2 * pad, mark.height + 2 * pad), img.getpixel((0, 0))[:3] + (0,))
    out.paste(mark, (pad, pad))
    return out
