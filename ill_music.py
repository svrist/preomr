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

from sheetmusic import MusicImage
from outline import outline
from gamera.core import RGBPixel


class IllMusicImage(MusicImage):
    def color_segment(self,text_color=RGBPixel(255,255,0),\
                      instaff_color=RGBPixel(0,255,0),\
                      other_color=RGBPixel(100,100,100),
                      classified_color=None,
                     classified_box=False):
        """ Segment image in three with colors
        Segment the image into three parts:
             - text
             - inside staff
             - Others/relevant for Classifier

        Keyword arguments:
            text_color --- What color to use for text ccs
            instaff_color --- The color to use for in-staff ccs
            other_color --- The color of the rest.
            classified_color --- If set we will try to classify stuff in the
            image and give them the given color
            classified_box --- If set we will try to classify and but instead of
            highlight I will box them.

        """
        ret = self.to_rgb().to_onebit().to_rgb()
        classify = False
        if not(classified_color is None and classified_box is None):
            classify = True
            if classified_color is None:
                classified_color = RGBPixel(255,0,0)

        text,instaff,other,classified = self.segment(classify=classify)
        # Painting inside staff things green
        for c in instaff:
            ret.highlight(c,instaff_color)

        # Painting relevant ccs' red.
        for c in other:
            ret.highlight(c,other_color)


        for c in classified:
            if classified_box:
                outline(ret,c,width=2.0,color=classified_color)
            else:
                ret.highlight(c,classified_color)

        # Painting text yellow
        for c in text:
            ret.highlight(c,text_color)

        return ret

    def highlight_ccs(self,ccs,color=RGBPixel(0,255,0)):
        bla = self.to_rgb()
        [ bla.highlight(c,color) for c in ccs ]
        return bla


    def highlight_possible_text(self, image=None):

        if image is None:
            ret = self._orig.to_rgb()
        else:
            ret = image
        spikes = self._text()._possible_text_areas()

        [ ret.draw_hollow_rect((0,s['start']),(ret.width-1,s['stop']),RGBPixel(255,0,0))\
         for s in spikes ]
        return ret


    def with_row_projections(self,color=RGBPixel(200,50,50),image=None,ret=None,fac=None):
        if ret is None:
            ret = self._orig.to_rgb()

        if image is None:
            image = self.without_insidestaves_info()
        p = image.projection_rows()
        # l = [ (v,i) for i,v in enumerate(p) ]
        #[ ret.draw_line( (0,i[1]), (i[0],i[1]),color) for i in l]
        self.draw_y_proj(p,image=ret,color=color,fac=None)
        return ret

    def highlight_text_by_hist(self,bc=5,f=lambda c: c.aspect_ratio()[0]):
        import matplotlib.pyplot as plt
        from random import randint
        ret = self._orig.to_rgb()
        ccs = self._text().possible_text_ccs()
        l = [ f(c) for c in ccs ]

        n,bins,patches = plt.hist(l,bc)
        colors = [ RGBPixel(255,c,c) for c in xrange(0,255,int(255/bc)) ]
        nv = [ (v,i) for i,v in enumerate(n) ]
        nv.sort(reverse=True)
        nv = [ (v,origi, colors[i] ) for i,(v,origi) in enumerate(nv) ]

        for v,i,color in nv :
            [ ret.highlight(c,color) for c in ccs \
             if f(c) >= bins[i]  and f(c) <= bins[i+1] ]

        i = 0
        [ ret.draw_hollow_rect(c,colors[0]) for c in ccs if f(c) >= bins[i] and
         f(c) <= bins[i+1] ]


    def highlight_words(self):
        ret = self._orig.to_rgb()
        img = self.without_insidestaves_info().image_copy()
        ccs = img.cc_analysis()
        words = self._text()._words(img,ccs)
        [ ret.draw_hollow_rect(c,RGBPixel(255,0,0)) for c in words ]
        return ret


    def draw_y_proj(self,rl,image=None,color=RGBPixel(255,0,0),norm=True,side="left",fac=None):
        """ Draw projections on the y-axis on top of an image 
        *rl*:
            the projection data. One value for each y-value in the image
        *image*:
            The image to draw upon. Defaults to use this image in rgb edition
        *color*:
            The color to draw with.
        *norm*:
            Should the projections be normalized so that the longest value is a
            page wide?. Defaults to true.
        *side*:
            Unused for now. From which side should the projections be drawn.
            Left/Right. default left.
        *fac*:
            Factor to normalize by.
        """

        if image is None:
            image = self.to_rgb()

        assert len(rl) == image.nrows

        if norm:
            if fac is None:
                fac = int(image.ncols/max(rl))
            rl = [ fac*r for r in rl ]

        l = [ (v,i) for i,v in enumerate(rl) ]
        [ image.draw_line( (0,i[1]), (i[0],i[1]),color) for i in l]
        return image

    def without(self,classified=True,text=True):
        """ Create an image where text and classified are whited out"""
        ret = self.color_segment(other_color=RGBPixel(0,0,0),
                               text_color=RGBPixel(255,255,255),
                               instaff_color=RGBPixel(0,0,0),
                               classified_color=RGBPixel(255,255,255)
                              )
        return ret
