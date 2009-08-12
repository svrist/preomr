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
import sys
import re

def remstaves(image):
    ms = musicstaves_rl_fujinaga.MusicStaves_rl_fujinaga(image)
    ms.remove_staves(crossing_symbols = 'bars')
    return ms


if __name__ == '__main__':
    init_gamera()
    for imgname in sys.argv[1:]:
        m = re.match(r"^(.*)\.[^\.]+$",imgname)
        noend = m.group(1)
        image = load_image(imgname)
        image = image.to_onebit()
        ms = remstaves(image)
        ms.image.save_PNG("%s_fujinaga.png"%noend)
        print "Saved %s_fujinaga.png"%noend

