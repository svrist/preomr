from gamera.core import *
from gamera.toolkits.musicstaves import musicstaves_rl_simple
from gamera.toolkits.musicstaves import musicstaves_rl_fujinaga
from gamera.toolkits.musicstaves import musicstaves_skeleton
from gamera.toolkits.musicstaves import musicstaves_rl_carter
import sys
import re

init_gamera()
for imgname in sys.argv[1:]:
    m = re.match(r"^(.*)\.[^\.]+$",imgname)
    noend = m.group(1)
    image = load_image(imgname)
    image = image.to_onebit()
    ms = musicstaves_rl_fujinaga.MusicStaves_rl_fujinaga(image)
    ms.remove_staves(crossing_symbols = 'bars')
    ms.image.save_PNG("%s_fujinaga.png"%noend)
    print "Saved %s_fujinaga.png"%noend

