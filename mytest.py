# -*- coding: iso-8859-15 -*
# Copyright (C) 2009 S�ren Bjerregaard Vrist
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

from numpy import arange
from gamera.core import *
from class_dynamic import Classifier_with_remove
from outline import outline
import sys

class Result_item():
    def __init__(self,key,e_fp,d_t):
        self.key = key
        self.e_fp  = e_fp
        self.d_t = d_t

    def __str__(self):
        return "RI(%.2f,%.4f)"%(self.e_fp,self.d_t)

    def __repr__(self):
        return str(self)

def find_nearest(result,count):
    diff = 0
    myres = result.keys()
    myres.sort()
    myres.reverse()
    maxkey = myres[0]
    while True:
        if result.has_key(count-diff) and count-diff >0:
            return (count-diff),result[count-diff],-diff
        elif result.has_key(count+diff) and count+diff < maxkey:
            return (count+diff),result[count+diff],diff
        else:
            diff += 1
            if count-diff< 0 and count+diff > maxkey:
                return maxkey,result[maxkey],None

def test_e_fp(filename,expected_count=10):
    init_gamera()
    c = Classifier_with_remove()
    c.set_k(1)
    c.change_features(["volume64regions"])
    ci = c.classify_image(filename)
    #files = ["mergedyn2.xml", "mergedyn.xml","only-dynamics.xml",
    #        "newtrain-dynamic.xml", "preomr.xml"]
    files =  ["preomr.xml","preomr_edited.xml","preomr_edited_cnn.xml"]
    import os.path
    # try to match with different trainingsets.
    for dynamic in ([ d for d in files if os.path.isfile(d) ]):
        ci.load_new_training_data(dynamic)
        print "%s - count_of_training=%d, k=%d"%(dynamic,len(c.stats),c.k)
        result = {} # Push into buckets based on the count of found glyphs.
        csv = {}
        sys.stdout.flush()

        # Try with different epsilon for false_positives: e_fp
        for e_fp in arange(0.01,1.01,0.01):
            c.e_fp=e_fp
            count = len(ci.classified_glyphs())

            # Init bucket.
            if not result.has_key(count):
                result[count] = []

            result[count].append((e_fp,c.d_t()))
            csv[e_fp] = count

        # Find the best match to the wanted result.
        k,res,diff  = find_nearest(result,expected_count)
        
        confid = [ (len(v),key,v[0][0],v[0][1]) for key,v in result.iteritems() ]
        confid2 = [ (key,len(v)) for key,v in result.iteritems() ]

        confid.sort(reverse=True)
        confid2.sort()
        print "efp,count"
        for e_fp,c in sorted(csv.iteritems()):
            print "%s,%s"%(e_fp,c)
        print
        print "count,spansize"
        for count,spansize in confid2:
            print "%s,%s"%(count,spansize)


        return
        ret = []
        for i in range(0,min(10,len(confid))+1):
            ret.append(confid[i])

        if not result.has_key(expected_count):
            print "Never found the desired amount with %s"%dynamic

        print "Found in %d(%d): %s"%(k,diff,[r for r in res])
        rgbimg = ci.image.to_rgb()
        cg = ci.classified_glyphs(res[0].d_t)
        [outline(rgbimg,g,3.0,RGBPixel(255,0,0)) for g in cg]
        rgbimg.save_PNG("class_%s_%s.png"%(filename,dynamic))
        print



if __name__ == '__main__':
    test_e_fp(sys.argv[1],int(sys.argv[2]))
