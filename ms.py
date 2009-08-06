from gamera.core import *
from gamera.toolkits.musicstaves import musicstaves_rl_simple
from gamera.toolkits.musicstaves import musicstaves_rl_fujinaga
from gamera.toolkits.musicstaves import musicstaves_skeleton
from gamera.toolkits.musicstaves import musicstaves_rl_carter
import sys
import re
from outline import *

init_gamera()

imgname = sys.argv[-1]
m = re.match(r"^(.*)\.[^\.]+$",imgname)
noend = m.group(1)

image = load_image(imgname)
image = image.to_onebit()
ms = musicstaves_rl_fujinaga.MusicStaves_rl_fujinaga(image)
ms.remove_staves(crossing_symbols = 'bars')

rgbimg = image.to_rgb()

ccs = ms.image.cc_analysis()

_scaled_f_cols = 3.0769230769230771
_scaled_f_rows = 3.3846153846153846
_precis = 10
scaled_f_cols = int(_scaled_f_cols*_precis)
scaled_f_rows = int(_scaled_f_rows*_precis)

print (scaled_f_cols,scaled_f_rows, ms.staffspace_height)

for i in range(len(ccs)):
    c = ccs[i]
    c_scaled_cols = int(c.ncols/float(ms.staffspace_height)*_precis)
    c_scaled_rows = int(c.nrows/float(ms.staffspace_height)*_precis)
    print "%d: %dx%d scaled %s"%(i,c.ncols,c.nrows,(c_scaled_cols,c_scaled_rows))

    if scaled_f_cols == c_scaled_cols and scaled_f_rows == c_scaled_rows:
        outline(rgbimg,c,2,RGBPixel(0,255,0))
        print "Match in %s(%s)"%(i,c.label)


rgbimg.save_PNG("rgboutlined_%s.png"%noend)
