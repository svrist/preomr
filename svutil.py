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


