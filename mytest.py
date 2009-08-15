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

from numpy import arange
from gamera.core import *
from class_dynamic import Classifier_with_remove
import sys

def test_e_fp(filename):
    init_gamera()
    for dynamic in ["mergedyn.xml","only-dynamics.xml", "newtrain-dynamic"]:
        c = Classifier_with_remove("mergedyn.xml",0.1)
        ci = c.classify_image(filename)
        result = {}
        for e_fp in arange(0.1,0.95,0.01):
            c.e_fp=e_fp
            count = len(ci.classified_glyphs(c.d_t()))
            if not result.has_key(count):
                result[count] = []
                result[count].append(e_fp)
        print "%s: %s"%(dynamic,[round(r,3) for r in result[10]])

if __name__ == '__main__':
    test_e_fp(sys.argv[-1])
