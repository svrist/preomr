from gamera.core import *
from gamera.toolkits.musicstaves import musicstaves_rl_simple
from gamera.toolkits.musicstaves import musicstaves_rl_fujinaga
from gamera.toolkits.musicstaves import musicstaves_skeleton
from gamera.toolkits.musicstaves import musicstaves_rl_carter
import sys
import re

init_gamera()

imgname = sys.argv[-1]
m = re.match(r"^(.*)\.[^\.]+$",imgname)
noend = m.group(1)

image = load_image(imgname)
image = image.to_onebit()
ms = musicstaves_rl_fujinaga.MusicStaves_rl_fujinaga(image)
ms.remove_staves(crossing_symbols = 'bars'):q




#no_staves_img = ms.image.image_copy()
# alternative without copying:  no_staves_img = ms.image
