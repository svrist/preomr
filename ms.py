# -*- coding: iso-8859-15 -*
# Copyright (C) 2009 Søren Bjerregaard Vrist
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

"""
Uses fixed but scaled bounding box measures with a precision of _precis to mark
dynamic f and dynamic ff with red and green.
The scaled numbers is based on bounding box for ff and f in 
http://www.free-scores.com/download-sheet-music.php?pdf=14870#
"""
from gamera.core import *
#from gamera.toolkits.musicstaves import musicstaves_rl_fujinaga
from gamera.toolkits.musicstaves import musicstaves_skeleton
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
ms = musicstaves_skeleton.MusicStaves_skeleton(image)
#ms = musicstaves_rl_fujinaga.MusicStaves_rl_fujinaga(image)
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
