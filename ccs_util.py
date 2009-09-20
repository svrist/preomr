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
        




