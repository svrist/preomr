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
from gamera.toolkits.musicstaves import musicstaves_rl_fujinaga
from gamera import knn
from remove import remstaves
from outline import outline
from cdf import EmpiricalCDF
from within import inout_staff_condition
from sheetmusic import MusicImage
import sys
import re
import time

k = 5
e_fp = 0.78

class Classified_image:
    """
     Image with an attached classifier.
     When the classifier gets updated somewhere, this image uses the new
     classifier.
    """

    def __init__(self,classifier,image,ccs):
        self.myclassifier = classifier
        self.image = image
        self.ccs = ccs
        self._invalid = True

    def classify_image(self):
        self.myclassifier.classifier.classify_list_automatic(self.ccs)
        self.valid()

    def invalid(self):
        self._invalid = True

    def valid(self):
        self._invalid = False

    def classified_glyphs(self,d_t=None):
        if self._invalid:
            self.classify_image()
            print "k=%d"%self.myclassifier.classifier.num_k

        if d_t is None:
            d_t = self.myclassifier.d_t()

        return [g for g in self.ccs if g.get_confidence(CONFIDENCE_AVGDISTANCE) <= d_t]

    def load_new_training_data(self,filename):
        self.myclassifier.load_new_training_data(filename)

class Classifier_with_remove(object):

    def baseinit(self):
        self.images = []
        self.classifier = None

    def __init__(self,training_filename=None,e_fp=0.1,k=1):
        self.filename = training_filename
        self.baseinit()
        self.e_fp = e_fp
        self.k = k
        self.init_classifier(self.filename)

    def set_k(self,value):
        self.k =value
        if not self.classifier is None:
            self.classifier.num_k = value
            self.invalidate_images()

    def init_classifier(self,filename=None,features= ["aspect_ratio", "zernike_moments",\
                                   "volume64regions","volume"]):
        self.classifier=knn.kNNInteractive([],features, 0)
        self.classifier.num_k = self.k
        if not filename is None:
            self.load_new_training_data(filename)
        else:
            self.invalidate_images()

    def invalidate_images(self):
        [ i.invalid() for i in self.images]

    def change_features(self,features):
        self.classifier.change_feature_set(features)
        self.invalidate_images()

    def load_new_training_data(self,filename):
        self.classifier.from_xml_filename(filename)
        self.classifier.confidence_types = [CONFIDENCE_AVGDISTANCE]
        self.stats = self.classifier.knndistance_statistics()
        self.invalidate_images()
        print "loaded new file with training data: %s"%filename

    def d_t(self):
        cdf = EmpiricalCDF([s[0] for s in self.stats])
        return cdf.invcdf(self.e_fp)

    def classify_image(self,imgname):
        mi = MusicImage(imgname)
        #def ccs(remove_text=True,remove_inside_staffs=True):
        relevant_cc = mi.ccs(remove_text=True,remove_inside_staffs=True)
        ret = Classified_image(self,mi,relevant_cc)
        self.images.append(ret)
        return ret


if __name__ == '__main__':
    start=time.time()
    init_gamera()
    c = Classifier_with_remove(sys.argv[1],float(sys.argv[2]))
    d_t = c.d_t()
    print "Loaded Gamera and classifier in %f seconds"%(time.time()-start)
    print "count_of_training=%d, k=%d, e_fp=%f, d_t=%f"%(len(c.stats),c.k,c.e_fp,d_t)
    sys.stdout.flush()

    start=time.time()
    for imgname in sys.argv[3:]:
        m = re.match(r"^(.*)\.[^\.]+$",imgname)
        noend = m.group(1)
        ci = c.classify_image(imgname)
        rgbimg = ci.image.to_rgb()
        cg = ci.classified_glyphs(d_t)
        [outline(rgbimg,g,3.0,RGBPixel(255,0,0)) for g in cg]
        rgbimg.save_PNG("class_%s.png"%noend)
        print "Saved class_%s.png: %d glypgs found"%(noend,len(cg))
        sys.stdout.flush()
    print "Parsed %d images in %f seconds"%(len(sys.argv[3:]),time.time()-start)
