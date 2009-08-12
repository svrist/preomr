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
from outline import outline
import sys
import re
import time

k = 1
e_fp = 0.78


def paint_dynamics(classifier,imgname,d_t):
    start=time.time()
    image = load_image(imgname)
    image = image.to_onebit()
    ms = musicstaves_rl_fujinaga.MusicStaves_rl_fujinaga(image)
    ms.remove_staves(crossing_symbols = 'bars')
    rgbimg = image.to_rgb()
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
    from gamera import knn
    classifier=knn.kNNInteractive([],["aspect_ratio", "moments",
                                       "volume64regions"], 0)
    classifier.num_k = 2
    classifier.from_xml_filename("only-dynamics.xml")
    classifier.confidence_types = [CONFIDENCE_AVGDISTANCE]

    stats = classifier.knndistance_statistics()
    from cdf import EmpiricalCDF
    cdf = EmpiricalCDF([s[0] for s in stats])
    d_t = cdf.invcdf(e_fp)
    print "Loaded Gamera and classifier in %f seconds"%(time.time()-start)

    start=time.time()
    for imgname in sys.argv[1:]:
        m = re.match(r"^(.*)\.[^\.]+$",imgname)
        noend = m.group(1)
        rgbimg = paint_dynamics(classifier,imgname,d_t)
        rgbimg.save_PNG("class_%s.png"%noend) 
        print "Saved class_%s.png"%noend

    print "Parsed %d images in %f seconds"%(len(sys.argv[1:]),time.time()-start)
