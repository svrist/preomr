from sheetmusic import MusicImage
from within import inout_staff_condition
import os.path
if os.path.isfile("lvbp0.tif"):
    mi = MusicImage("lvbp0.tif")
    rgb = mi.to_rgb().to_onebit().to_rgb()
    # Painting inside staff things green
    cond = inout_staff_condition(mi.ms().get_staffpos())
    ccs = [ c for c in mi.ccs(False,False) if cond(c)]
    for c in ccs:
        rgb.highlight(c,RGBPixel(0,255,0))
    # Painting relevant ccs' red.
    ccs = mi.ccs()
    for c in ccs:
        rgb.highlight(c,RGBPixel(255,0,0))
    # Painting text yellow
    ccs = mi.possible_text_ccs()
    for c in ccs:
        rgb.highlight(c,RGBPixel(255,255,0))
    rgb.save_PNG("lvbp0_relevant_ccs.png")

mi = MusicImage("debussyp0.tif")
rgb = mi.to_rgb().to_onebit().to_rgb()

cond = inout_staff_condition(mi.ms().get_staffpos())
ccs = [ c for c in mi.ccs(False,False) if cond(c)]
for c in ccs:
    rgb.highlight(c,RGBPixel(0,255,0))
ccs = mi.ccs()
for c in ccs:
    rgb.highlight(c,RGBPixel(255,0,0))
ccs = mi.possible_text_ccs()
for c in ccs:
    rgb.highlight(c,RGBPixel(255,255,0))
rgb.save_PNG("debussyp0_relevant_ccs.png")


