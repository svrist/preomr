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
def outline(rgb_img,cc,width=2.0,color=RGBPixel(255,0,0)):
    rgb_img.draw_hollow_rect((cc.offset_x,cc.offset_y),(cc.offset_x+cc.ncols,cc.offset_y+cc.nrows),color,width)
       
def outline_matched(rgb_img,needle,haystack):
    epsilon = 5
    bottom_ncols = needle.ncols-5
    top_ncols = needle.ncols+5
    for c in haystack:
        if c.ncols == needle.ncols and c.nrows == needle.nrows:
            outline(rgb_img,c)
