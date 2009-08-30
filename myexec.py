from sheetmusic import MusicImage
from within import inout_staff_condition
mi = MusicImage("lvbp0.tif")
rgb = mi.to_rgb()

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
print "Next Image"

mi = MusicImage("debussyp0.tif")
rgb = mi.to_rgb()

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


