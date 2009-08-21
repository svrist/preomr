from gamera.core import * 
from remove import remstaves,reminside,remoutside

class MusicImage(object):
    self.image  =None

    def __init__(self,image):
        self.image= image
        self.ms = None

    def without_staves(self):
        if self.ms is None:
            self.ms = remstaves(self.image)
        return self.ms.image

    def without_insidestaves_info(self):
        if self.noinside is None:
            self.noinside = reminside(self.ms,self.ms.image.image_copy())
        return self.noinside

    def __getattr__(self,name):
        return self.image.__getattr__(name)

