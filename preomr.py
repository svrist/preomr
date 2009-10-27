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
import logging
import sys
import re
from class_dynamic import Classifier_with_remove
from ill_music import IllMusicImage


if __name__ == '__main__':
    FORMAT = "%(asctime)-15s %(levelname)s [%(name)s.%(funcName)s]  %(message)s"
    logging.basicConfig(level=logging.INFO,format=FORMAT)
    init_gamera()
    files = []
    if sys.argv[1][-4:] == ".xml":
        c = Classifier_with_remove(training_filename=sys.argv[1])
        files = sys.argv[2:]
    else:
        c = Classifier_with_remove(training_filename="preomr_edited_cnn.xml")
        files = sys.argv[1:]
    c.set_k(1)
    sys.stdout.flush()
    for imgname in files:
        m = re.match(r"^(.*)\.[^\.]+$",imgname)
        noend = m.group(1)
        mi = IllMusicImage(imgname,classifier=c)
        without = mi.without()
        without.save_PNG("%s_clean.png"%noend)
        print "%s_clean.png"%noend
        sys.stdout.flush()
