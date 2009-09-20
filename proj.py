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

from gamera.core import Rect

class Projection(object):
    """ projection wrapper
    for finding  peaks, and peak areas
    """
    def __init__(self,proj):
        self.orig = proj
        self.proj = proj[:]


    def threshold(self,threshold):
        """ Cut out all projections lower than a given threshold

        Keyword arguments:
            threshold --- the absolute threshold to cut off with. Base it on a
            procentile of the complete page width.

        """
        self.proj = [ v if v > threshold else 0\
                     for v in self.proj ]

    def rspikes(self,width,height_threshold=None):
        return [ Rect((0,s['start']),(width,s['stop'])) \
                for s in self.spikes(height_threshold)
               ]

    def spikes(self,height_threshold=None):
        """ Get a list of all spikes split around zero areas.

        Keyword arguments:
            height_threshold --- only return spikes which is at least as wide as
            height_threshold.
        """
        state = 0
        start = None
        stop = None
        ret = []
        data = []
        for i,v in enumerate(self.proj):
            if state == 1 and v == 0:
                state = 0
                stop  = i
                data.append((i,v))
                ret.append({ 'start': start, 'stop':stop,'data':data })
                data = []
                stop = None
                start = None
            elif state == 0 and v > 0:
                state = 1
                start = i
                data.append((i,v))
            elif state == 1 and v > 0:
                data.append((i,v))

        if height_threshold is None:
            return ret
        else:
            return  [v for v in ret if len(v['data']) > height_threshold]

    def reset(self):
        self.proj = self.orig[:]

    def __getitem__(self,key):
        self.proj[key]

    def __len__(self):
        return len(self.proj)

    def __iter__(self):
        return self.proj.__iter__()

    def __contains__(self,item):
        return item in self.proj


if __name__ == '__main__':
    from gamera.core import *
    import sys
    import re
    import time
    from sheetmusic import MusicImage
    from within import inout_vertical_ys
    from numpy import average
    init_gamera()
    for i,imgname in enumerate(sys.argv[1:]):
        m = re.match(r"^(.*)\.[^\.]+$",imgname)
        noend = m.group(1)
        start = time.time()
        i = MusicImage(imgname)
        print "Load image %f"%(time.time()-start)
        start = time.time()
        spikes = i.possible_text_areas()
        print "Spikes %f"%(time.time()-start)
        start=time.time()
        ccs = i.without_insidestaves_info().cc_analysis()
        print "ccanalysis %f"%(time.time()-start)
        sys.stdout.flush()
        for s in spikes:
            cond = inout_vertical_ys([(s['start'],s['stop'])])
            cs = [ c for c in ccs if cond(c) ]
            print "%d ccs in ys: %d-%d"%(len(cs),s['start'],s['stop'])
            avgaspect = average([ c.aspect_ratio() for c in cs ])
            print "%f mean aspect"%(avgaspect)
            print
            sys.stdout.flush()

        #i.highlight_possible_text().scale(0.5,2).save_PNG("%s_possibletext.png"%noend)
        i.highlight_possible_text(
            image=i.with_row_projections(RGBPixel(50,50,50))
            ).scale(0.5,2).save_PNG("%s_possibletext_withproj.png"%noend)

        print ("Save %s_possibletext.png and "+\
        "%s_possibletext_withproj.png")%(noend,noend)
