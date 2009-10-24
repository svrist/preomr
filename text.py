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

from numpy import average,median
from proj import Projection
from ccs_util import ccs_in_rspike
from within import inout_vertical_ys,between
from gamera.core import *
from gamera.kdtree import *

import logging

def slack_match(y1,y2,slack=1):
    return y1 <= y2+slack and y1 >= y2-slack


class Word():
    """ Wrapper for two types of CC from an image.
    CC as the one returned from a pagesegmentation algorithm
    and CC as the least primitive component in an image
    """
    def __init__(self,word,ccs):
        """ Word with the an overall rect containing the given small ccs

        Keyword arguments:
            word    --- An "CC" as determined by an PageSegmentation algorithm
            ccs     --- The ccs contained in this word.
        """
        self.w = word
        self.ccs = ccs

    """ Length of word in ccs
    """
    def clen(self):
        return len(self.ccs)

def wordlist(words,ccs,min_word_l=1):
    """ Generate a list of words based on a list of PageSegmentation"Words" and
    all CCs in the image

    Keyword arguments:
        words       --- PageSegmentation "words"
        ccs         --- All ccs in the image which could be in words
        min_word_l  --- If >1 words with only one cc in them will be discarded.

    """
    ret = []
    for w in words[:]:
        r = Rect(w)
        contained = [ c for c in ccs if r.contains_rect(c) ]
        if len(contained) >= min_word_l:
            word = Word(w,contained)
            ret.append(word)
    return ret


class Line():
    """ A line is a list of words. This object will hold the line which is a
    Rect and the a list of all Words contained in this line/rect"""
    def __init__(self,line,words):
        self.ws = words
        self.l = line
        self.t = KdTree([KdNode([c.w.center_x,c.w.center_y],c.w) for c in words ])

    def distance_next_cc(self,c):
        """ Within this line - how close is the given Word to it's closest
        neightbor based on its center

        Keyword arguments:
            c   --- A word as defined in *Word*

        Returns:
            the distance to the closest neighbor within this line
        """
        nextn = self.t.k_nearest_neighbors([c.w.center_x,c.w.center_y],2)
        assert len(nextn)>0
        if len(nextn) == 1:
            return 0
        return c.w.distance_bb(nextn[1].data)# first after me

    def line_feature(self,norm_factor=1):
        """ Calculate the average distance between words in this line
        normalized by the given factor and weighted by the inverse count of words in
        this line. 

        *norm_factor*:
            Use to make this feature invariant by given an image-based constant
            the follows the same scale pattern as ccs.
            For example page-width or staffspace_height.
        """
        return average([d for c,d in self])*1.0/len(self)

    #### Sequence interface
    def __getitem__(self,key):
        """ Index the words in this Line """
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
    """ Use guestimates to find areas of text in an image """

    def __init__(self,image,
                 min_cutoff_factor=0.02,
                 height_cutoff_factor=0.8,
                 avg_cutoff=(0.70,2.0),
                 min_cc_count=5,
                 min_wordlength = 2,
                 deviation_avg_feature = 3,
                 text_near = 1.0
                ):
        """ Text in Music approimation
        This will try to identify areas of the given image which might be text.

        *min_cutoff_factor*: 
            Percentage of the page width which should be black to be considered
            as a text area. Defaults to 2% (0.02) based on tests


         *height_cutoff_factor*:
             How high should the black area be to be considered a letter in
             percent of staffspace_height
             Defaults to 80% (0.08) based on tests


         *avg_cutoff*:
             What should the average aspect-ratio be of all ccs in an area to be
             considered as an area with text?
             Defaults to 0.75 -> 2.0 ie somewhere around quadratic

         *min_cc_count*:
            How many cc's should there be in an area for it to be considered a
            text area?
            Defaults to 5.

        *min_wordlength*:
            How many cc's should there be in a words(as found by a
            pagesegmentation algorithm" before it is considered a word.
            Defaults to 2 to rule out music symbols if any.

        *deviation_avg_feature*:
            How much should the deviation from the average word-to-word distance
            be before discarding a possible text area?
            Defaults to 3

        *text_near*: 
            How close should cc's be before they are considerd part of
            the current word.
            Defaults to allow a whole char (median width of all ccs) of space. (1.0)

         """
        self.l = logging.getLogger(self.__class__.__name__)
        self._image = image

        # Settings
        self._text_near = text_near
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
        p = self._word_projections(words=words).rspikes(self._image._orig.ncols-1) # Get lines of document
        lines = llist(p,words)
        avgl = average( [ l.line_feature() for l in lines ] )
        self.l.debug("Avg line_feature")
        flat = [ l for l in lines if l.line_feature() < avgl*self._deviation_avg_feature ]
        return flat

    def _words(self,image,ccs,pageseg_function=None):
        if pageseg_function is None:
            pageseg_function = pc(self,ccs)
        words = pageseg_function(image)
        return words

    def _lines(self,image,pageseg_function=None,ccs=None):
        words = self._words(image,ccs,pageseg_function)
        return self._confirmed_text_lines(wordlist(words,ccs,self._min_wordlength))

    def _text_near_width(self,ccs):
        return median([ c.ncols for c in ccs])*self._text_near
   

    def _def_wordproj(self,image=None,words=None,word_seg):
        if image is None:
            image = self._image.without_insidestaves_info()
        if words is None:
            ccs = image.cc_analysis()
            words = wordlist(word_seg(self)(image),ccs)
        return image,words

    def _word_projections(self,image=None,words = None,word_seg=None):
        words,image = self._def_wordproj(image,words,word_seg)
        return Projection([ len( [ c for c in words if c.w.contains_y(y) ]) \
                for y in range(0,image.nrows)])


    def _word_projections_slackmatch(self,image=None,words = None,word_seg=None,slack=1):
        words,image = self._def_wordproj(image,words,word_seg)
        return Projection([ len( [ c for c in words if slack_match(c.w.center_y,y) ]) \
                for y in range(0,image.nrows)])



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

    def _possible_text_areas_projection(self,image):
        p = Projection(image.projection_rows())
        p.threshold(self._min_cutoff_factor*image.width)
        rspikes = p.rspikes(image.ncols-1,self._height_cutoff_factor*self._image.ms().staffspace_height)
        return p,rspikes


    def _possible_text_areas(self,
                             image=None,
                            ccs=None):

        if image is None:
            self.l.debug("No image given, using without_inside_staves_info()")
            image = self._image.without_insidestaves_info()

        if ccs is None:
            ccs = image.cc_analysis()

        p,spikes = self._possible_text_areas_projection(image)

        for s in spikes[:]:
            cs = ccs_in_rspike([s],ccs)
            avgaspect = median([ c.aspect_ratio()[0] for c in cs ])

            if not (len(cs) > self._min_cc_count and
                    between(avgaspect,self._avg_cutoff[0],self._avg_cutoff[1])):
                self.l.debug("Avg aspect: %f, %d ccs",avgaspect,len(cs))
                spikes.remove(s)
        return spikes


