import sys
import os
import random
from subprocess import Popen,PIPE,STDOUT
from pdftools.pdffile import PDFDocument
sys.path.append("..")

from sheetmusic import *

file = sys.argv[-1]
doc = PDFDocument(file)
print "Document uses PDF format version", doc.document_version()
pages = doc.count_pages()
print "Document contains %i pages." % pages
chosen_pages = random.sample([i for i in xrange(1,pages+1)],min(pages,10))
chosen_pages.sort()
print "Chose pages %s"%chosen_pages

dirname = file[:-4]

if not os.path.exists(dirname):
    os.mkdir(dirname)

gspath="\"c:/Program Files/gs/gs8.70/bin/gswin32c.exe\"".replace("/","\\")
from gamera.core import * 
init_gamera()
for page in chosen_pages:
    print "Page %d"%page
    sys.stdout.flush()
    outfile = "%s/%s-page%d.tif"%(dirname,file[:-4],page)
    outfile_staves = "%s/%s-page%d-staves.tif"%(dirname,file[:-4],page)
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
                    #'-c quit',
                    file
                   ])
    po = Popen(cmd,shell=True,stdout=PIPE,stderr=STDOUT).stdout
    for l in po.readlines():
        print l
    po.close()
    mi = MusicImage(outfile)
    mi.without_staves().save_PNG(outfile_staves)

