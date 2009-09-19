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

from numpy import average
from proj import Projection
from ccs_util import ccs_in_spike
from within import inout_vertical_ys,between
from gamera.core import *
from gamera.kdtree import *

import logging

class Text_in_music():

    def __init__(self,image,
                 min_cutoff_factor=0.02,
                 height_cutoff_factor=0.8,
                 avg_cutoff=(0.75,2.0),
                 min_cc_count=5,
                 min_wordlenght = 2,
                 text_near = None
                ):
        self.l = logging.getLogger(self.__class__.__name__)
        self._image = image

        # Settings
        if text_near is None:
            text_near = int(image._orig.ncols /  200.0 * 1.5) # 200 chars on the width of page.  Allow almost 1.5 chars space between
        self._min_cutoff_factor = min_cutoff_factor
        self._height_cutoff_factor = height_cutoff_factor
        self._avg_cutoff = avg_cutoff
        self._min_cc_count = min_cc_count
        self._text_near = text_near
        self._min_wordlenght = min_wordlenght # two ccs in a "word" is a good word.
        self.l.debug("thresholded:%.2f, min_cc_count:%d, avgcutoff: %s, heightcutoff:%.2f",
                     self._min_cutoff_factor,self._min_cc_count,self._avg_cutoff,
                     self._height_cutoff_factor)

    def possible_text_ccs(self, image=None, ccs=None):
        if image is None:
            self.l.debug("No image given. Using without_insidestaves_info()")
            baseimg = self._image.without_insidestaves_info()
        else:
            baseimg = image

        if ccs is None:
            ccs = set(baseimg.cc_analysis())
        spikes = self._possible_text_areas(image=self._image.without_insidestaves_info(),
                                           ccs=ccs)
        inccs = ccs_in_spike(spikes,ccs)

        words = baseimg.projection_cutting(Tx=self._text_near)

        goodccs = []
        for w in words:
            r = Rect(w)
            contained = [ c for c in inccs if r.contains_rect(c) ]
            if len(contained) > self._min_wordlenght:
                goodccs.extend(contained)

        #n,bins,patches = hist([c. 

        self.l.debug("Removed %d/%d ccs due to wordsize", (len(inccs)-len(goodccs)),len(inccs))
        return goodccs


    def _possible_text_areas(self,
                             image=None,
                            ccs=None):

        if image is None:
            self.l.debug("No image given, using without_inside_staves_info()")
            image = self._image.without_insidestaves_info()

        if ccs is None:
            ccs = image.cc_analysis()

        p = Projection(image.projection_rows())
        p.threshold(self._min_cutoff_factor*image.width)


        spikes = p.spikes(self._height_cutoff_factor*self._image.ms().staffspace_height)
        for s in spikes[:]:
            cond = inout_vertical_ys([(s['start'],s['stop'])])
            cs = [ c for c in ccs if cond(c) ]
            avgaspect = average([ c.aspect_ratio()[0] for c in cs ])

            if not (len(cs) > self._min_cc_count and
                    between(avgaspect,self._avg_cutoff[0],self._avg_cutoff[1])):
                spikes.remove(s)
        return spikes