#=======================Public=================


    def possible_text_ccs(self, image=None, ccs=None):
        if image is None:
            self.l.debug("No image given. Using without_insidestaves_info()")
            baseimg = self._image.without_insidestaves_info()
        else:
            baseimg = image

        if ccs is None:
            ccs = set(baseimg.cc_analysis())
        # Horizontal projections
        spikes = self._possible_text_areas(image=baseimg,
                                           ccs=ccs)
        inccs = ccs_in_rspike(spikes,ccs)

        # Iterative projection profile cutting
        goodccs = self._good_ccs(baseimg,inccs)
        self.l.debug("Removed %d from original %d ccs", (len(inccs)-len(goodccs)),len(inccs))
        return goodccs


if __name__ == '__main__':
    import sys
    import os
    from ill_music import IllMusicImage
    FORMAT = "%(asctime)-15s %(levelname)s [%(name)s.%(funcName)s]  %(message)s"
    logging.basicConfig(level=logging.DEBUG,format=FORMAT)
    def ensure_dir(dir):
        if not os.path.exists(dir):
            logging.debug("%s dir dint exits. Creating it.",dir)
            os.mkdir(dir)

    init_gamera()
    filename=sys.argv[-1]
    basename=filename[:-4]
    mi = IllMusicImage(filename,training_filename="preomr_edited_cnn.xml")
    ensure_dir("texttest")
    ensure_dir("texttest/%s"%basename)
    outputbase = "texttest/%s"%basename
    t = mi._text()

    # show row projections
    p,sp = t._possible_text_areas_projection(mi.without_insidestaves_info())
    # add after threshold image
    mp = max(p)
    fac = mi._image.ncols/mp
    logging.debug("Resize proj factor: %d, max:%d, ncols:%d, max*nc:%d",fac,mp,mi._image.ncols,mp*fac)
    r =mi.with_row_projections(fac=fac)
    r = mi.draw_y_proj(p,image=r,color=RGBPixel(100,0,0),fac=fac)
    r.save_PNG("%s/%s-01-rowprojections.png"%(outputbase,basename))
    logging.debug("01-rowprojections.png")

    # draw in text areas based on these projections
    r = mi.to_rgb()
    width = mi._image.ncols-1
    for re in p.rspikes(width):
        r.draw_hollow_rect(re,RGBPixel(210,210,210))
    for re in sp:
        r.draw_hollow_rect(re,RGBPixel(150,150,150))
    ra = t._possible_text_areas()
    for re in ra:
        r.draw_hollow_rect(re,RGBPixel(255,0,0))
    firstccs = ccs_in_rspike(ra,mi.without_insidestaves_info().cc_analysis())

    for c in firstccs:
        r.highlight(c,RGBPixel(0,100,0))
    r.save_PNG("%s/%s-02-areas-and-ccs.png"%(outputbase,basename))
    logging.debug("02-areas-and-ccs.png")

    # Draw words
    r = mi.to_rgb()








    r = mi.color_segment()
    r.save_PNG("%s/%s-XX-colorsegmented.png"%(outputbase,basename))






    

