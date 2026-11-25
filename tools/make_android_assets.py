#!/usr/bin/env python3
# Regenerates the Obscurant images for the Android app from the logo (needs Pillow).
# usage: make_android_assets.py <firefox source>/mobile/android/fenix/app/src <logo 512px png>
import glob, os, sys
from PIL import Image, ImageDraw, ImageFont

SRC, LOGO = sys.argv[1:3]
logo = Image.open(LOGO).convert("RGBA")


def font(size):
    for p in ("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def wordmark(color):
    w, h = 1103, 319
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    lg = logo.resize((h - 20, h - 20), Image.LANCZOS)
    im.paste(lg, (10, 10), lg)
    d = ImageDraw.Draw(im)
    f = font(170)
    bb = d.textbbox((0, 0), "Obscurant", font=f)
    d.text((h + 10, (h - (bb[3] - bb[1])) // 2 - bb[1]), "Obscurant", font=f, fill=color)
    return im


def padded(img, size, ratio):
    c = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    s = int(size * ratio)
    r = img.resize((s, s), Image.LANCZOS)
    c.paste(r, ((size - s) // 2, (size - s) // 2), r)
    return c


res = os.path.join(SRC, "main", "res")
for d in ("drawable-nodpi", "drawable-night-nodpi"):
    os.makedirs(os.path.join(res, d), exist_ok=True)
wordmark((18, 21, 28, 255)).save(os.path.join(res, "drawable-nodpi", "ic_logo_wordmark_normal.png"))
wordmark((232, 234, 242, 255)).save(os.path.join(res, "drawable-night-nodpi", "ic_logo_wordmark_normal.png"))
wordmark((255, 255, 255, 255)).save(os.path.join(res, "drawable-nodpi", "ic_logo_wordmark_private.png"))
for f in glob.glob(os.path.join(SRC, "release", "res", "drawable-*", "ic_logo_wordmark_*.webp")):
    os.remove(f)
fg = padded(logo, 432, 0.62)
fg.save(os.path.join(res, "drawable-nodpi", "obscurant_launcher_fg.png"))
alpha = fg.split()[3]
Image.merge("RGBA", (Image.new("L", fg.size, 255),) * 3 + (alpha,)).save(os.path.join(res, "drawable-nodpi", "obscurant_launcher_mono.png"))
for d, sz in {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}.items():
    bg = Image.new("RGBA", (sz, sz), (13, 16, 23, 255))
    lg = logo.resize((int(sz * 0.8),) * 2, Image.LANCZOS)
    bg.paste(lg, ((sz - lg.width) // 2, (sz - lg.height) // 2), lg)
    for n in ("ic_launcher", "ic_launcher_round"):
        bg.save(os.path.join(SRC, "release", "res", f"mipmap-{d}", f"{n}.webp"))
print("assets written")
mark = fg.crop(fg.getbbox())
for p in (os.path.join(res, "drawable-hdpi", "fenix_search_widget.webp"),
          os.path.join(SRC, "release", "res", "drawable-hdpi", "fenix_search_widget.webp")):
    size = Image.open(p).size
    card = Image.new("RGBA", size, (13, 16, 23, 255))
    small = mark.copy()
    small.thumbnail((int(min(size) * 0.7),) * 2)
    card.paste(small, ((size[0] - small.width) // 2, (size[1] - small.height) // 2), small)
    card.save(p)
print("widget preview written")
