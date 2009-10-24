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

from within import inout_vertical_ys,between

def ccs_manip(baseccs,subccs, condturn = lambda x: not x):
    """ Manipulate "subccs" from baseccs and return a new list
    Compares on offset_* and cols/rows.
    Defaults to subtract subccs.
    """
    return [ c for c in baseccs \
            if condturn((c.offset_x,c.offset_y,c.ncols,c.nrows) in \
                [(ic.offset_x,ic.offset_y,ic.ncols,ic.nrows) for ic in \
                subccs] ) ]

def ccs_remove(haystack,needles):
    return ccs_manip(haystack,needles)

def ccs_intersect(haystack,needles):
    return ccs_manip(haystack,needles, lambda x: x)

def ccs_in_spike(spikes,ccs):
        ret = []
        for s in spikes[:]:
            cond = inout_vertical_ys([(s['start'],s['stop'])])
            cs = [ c for c in ccs if cond(c) ]
            ret.extend(cs)
        return ret

def ccs_in_rspike(spikes,ccs):
    return [ c for s in spikes for c in ccs if s.contains_y(c.center_y)]

# Verbose copy from from gamera src.
def expand_ccs(image,ccs,Ex,Ey):
    # two helper functions for merging rectangles
    def find_intersecting_rects(glyphs, index):
        g = glyphs[index]
        inter = []
        for i in range(len(glyphs)):
            if i == index:
                continue
            if g.intersects(glyphs[i]):
                inter.append(i)
        return inter
    def list_union_rects(big_rects):
        current = 0
        rects = big_rects
        while(1):
            inter = find_intersecting_rects(rects, current)
            if len(inter):
                g = rects[current]
                new_rects = [g]
                for i in range(len(rects)):
                    if i == current:
                        continue
                    if i in inter:
                        g.union(rects[i])
                    else:
                        new_rects.append(rects[i])
                rects = new_rects
                current = 0
            else:
                current += 1
            if(current >= len(rects)):
                break
        return rects

    # the actual plugin
    from gamera.core import Dim, Rect, Point, Cc
    from gamera.plugins.image_utilities import union_images
    page = image

    # extend CC bounding boxes
    big_rects = []
    for c in ccs:
        ul_y = max(0, c.ul_y - Ey)
        ul_x = max(0, c.ul_x - Ex)
        lr_y = min(page.lr_y, c.lr_y + Ey)
        lr_x = min(page.lr_x, c.lr_x + Ex)
        nrows = lr_y - ul_y + 1
        ncols = lr_x - ul_x + 1
        big_rects.append(Rect(Point(ul_x, ul_y), Dim(ncols, nrows)))
    extended_segs = list_union_rects(big_rects)

    # build new merged CCs
    tmplist = ccs[:]
    dellist = []
    seg_ccs = []
    seg_cc = []
    if(len(extended_segs) > 0):
        label = 1
        for seg in extended_segs:
            label += 1
            for cc in tmplist:
                if(seg.intersects(cc)):
                    # mark original image with segment label
                    #self.highlight(cc, label)
                    seg_cc.append(cc)
                    dellist.append(cc)
            if len(seg_cc) == 0:
                continue
            seg_rect = seg_cc[0].union_rects(seg_cc)
            new_seg = Cc(image, label, seg_rect.ul, seg_rect.lr)
            seg_cc = []
            for item in dellist:
                tmplist.remove(item)
            dellist = []
            seg_ccs.append(new_seg)
    return seg_ccs




