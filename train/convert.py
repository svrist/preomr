import sys
import os
import random
import time
from subprocess import Popen,PIPE,STDOUT
from pdftools.pdffile import PDFDocument
sys.path.append("..")

from sheetmusic import *
from gamera.core import * 
init_gamera()
gspath="\"c:/Program Files/gs/gs8.70/bin/gswin32c.exe\"".replace("/","\\")
FORMAT = "%(asctime)-15s %(levelname)s [%(name)s.%(funcName)s]  %(message)s"
logging.basicConfig(level=logging.DEBUG,format=FORMAT,filename="convert.log")


for file in sys.argv[1:]:
    print "Converting %s"%file
    start = time.time()
    try:
        doc = PDFDocument(file)
        pages = doc.count_pages()
        chosen_pages = random.sample([i for i in xrange(1,pages+1)],min(pages,10))
        chosen_pages.sort()
        logging.info("%s - %d pages. %s chosen",file,pages,chosen_pages)
        dirname = file[:-4]
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        for page in chosen_pages:
            sys.stdout.flush()
            outfile = "%s/%s-page%d.tif"%(dirname,file[:-4],page)
            outfile_staves = "%s/%s-page%d-staves.tif"%(dirname,file[:-4],page)
            outfile_gamscript = "%s-page%d-class.py"%(file[:-4],page)
            cmd = ' '.join([gspath,
                            '-dNOPAUSE',
                            '-q',
                            '-r300',
                            '-sDEVICE=tiffg4',
                            '-dBATCH',
                            '-sOutputFile=%s'%outfile,
                            '-sPAPERSIZE=a4',
                            '-dFirstPage=%d'%page,
                            '-dLastPage=%d'%page,
                            file
                        ])
            po = Popen(cmd,shell=True,stdout=PIPE,stderr=STDOUT).stdout
            for l in po.readlines():
               print l
            po.close()
            mi = MusicImage(outfile)
            mi.without_staves().save_PNG(outfile_staves)
            gamscript = open(outfile_gamscript,'w')
            gamscript_head = open("gamscripthead.py")
            gamscript.write("# Open %s in gamera with a classifier\n"%outfile_staves)
            gamscript.write(gamscript_head.read())
            gamscript_head.close()
            gamscript.write("\n####\n")
            gamscript.write("image = load_image(\"%s\")\n"%outfile_staves)
            gamscript.write("ccs = image.cc_analysis()\n")
            gamscript.write("classifier.display(ccs,image)\n")
            gamscript.close()
    except Exception, e:
        logging.warn("Failed to parse %s: %s",file,e)
    finally:
        end=time.time()
        print "\t%f seconds"%(end-start)
        if not chosen_pages is None:
            print "\t%d pages handled"%len(chosen_pages)

