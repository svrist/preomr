import sys
import logging
import time
FORMAT = "%(asctime)-15s %(levelname)s [%(name)s.%(funcName)s]  %(message)s"
logging.basicConfig(level=logging.DEBUG,format=FORMAT,filename="convert.log")

sys.path.append("..")

from  convlib import Pdfsampler
from gamera.core import * 
init_gamera()


for file in sys.argv[1:]:
    print "Converting %s"%file
    start = time.time()
    #try:
    pdf = Pdfsampler(file)
    chosen_pages = pdf.randompages(2)
    for page in chosen_pages:
        page.save()
        page.save_nostaves()
        page.generate_gamera_script()
        page.save_color_segmented()
            #except Exception, e:
                #logging.warn("Exception during file %s: %s",file,e)
    print "Duration %f"%((time.time()-start))
    sys.stdout.flush()
