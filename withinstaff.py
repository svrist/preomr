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

from gamera.toolkits.musicstaves import musicstaves_rl_fujinaga
from outline import outline
from remstaves import remstaves


def minmaxy(cc):
    return cc.offset_y,cc.offset_y+cc.nrows

def between(y,bottom,top):
    return y <= top and y >= bottom

def inout_staff_condition(mss):
    stavey = [ (s.yposlist[0],s.yposlist[-1]) for s in mss.get_staffpos()]
    def ret(c):
        c1,c2 = minmaxy(c)
        f = lambda x: between(x[0],c1,c2) 
        f2 = lambda x,y: between(y,x[0],x[1])
        return (True in [ f2(s,c1) or f2(s,c2) or f(s) for s in stavey ])
    return ret

def split_on_condition(seq, condition):
    a, b = [], []
    for item in seq:
        (a if condition(item) else b).append(item)
    return a,b
 

if __name__ == '__main__':
    from gamera.core import *
    import sys
    import re
    import time
    init_gamera()

    progress=0
    amount = len(sys.argv[1:])
    elapsed = 0
    for i,imgname in enumerate(sys.argv[1:]):
        progress = ((i+1)/float(amount))*100
        m = re.match(r"^(.*)\.[^\.]+$",imgname)
        noend = m.group(1)
        image = load_image(imgname)
        rgbimg = image.to_rgb()
        image = image.to_onebit()
        ms = remstaves(image)
        ccs = ms.image.cc_analysis()
        cond = inout_staff_condition(ms)
        for c in ccs:
            if cond(c):
                # insid
                col = RGBPixel(255,0,0)
            else:
                col = RGBPixel(0,255,0)
            outline(rgbimg,c,2.0,col)

        savename = "insideoutside_%s.png"%noend
        rgbimg.save_PNG(savename)
        print "Saved %s"%savename
        sys.stdout.flush()
