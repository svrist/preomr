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
from gamera.toolkits.musicstaves import musicstaves_skeleton
from gamera.core import RGBPixel
import gamera.core
from within import inout_staff_condition

def remstaves(image):
    ms = musicstaves_rl_fujinaga.MusicStaves_rl_fujinaga(image)
    ms.remove_staves(crossing_symbols = 'bars')
    return ms

def remstaves_skeleton(image):
    ms = musicstaves_skeleton.MusicStaves_skeleton(image)
    ms.remove_staves(crossing_symbols = 'bars')
    return ms

def _rembase(staffpos,image):
    if isinstance(image,gamera.core.Image):
        ccs = image.cc_analysis()
    else:
        ccs = image
    cond = inout_staff_condition(staffpos)
    return ccs,cond

def reminside(staffpos,image):
    ccs,cond = _rembase(staffpos,image)
    [c.fill_white() for c in ccs if cond(c) ]
    return image

def remoutside(staffpos,image):
    ccs,cond = _rembase(staffpos,image)
    [c.fill_white() for c in ccs if not cond(c) ]
    return image

def is_sort_of_a_list(l):
    for method in ['__getitem__', '__setitem__']:
        if method not in dir(l):
            return False
    return True




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
        start = time.time()
        m = re.match(r"^(.*)\.[^\.]+$",imgname)
        noend = m.group(1)
        image = load_image(imgname)
        image = image.to_onebit()
        try:
            ms = remstaves(image)
        except:
            ms = remstaves_skeleton(image)

        stop = time.time()
        elapsed += stop-start
        timeleft = (elapsed/float(i+1))*(amount-(i+1))
        ms.image.save_PNG("%s_fujinaga.png"%noend)
        print "%d %% done (%d/%d) %ds elapsed. %ds remaining"\
                %(progress,i,amount,elapsed,timeleft)
        print "Saved %s_fujinaga.png"%noend
        sys.stdout.flush()

