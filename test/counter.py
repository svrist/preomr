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

"""
$ ls  -1 --color=never testrun-20090921/*/*-colorseg.png | sed
"s/-colorseg.png/.tif/" > countlist

$ for f in `cat countlist` 
do
python counter.py $f
done

"""
from __future__ import with_statement
from gamera.core import *
import logging
import sys
import re
import yaml
sys.path.append("..")
from sheetmusic import MusicImage


if __name__ == '__main__':
    FORMAT = "%(asctime)-15s %(levelname)s [%(name)s.%(funcName)s]  %(message)s"
    logging.basicConfig(level=logging.DEBUG,format=FORMAT,filename="counter.log")
    init_gamera()

    for imgname in sys.argv[1:]:
        m = re.match(r"^(.*)\.[^\.]+$",imgname)
        noend = m.group(1)
        mi = MusicImage(imgname,training_filename="../preomr_edited_cnn.xml")
        c = mi.ccs_overall()
        cl = dict([ (k,len(v)) for k,v in c.iteritems() ])
        outf = "%s-colorseg.yaml"%noend
        with open(outf,"w") as f:
            data = {'text':{'found':cl['text'],'count':cl['text']},
                    'dynamics':{'found':cl['classified'], 'count':cl['classified']
                               }
                   }
            print "%s"%data
            yaml.dump(data,f)
        logging.debug("Wrote %s",outf)



