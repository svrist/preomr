
from gamera.core import *
from gamera.toolkits.musicstaves import musicstaves_rl_fujinaga

def initrex():
    ret = []
    for i in range(5):
        img = load_image("rexp%d.tif"%i)
        rgbimg = img.to_rgb()
        img = img.to_onebit()
        ms = musicstaves_rl_fujinaga.MusicStaves_rl_fujinaga(img)
        ms.remove_staves(crossing_symbols = 'bars')
        ms.image.save_PNG("nostaves_rexp%d.png"%i)
        #elem = {}
        #elem["orig"] = img
        #elem["ms"] = ms
        #elem["rgb"] = rgbimg
        #ret.append(elem)
        print "Loaded and prepared rexp%d.tif. Saved nostaves_rexp%d.png"%(i,i)

    return ret

if __name__ == '__main__':
    init_gamera()
    initrex()
