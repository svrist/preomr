import sys
import logging
import time
import traceback
FORMAT = "%(asctime)-15s %(levelname)s [%(name)s.%(funcName)s]  %(message)s"
logging.basicConfig(level=logging.DEBUG,format=FORMAT,filename="convert.log")

sys.path.append("..")

from  convlib import Pdfsampler
from sheetmusic import NoStavesException
from gamera.core import * 
init_gamera()


for file in sys.argv[1:]:
    print "Converting %s"%file
    sys.stdout.flush()
    start = time.time()
    try:
        pdf = Pdfsampler(file)
        chosen_pages = pdf.all()
        for page in chosen_pages:
            page.save()
            #page.save_nostaves()
            try:
                colfilename = page.save_without(type="tif")
            except NoStavesException,e:
                logging.info("No staves in %s page %s",file,page._pagenumber)
            #        page.generate_gamera_script(openfile=colfilename)
    except Exception,e:
        print "Skipping %s"%file
        logging.warn("Failed with %s, Skipping: %s",file,e)
        logging.info("Exception: %s",traceback.format_exc(10))

    print "Duration %f"%((time.time()-start))
    sys.stdout.flush()
