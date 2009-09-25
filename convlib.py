# -*- coding: iso-8859-15 -*
# Copyright (C) 2009 Søren Bjerregaard Vrist
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
from __future__ import with_statement

import logging
import os
import sys
import os
import random
import time
import yaml
from subprocess import Popen,PIPE,STDOUT
from pdftools.pdffile import PDFDocument
from ill_music import IllMusicImage

from class_dynamic import Classifier_with_remove

gspath="\"c:/Program Files/gs/gs8.70/bin/gswin32c.exe\"".replace("/","\\")

class Page:

    def __init__(self,origfile,pagenumber,classifier=None):
        self._pagenumber = pagenumber
        self._origfile = origfile
        self._noend = origfile[:-4] # shortcut
        self._classifier = classifier

        # internal logger
        self._l = logging.getLogger(self.__class__.__name__)

        # Internal params init.
        self._file = None
        self._mi = None
        self._nostavesfile = None

    def save(self,filename=None):
        start = time.time()
        if filename is None:
            filename = self._genfilename()

        cmd = ' '.join([gspath,
                            '-dNOPAUSE',
                            '-q',
                            '-r300',
                            '-sDEVICE=tiffg4',
                            '-dBATCH',
                            '-sOutputFile=%s'%filename,
                            '-sPAPERSIZE=a4',
                            '-dFirstPage=%d'%self._pagenumber,
                            '-dLastPage=%d'%self._pagenumber,
                            self._origfile
                        ])
        po = Popen(cmd,shell=True,stdout=PIPE,stderr=STDOUT).stdout
        for l in po.readlines():
            self._l.debug("GS Output:%s",l)
        po.close()
        self._file = filename
        self._l.debug("Saving file %s (duration %f)",
                      filename,(time.time()-start))
        return filename

    def _init_mi(self):
        """ Setup a MusicImage with our classifier """
        self._mi = IllMusicImage(self._file,classifier=self._classifier)

    def save_nostaves(self,filename=None):
        start = time.time()
        if self._file is None:
            self._l.debug("No converted tif page. Forcing one now.")
            self.save()

        if filename is None:
            filename = self._genfilename(postfix="-nostaves",extension=".png")

        if self._mi is None:
            self._init_mi()

        self._mi.without_staves().save_PNG(filename)
        self._nostavesfile = filename
        self._l.debug("Saved file %s (duration %f)",filename,(time.time()-start))
        return filename

    def generate_gamera_script(self,dir=".",filename=None,openfile=None):
        start = time.time()
        if filename is None:
            filename = self._genfilename(dir=dir,extension=".py")
            #self._l.info("Filename not given. Using %s",filename)

        if openfile is None and not self._nostavesfile is None:
            openfile = self._nostavesfile

        if openfile is None:
            raise Exception,"No file to open"

        with open(filename,'w') as gamscript:
            gamscript.write("# Open %s in gamera with a classifier\n"%self._nostavesfile)
            with open("gamscripthead.py") as gamscript_head:
                gamscript.write(gamscript_head.read())

            gamscript.write("\n####\n")
            gamscript.write("image = load_image(\"%s\")\n"%self._nostavesfile)
            gamscript.write("ccs = image.cc_analysis()\n")
            gamscript.write("classifier.display(ccs,image)\n")
        self._l.debug("Saved file %s (duration %f)",filename,(time.time()-start))
        return filename

    def save_color_segmented(self,filename=None):
        start = time.time()
        if self._mi is None:
            self._init_mi()

        if filename is None:
            filename = self._genfilename(postfix="-colorseg",extension=".png")

        color = self._mi.color_segment(classified_box=True)
        color.save_PNG(filename)
        self._l.debug("Saved file %s (duration %f)",
                      filename,(time.time()-start))
        return filename

    def gen_count_yaml(self,filename=None):
        if filename is None:
            filename = self._genfilename(postfix="-colorseg",extension=".yaml")
        if self._mi is None:
            self._init_mi()
        c = self._mi.ccs_overall()
        cl = dict([ (k,len(v)) for k,v in c.iteritems() ])
        with open(filename,"w") as f:
            data = {'text':{'found':cl['text'],'count':cl['text']},
                    'dynamics':{'found':cl['classified'], 'count':cl['classified']
                               }
                   }
            yaml.dump(data,f)
        logging.debug("Wrote %s",filename)



    def _genfilename(self,dir=None,postfix="",extension=".tif"):
        if dir is None:
            dir = self._noend
        filename = "%s/%s-page%02d%s%s"%\
                (dir,self._noend,self._pagenumber,postfix,extension)
        if not os.path.exists(dir):
            self._l.debug("%s dir dint exits. Creating it.",dir)
            os.mkdir(dir)

        return filename

class Pdfsampler:

    def __init__(self,filename):
        self.filename = filename
        self._l = logging.getLogger(self.__class__.__name__)
        self.c = Classifier_with_remove(training_filename="../preomr_edited_cnn.xml")
        self.c.set_k(1)

    def randompages(self,count,firstpage=1):
        doc = PDFDocument(self.filename)
        pages = doc.count_pages()
        chosen_pages = random.sample([i for i in xrange(firstpage,pages+1)],min(pages-firstpage+1,count))
        chosen_pages.sort()
        self._l.info("%s - %d pages. %s chosen",self.filename,pages,chosen_pages)
        def pi(n): return Page(self.filename,n,self.c)
        return [ pi(p) for p in chosen_pages ]

