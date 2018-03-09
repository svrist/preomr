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
from within import inout_staff_condition
from ccs_util import ccs_remove, ccs_intersect
from text import Text_in_music
from class_dynamic import Classifier_with_remove


import logging

class NoStavesException(Exception):
    pass

class MusicImage(object):

    def __init__(self,image,training_filename=None, classifier=None):
        """ Setup a wrapped image with music methods around 
        If a classifier or training_filename is set, the classifier will be used
        to match objects after text and "in-staff" objects have been removed.

        If both training_filename and classifier is set, classier wins.

        Keyword Arguments:
            image - Gamera Image or image filename
            training_filename - Filename to use for classifier,(optional)
            classifier - Classifier to use. If both training_filename and
            classifier is set, classifier wins.
        """
        self.l = logging.getLogger(self.__class__.__name__)
        if isinstance(image,basestring):
            image = load_image(image)

        self._ccs = None
        self._orig = image
        self._image= image
        self._image = self._image.to_onebit()
        self._ms = None
        self._noinside = None
        self._text_obj = None

        self.classifier = None
        if not training_filename is None:
            self.classifier = Classifier_with_remove(training_filename)

        if not classifier is None:
            self.classifier = classifier

    def _text(self):
        if self._text_obj is None:
            self.setup_textmatcher()

        return self._text_obj

    def ms(self):
        if self._ms is None:
            self.without_staves()
        return self._ms

    def without_staves(self):
        """ Return the image without staves """
        if self._ms is None:
            self._ms = remstaves(self._image)
        return self._ms.image

    def without_insidestaves_info(self):
        """ Return an image without staves, and everything that touches
        stafflines
        """
        self.without_staves()

        if self._noinside is None:
            self._noinside = reminside(self._ms.get_staffpos(),
                                        self._ms.image.image_copy())
        return self._noinside

    def setup_textmatcher(self,
                          image=None,
                          min_cutoff_factor=0.02,
                          height_cutoff_factor=0.8,
                          avg_cutoff=(0.70,2.0),
                          min_cc_count=5,
                          min_wordlength = 2,
                          deviation_avg_feature = 3,
                          text_near = 0.5
                         ):
        """
        See text.py - Text_in_music.__init__
        """
        self._text_obj = Text_in_music(self,
                                       min_cutoff_factor= min_cutoff_factor,
                                       height_cutoff_factor=height_cutoff_factor,
                                       avg_cutoff=avg_cutoff,
                                       min_cc_count=min_cc_count,
                                       min_wordlength=min_wordlength,
                                       deviation_avg_feature=deviation_avg_feature,
                                       text_near=text_near
                                      )




    def to_rgb(self):
        """ Return the image as RGB edition """
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
        c = self.ccs_overall()

        ccs = c["all"]


        if (remove_text):
            inccs = c["text"]
            self.l.debug("Removing %d ccs as text",len(inccs))
            ccs = ccs_remove(ccs,inccs)

        if (remove_inside_staffs):
            pre = ccs
            ccs = ccs_intersect(ccs,c["outside"])
            self.l.debug("Removing %d ccs as inside staffs",(len(pre)-len(ccs)))

        if (remove_classified):
            clasccs = ret["classified"]
            self.l.debug("Removing %d ccs as classified",(len(classcs)))
            ccs = ccs_remove(ccs,clasccs)
        return ccs


    def ccs_overall(self):
        """ Segment image in inside/outside staves,text,dynamics and return the
        ccs for each of these segments as a dict:
            return {
                     'all'
                     'outside'
                     'inside'
                     'text'
                     'classified'
                }
        """
        ret = {}
        if self._ccs is None:
            baseimg = self.without_staves()
            ccs = set(baseimg.cc_analysis())
            stavey = self.ms().get_staffpos()
            if stavey is None:
                raise NoStavesException,"No stafflines, no need for anything here.  Abort"
            cond = inout_staff_condition(self.ms().get_staffpos())
            ret["all"] = ccs
            ret["outside"] = [ c for c in ccs if not cond(c)]
            ret["inside"] = [ c for c in ccs if cond(c)]
            assert (len(ret['outside'])+len(ret["inside"]) == len(ccs))
            ret["text"] = self._text().possible_text_ccs(image=self.without_insidestaves_info(),ccs=ret["outside"])
            self._ccs = ret
        else:
            self.l.debug("Cached")
            ret = self._ccs

        if not "classified" in ret and not self.classifier is None:
           ret["classified"] = self._classified_ccs(ccs_remove(ret['outside'],ret['text']))
           self._ccs = ret

        return ret



    def _classified_ccs(self,ccs=None):
        if self.classifier is None:
            raise Error("Classifier not initialized")

        ci = self.classifier.classify_image(self,ccs=ccs)
        d_t = ci.confident_d_t()
        self.l.debug("Confident d_t %f",d_t)
        ret = ci.classified_glyphs(d_t)
        self.l.debug("Found %d glyphs",len(ret))
        return ret

    def segment(self,classify=False):
        """ Get cc's for three parts of the image
        text, instaff,other
        OBSOLETE
        """
        seg = self.ccs_overall()
        if classify:
            classified = seg['classified']
        else:
            classified = []

        return seg['text'],seg['inside'],seg['outside'],classified

   
if __name__ == '__main__':
    from gamera.core import * 
    from class_dynamic import Classifier_with_remove
    from ill_music import IllMusicImage
    import sys
    #LOG_FILENAME = '/tmp/logging_example.out'
    FORMAT = "%(asctime)-15s %(levelname)s [%(name)s.%(funcName)s]  %(message)s"
    logging.basicConfig(level=logging.DEBUG,format=FORMAT)
    init_gamera()
    c = Classifier_with_remove(training_filename="preomr_edited_cnn.xml")
    c.set_k(1)
    filename = sys.argv[-1]
    #c.classifier.load_settings("gasettings.txt")
    mi = IllMusicImage(load_image(filename),classifier=c)
    ret = mi.without()
    ret.save_PNG("%s_Removed.png"%filename)
    logging.debug("Done with %s"%filename)
    ret = mi.color_segment(classified_box=True)
    ret.save_PNG("%s_ColorSegment.png"%filename)
    logging.debug("Done with %s"%filename)




