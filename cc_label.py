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

from remove import remstaves

if __name__ == '__main__':
    from gamera.core import *
    import sys
    init_gamera()

    for i,imgname in enumerate(sys.argv[1:]):
        image = load_image(imgname)
        image = image.to_onebit()
        try:
            ms = remstaves(image)
        except:
            ms = remstaves_skeleton(image)

        ccs = ms.image.cc_analysis()

        print "%s: %s"%(imgname,[(i,c.label) for i,c in enumerate(ccs) ])

        sys.stdout.flush()

