#!/usr/bin/env python3
# Converts the desktop new tab fonts to TrueType for the Android app (needs fontTools and brotli).
# usage: make_android_fonts.py <firefox source dir>
import os, sys
from fontTools.ttLib import TTFont

SRC = sys.argv[1]
FONTS = os.path.join(SRC, "browser", "base", "content", "fonts")
OUT = os.path.join(SRC, "mobile", "android", "fenix", "app", "src", "main", "res", "font")
# Same order as FONTS in obscurant-home.js.
NAMES = [
    "Rubik80sFade-subset", "alumnisanscollegiateone", "londrinasketch", "kablammo", "honk", "astloch", "danfo",
    "bungeehairline", "rubikpuddles", "akronim", "rubikdistressed", "ralewaydots", "silkscreen", "sixtyfour",
]

os.makedirs(OUT, exist_ok=True)
for index, name in enumerate(NAMES):
    font = TTFont(os.path.join(FONTS, name + ".woff2"))
    font.flavor = None
    font.save(os.path.join(OUT, "obscurant_font_%d.ttf" % index))
print(len(NAMES), "fonts written")
