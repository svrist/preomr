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

class Word():
    def __init__(self,word,ccs):
        self.w = word
        self.ccs = ccs

    def clen(self):
        return len(self.ccs)



def wordlist(words,ccs,min_word_l):
    ret = []
    for w in words[:]:
        r = Rect(w)
        contained = [ c for c in ccs if r.contains_rect(c) ]
        if len(contained) >= min_word_l:
            word = Word(w,contained)
            ret.append(word)
    return ret

class Line():
    def __init__(self,line,words):
        self.ws = words
        self.l = line
        self.t = KdTree([KdNode([c.w.center_x,c.w.center_y],c.w) for c in words ])

    def distance_next_cc(self,c):
        nextn = self.t.k_nearest_neighbors([c.w.center_x,c.w.center_y],2)
        assert len(nextn)>0
        if len(nextn) == 1:
            return 0
        return c.w.distance_bb(nextn[1].data)# first after me

    def line_feature(self):
        return average([d for c,d in self])*1.0/len(self)

    def __getitem__(self,key):
        words = self.ws
        return (words[key],self.distance_next_cc(words[key]))

    def __iter__(self):
        for i,k in enumerate(self.ws):
            yield self[i]


    def __len__(self):
        return len(self.ws)

def llist(lines,words):
    ret = []
    for l in lines:
        ws = [ c for c in words if l.contains_y(c.w.center_y) ]
        ret.append(Line(l,ws))
    return ret




class Text_in_music():

    def __init__(self,image,
                 min_cutoff_factor=0.02,
                 height_cutoff_factor=0.8,
                 avg_cutoff=(0.75,2.0),
                 min_cc_count=5,
                 min_wordlength = 2,
                 deviation_avg_feature = 3,
                 text_near = None
                ):
        self.l = logging.getLogger(self.__class__.__name__)
        self._image = image

        # Settings
        if text_near is None:
            text_near = int(image._orig.ncols /  200.0 * 1.0) # 200 chars on the width of page.  Allow almost 1.5 chars space between
        self._min_cutoff_factor = min_cutoff_factor
        self._height_cutoff_factor = height_cutoff_factor
        self._avg_cutoff = avg_cutoff
        self._min_cc_count = min_cc_count
        self._text_near = text_near
        self._min_wordlength = min_wordlength # two ccs in a "word" is a good word.
        self._deviation_avg_feature = deviation_avg_feature
        self.l.debug("thresholded:%.2f, min_cc_count:%d, avgcutoff: %s, heightcutoff:%.2f",
                     self._min_cutoff_factor,self._min_cc_count,self._avg_cutoff,
                     self._height_cutoff_factor)

    def _confirmed_text_lines(self,words):
        """ Take a list of words and return a list of confirmed text lines
        """
        p = self.word_projections(words=words).rspikes(self._image._orig.ncols-1) # Get lines of document


        # split out words per line, based on word.center_y
        lines = llist(p,words)
        #rs = [ [ c for c in words if r.contains_y(c.center_y) ] for r in p ]

        # Augment rs list with a KdTree over all "words" in the given line
            #rtree = [ (r,KdTree([KdNode([c.center_x,c.center_y],c) for c in r ])) \
            #for r in rs ]

        # create a list with "word" and distance to nearest next word for each
        # line.
        #distc = [ [ (c,distance_next_cc(c,t))\
                #for c in words if r.contains_y(c.center_y)] for r,t in rtree ]
        #distc = [ (l,average([d for c,d in l])*1.0/len(l)) for l in lines ]
        avgl = average( [ l.line_feature() for l in lines ] )

        flat = [ l for l in lines if l.line_feature() < avgl*self._deviation_avg_feature ]
        return flat

    def _words(self,image,pageseg_function=None):
        if pageseg_function is None:
            pageseg_function = pc(self)
        words = pageseg_function(image)
        return words

    def _lines(self,image,pageseg_function=None,ccs=None):
        words = self._words(image,pageseg_function)
        return self._confirmed_text_lines(wordlist(words,ccs,self._min_wordlength))
   

    def _good_ccs(self,image=None,ccs=None, pageseg_function=None):
        if image is None:
            image = self._image.without_insidestaves_info()
        if ccs is None:
            ccs = image.cc_analysis()
        lines = self._lines(image,pageseg_function,ccs)
        ret = []
        for  l in lines:
            for w,d in l:
                ret.extend(w.ccs)
        return ret 

    def word_projections(self,image=None,words = None,word_seg=None):
        if image is None:
            image = self._image.without_insidestaves_info()

        if words is None:
            ccs = image.cc_analysis()
            words = wordlist(word_seg(self)(image),ccs)

        return Projection([ len( [ c for c in words if c.w.contains_y(y) ]) \
                for y in range(0,image.nrows)])



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
        goodccs = self._good_ccs(baseimg,inccs)
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


def pc(text):
    return lambda image : image.projection_cutting(Tx=text._text_near,Ty=1)

def bb(text):
    return lambda image : image.bbox_merging()

def rsm(text):
    return lambda image : image.runlength_smearing()
