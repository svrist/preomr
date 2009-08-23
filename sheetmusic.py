from gamera.core import *
from remove import remstaves,reminside

from proj import Projection


class MusicImage(object):

    def __init__(self,image):
        """ Setup a wrapped image with music methods around """
        if isinstance(image,basestring):
            image = load_image(image)

        self._orig = image
        self._image= image
        self._image = self._image.to_onebit()
        self._ms = None
        self._noinside = None

    def without_staves(self):
        if self._ms is None:
            self._ms = remstaves(self._image)
        return self._ms.image

    def without_insidestaves_info(self):
        self.without_staves()

        if self._noinside is None:
            self._noinside = reminside(self._ms.get_staffpos(),
                                        self._ms.image.image_copy())
        return self._noinside

    def with_row_projections(self,color=RGBPixel(200,50,50)):
        ret = self._orig.to_rgb()
        p = self.without_insidestaves_info().projection_rows()
        l = [ (v,i) for i,v in enumerate(p) ]
        [ ret.draw_line( (0,i[1]), (i[0],i[1]),color) for i in l]
        return ret

    def highlight_possible_text(self,min_cutoff_factor=0.02,
                                height_cutoff_factor=0.8):
        ret = self._orig.to_rgb()
        p = Projection(self.without_insidestaves_info().projection_rows())
        p.threshold(min_cutoff_factor*self._orig.width)
        spikes = p.spikes(height_cutoff_factor*self._ms.staffspace_height)
        [ ret.draw_hollow_rect((0,s['start']),(ret.width-1,s['stop']),RGBPixel(255,0,0))\
         for s in spikes ]

        return ret


    def to_rgb(self):
        return self._orig.to_rgb()


if __name__ == '__main__':
    from gamera.core import * 
    init_gamera()
    mi = MusicImage(load_image("brahmsp1.tif"))
    mi2 = mi.without_insidestaves_info()
    mi2.image.save_PNG("newpng.png")
    mi3 = mi.image_copy_with_row_projections()
    mi3.image.save_PNG("proj_new.png")
