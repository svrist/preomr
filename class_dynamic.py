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
from remstaves import remstaves
from outline import outline
from cdf import EmpiricalCDF
import sys
import re
import time

k = 1
e_fp = 0.78

class Classified_image:

    def __init__(self,classifier,image,image_without_stafflines):
        self.classifier = classifier
        self.image = image
        self.ms = image_without_stafflines
        self.classify_image()
        self._rgbimg = None

    def classify_image(self):
        self.ccs = self.ms.image.cc_analysis()
        self.classifier.classify_list_automatic(self.ccs)

    def classified_glyphs(self,d_t):
        return [g for g in self.ccs if g.get_confidence(CONFIDENCE_AVGDISTANCE) <= d_t]

    def rgbimg(self):
        if self._rgbimg is None:
            self._rgbimg = self.image.to_rgb()
        return self._rgbimg

class Classifier_with_remove:

    def __init__(self,training_filename,e_fp=0.1,k=1):
        self.filename = training_filename
        self.e_fp = e_fp
        self.k = k
        self.init_classifier()

    def init_classifier(self,features= ["aspect_ratio", "zernike_moments",\
                                   "volume64regions","volume"]):
        self.classifier=knn.kNNInteractive([],features, 0)
        self.classifier.num_k = self.k
        self.classifier.from_xml_filename(self.filename)
        self.classifier.confidence_types = [CONFIDENCE_AVGDISTANCE]
        self.stats = self.classifier.knndistance_statistics()

    def change_features(self,features):
        self.classifier.change_feature_set(features)

    def d_t(self):
        cdf = EmpiricalCDF([s[0] for s in self.stats])
        return cdf.invcdf(self.e_fp)

    def classify_image(self,imgname):
        image = load_image(imgname)
        image = image.to_onebit()
        ms = remstaves(image)
        return Classified_image(self.classifier,image,ms)



def paint_dynamics(classifier,imgname,d_t):
    start=time.time()
    ccs = ms.image.cc_analysis()
    classifier.classify_list_automatic(ccs)
    count = 0
    for g in ccs:
        if g.get_confidence(CONFIDENCE_AVGDISTANCE) <= d_t:
            outline(rgbimg,g,3,RGBPixel(255,0,0))
            count += 1
    print "Classified %d glyps in  %f seconds"%(count,time.time()-start)
    return rgbimg


if __name__ == '__main__':
    start=time.time()
    init_gamera()
    c = Classifier_with_remove("newtrain-dynamic.xml",0.35)
    print "Loaded Gamera and classifier in %f seconds"%(time.time()-start)
    print "count_of_training=%d, k=%d, e_fp=%f, d_t=%f"%(len(c.stats),c.k,c.e_fp,c.d_t())

    start=time.time()
    for imgname in sys.argv[1:]:
        m = re.match(r"^(.*)\.[^\.]+$",imgname)
        noend = m.group(1)
        ci = c.classify_image(imgname)
        rgbimg = ci.rgbimg()
        cg = ci.classified_glyphs(c.d_t())
        [outline(rgbimg,g,3.0,RGBPixel(255,0,0)) for g in cg]
        rgbimg.save_PNG("class_%s.png"%noend)
        print "Saved class_%s.png: %d glypgs found"%(noend,len(cg))
        sys.stdout.flush()

    print "Parsed %d images in %f seconds"%(len(sys.argv[1:]),time.time()-start)
