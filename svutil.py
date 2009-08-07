from gamera.core import RGBPixel
from outline import *

def get_index_of_label(ccs,label):
    for i in range(len(ccs)):
        c = ccs[i]
        if c.label == label:
            return i

def match_bb(rgbimg,ccs,match,scale_factor, precision):
    for c in ccs:
        c_scaled_cols = int(c.ncols/float(scale_factor)*precision)
        c_scaled_rows = int(c.nrows/float(scale_factor)*precision)
        #print "cols:%s, rows:%s"%(c_scaled_cols,c_scaled_rows)
        [ outline(rgbimg,c,2,m['color']) for m in match if m['cols'] == c_scaled_cols and m['rows'] == c_scaled_rows ]


