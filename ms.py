from gamera.core import *
from gamera.toolkits.musicstaves import musicstaves_rl_fujinaga
import sys
import re
import time
from svutil import match_bb
start=time.time()
init_gamera()

imgname = sys.argv[-1]
m = re.match(r"^(.*)\.[^\.]+$",imgname)
noend = m.group(1)

image = load_image(imgname)
image = image.to_onebit()
ms = musicstaves_rl_fujinaga.MusicStaves_rl_fujinaga(image)
ms.remove_staves(crossing_symbols = 'bars')
rgbimg = image.to_rgb()
print "Loaded image and removed staves in %f seconds"%(time.time()-start)
start=time.time()
ccs = ms.image.cc_analysis()
print "CC analysis in %f seconds"%(time.time()-start)

_precis = 10

lib = []

_scaled_f_cols = 3.0769230769230771
_scaled_f_rows = 3.3846153846153846
scaled_f_cols = int(_scaled_f_cols*_precis)
scaled_f_rows = int(_scaled_f_rows*_precis)
lib.append({'cols' : scaled_f_cols, 'rows' : scaled_f_rows, 'color' : RGBPixel(0,255,0)})

_scaled_ff_rows = 3.3846153846153846
_scaled_ff_cols = 4.5384615384615383
scaled_ff_cols = int(_scaled_ff_cols*_precis)
scaled_ff_rows = int(_scaled_ff_rows*_precis)
lib.append({'cols' : scaled_ff_cols, 'rows' : scaled_ff_rows, 'color': RGBPixel(255,0,0)})

print "Gamera initialized and image analyzed in %f"%(time.time()-start)

start=time.time()
match_bb(rgbimg,ccs,lib,ms.staffspace_height,_precis)
stop=time.time()
print "Updated rgbimage in %f seconds"%(stop-start)

outfile = "rgboutlined_%s.png"%noend
rgbimg.save_PNG(outfile)

print "saved output in %s"%outfile
