from gamera.core import *
from remove import remstaves,reminside
from types import MethodType

class MusicImage(object):

    def __init__(self,image):
        """ Setup a wrapped image with music methods around """
        self.orig = image
        self.image= image
        self.image = self.image.to_onebit()
        self.ms = None
        self.noinside = None

    def without_staves(self):
        if self.ms is None:
            self.ms = remstaves(self.image)
        return MusicImage(self.ms.image)

    def without_insidestaves_info(self):
        self.without_staves()

        if self.noinside is None:
            self.noinside = MusicImage(reminside(self.ms.get_staffpos(),self.ms.image.image_copy()))
        return self.noinside

    def with_row_projections(self,color=RGBPixel(50,50,50)):
        ret = self.image.to_rgb()
        p = self.without_insidestaves_info().image.projection_rows()
        l = [ (v,i) for i,v in enumerate(p) ]
        [ ret.draw_line( (0,i[1]), (i[0],i[1]),color) for i in l ]
        return MusicImage(ret)


if __name__ == '__main__':
    from gamera.core import * 
    init_gamera()
    mi = MusicImage(load_image("brahmsp1.tif"))
    mi2 = mi.without_insidestaves_info()
    mi2.image.save_PNG("newpng.png")
    mi3 = mi.image_copy_with_row_projections()
    mi3.image.save_PNG("proj_new.png")
