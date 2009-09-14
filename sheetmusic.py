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

from gamera.core import *
from remove import remstaves,reminside
from within import inout_vertical_ys,between,inout_staff_condition
from outline import outline
from numpy import average

from proj import Projection

import logging


class MusicImage(object):

    def __init__(self,image,training_filename=None, classifier=None):
        """ Setup a wrapped image with music methods around """
        self.l = logging.getLogger(self.__class__.__name__)
        if isinstance(image,basestring):
            image = load_image(image)

        self._orig = image
        self._image= image
        self._image = self._image.to_onebit()
        self._ms = None
        self._noinside = None
        if not training_filename is None:
            self.classifier = Classifier_with_remove(training_filename)

        if not classifier is None:
            self.classifier = classifier

    def ms(self):
        if self._ms is None:
            self.without_staves()
        return self._ms

    def without_staves(self):
        if self._ms is None:
            self._ms = remstaves(self._image)
        return self._ms.image

    def without_insidestaves_info(self):
        self.without_staves()

        if self._noinside is None:
            self._noinside = reminside(self._ms.get_staffpos(),
                                        self._ms.image.image_copy())
        return self._noinside

    def with_row_projections(self,color=RGBPixel(200,50,50),image=None):
        ret = self._orig.to_rgb()
        if image is None:
            image = self.without_insidestaves_info()
        p = image.projection_rows()
        l = [ (v,i) for i,v in enumerate(p) ]
        [ ret.draw_line( (0,i[1]), (i[0],i[1]),color) for i in l]
        return ret

    def ccs_in_spike(self,spikes,ccs):
        ret = []
        for s in spikes[:]:
            cond = inout_vertical_ys([(s['start'],s['stop'])])
            cs = [ c for c in ccs if cond(c) ]
            ret.extend(cs)

        return ret

    def possible_text_ccs(self,image=None):
        if image is None:
            baseimg = self.without_insidestaves_info()
        else:
            baseimg = image
        ccs = set(baseimg.cc_analysis())
        spikes = self.possible_text_areas(image=self.without_insidestaves_info())
        inccs = self.ccs_in_spike(spikes,ccs)
        return inccs


    def possible_text_areas(self, min_cutoff_factor=0.02,
                            height_cutoff_factor=0.8,image=None,
                            avg_cutoff=(0.75,2.0),
                            min_cc_count=10):

        if image is None:
            self.l.debug("No image given, using without_inside_staves_info()")
            image = self.without_insidestaves_info()

        p = Projection(image.projection_rows())
        p.threshold(min_cutoff_factor*image.width)
        self.l.debug("thresholded at %f",min_cutoff_factor)
        self.l.debug("min_cc_count: %d",min_cc_count)
        self.l.debug("avgcutoff: %s",avg_cutoff)


        spikes = p.spikes(height_cutoff_factor*self.ms().staffspace_height)
        self.l.debug("HeightCutoff %f",height_cutoff_factor)
        ccs = image.cc_analysis()
        for s in spikes[:]:
            cond = inout_vertical_ys([(s['start'],s['stop'])])
            cs = [ c for c in ccs if cond(c) ]
            avgaspect = average([ c.aspect_ratio() for c in cs ])
            if not (len(cs) > min_cc_count and
                    between(avgaspect,avg_cutoff[0],avg_cutoff[1])):
                spikes.remove(s)
        return spikes

    def highlight_possible_text(self, image=None):

        if image is None:
            ret = self._orig.to_rgb()
        else:
            ret = image
        spikes = self.possible_text_areas()

        [ ret.draw_hollow_rect((0,s['start']),(ret.width-1,s['stop']),RGBPixel(255,0,0))\
         for s in spikes ]
        return ret

    def to_rgb(self):
        return self._orig.to_rgb()

    def ccs(self,remove_text=True,remove_inside_staffs=True,remove_classified=False):
        """ Return the connected components of the image
        Choose to get all, or with some parts removed

        Keyword arguments:
            remove_text --- Remove any thing that looks like text from the list
            off ccs
            remove_inside_staffs --- Remove all cc's  that overlap with the
            stafflines.
        """
        self.l.debug("remove_text=%s, remove_inside_staffs=%s, remove_classified=%s",\
                     remove_text,remove_inside_staffs,remove_classified)


        baseimg = self.without_staves()
        ccs = set(baseimg.cc_analysis())

        outsideccs = []
        if remove_text or remove_inside_staffs:
            cond = inout_staff_condition(self.ms().get_staffpos())
            outsideccs = set([ c for c in ccs if not cond(c)])

        if (remove_text):
            inccs = self.possible_text_ccs(image=self.without_insidestaves_info())
            self.l.debug("Removing %d ccs as text",len(inccs))
            ccs = ccs-set(inccs) # remove text

        if (remove_inside_staffs):
            pre = ccs
            ccs = outsideccs & ccs
            self.l.debug("Removing %d ccs as inside staffs",(len(pre)-len(ccs)))

        if (remove_classified):
            clasccs = self.classified_ccs()
            self.l.debug("Removing %d ccs as classified",(len(pre)-ccs))
            ccs = ccs - clasccs

        return ccs

    def classified_ccs(self,other=None):
        if self.classifier is None:
            raise Error("Classifier not initialized")

        ci = self.classifier.classify_image(self)
        d_t = ci.confident_d_t()
        self.l.debug("Confident d_t %f",d_t)
        ret = ci.classified_glyphs(d_t)
        self.l.debug("Found %d glyphs",len(ret))
        return ret

    def segment(self,classify=False):
        """ Get cc's for three parts of the image
        text, instaff,other
        """
        cond = inout_staff_condition(self.ms().get_staffpos())
        instaff = [ c for c in self.ccs(False,False) if cond(c)]
        other = self.ccs()
        text =  self.possible_text_ccs()
        if classify:
            classified = self.classified_ccs()
        else:
            classified = []

        return text,instaff,other,classified

    def without(self,classified=True,text=True):
        ret = self.color_segment(other_color=RGBPixel(0,0,0),
                               text_color=RGBPixel(255,255,255),
                               instaff_color=RGBPixel(0,0,0),
                               classified_color=RGBPixel(255,255,255)
                              )
        return ret

    def color_segment(self,text_color=RGBPixel(255,255,0),\
                      instaff_color=RGBPixel(0,255,0),\
                      other_color=RGBPixel(255,0,0),
                      classified_color=None,
                     classified_box=False):
        """ Segment image in three with colors
        Segment the image into three parts:
             - text
             - inside staff
             - Others/relevant for Classifier

        Keyword arguments:
            text_color --- What color to use for text ccs
            instaff_color --- The color to use for in-staff ccs
            other_color --- The color of the rest.
            classified_color --- If set we will try to classify stuff in the
            image and give them the given color
            classified_box --- If set we will try to classify and but instead of
            highlight I will box them.

        """
        ret = self.to_rgb().to_onebit().to_rgb()
        classify = False
        if not(classified_color is None and classified_box is None):
            classify = True
            if classified_color is None:
                classified_color = RGBPixel(255,0,0)

        text,instaff,other,classified = self.segment(classify=classify)
        # Painting inside staff things green
        for c in instaff:
            ret.highlight(c,instaff_color)

        # Painting relevant ccs' red.
        for c in other:
            ret.highlight(c,other_color)


        for c in classified:
            if classified_box:
                outline(ret,c,width=2.0,color=classified_color)
            else:
                ret.highlight(c,classified_color)

        # Painting text yellow
        for c in text:
            ret.highlight(c,text_color)

        return ret


if __name__ == '__main__':
    from gamera.core import * 
    from class_dynamic import Classifier_with_remove
    import sys
    #LOG_FILENAME = '/tmp/logging_example.out'
    FORMAT = "%(asctime)-15s %(levelname)s [%(name)s.%(funcName)s]  %(message)s"
    logging.basicConfig(level=logging.DEBUG,format=FORMAT)
    init_gamera()
    c = Classifier_with_remove(training_filename="mergedyn2.xml")
    c.set_k(2)
    filename = sys.argv[-1]
    mi = MusicImage(load_image(filename),classifier=c)
    ret = mi.without()
    ret.save_PNG("%s_Removed.png"%filename)
    logging.debug("Done with %s"%"brahmsRemove")
    ret = mi.color_segment(classified_box=True)
    ret.save_PNG("%s_ColorSegment.png"%filename)
    logging.debug("Done with %s"%"brahmsColorSegment")




