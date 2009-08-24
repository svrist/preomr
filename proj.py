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


class Projection(object):

    def __init__(self,proj):
        self.orig = proj
        self.proj = proj[:]


    def threshold(self,threshold):
        self.proj = [ v if v > threshold else 0\
                     for v in self.proj ]

    def spikes(self,height_threshold=None):
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





if __name__ == '__main__':
    from gamera.core import *
    import sys
    import re
    from sheetmusic import MusicImage
    init_gamera()
    for i,imgname in enumerate(sys.argv[1:]):
        m = re.match(r"^(.*)\.[^\.]+$",imgname)
        noend = m.group(1)
        i = MusicImage(imgname)
        i.highlight_possible_text().scale(0.5,2).save_PNG("%s_possibletext.png"%noend)
        i.highlight_possible_text(
            image=i.with_row_projections(RGBPixel(50,50,50))
            ).scale(0.5,2).save_PNG("%s_possibletext_withprojections.png"%noend)

        print ("Save %s_possibletext.png and "+\
        "%s_possibletext_withprojections.png")%(noend,noend)
