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

import logging
import os
import sys
import os
import random
import time
from subprocess import Popen,PIPE,STDOUT
from pdftools.pdffile import PDFDocument
from sheetmusic import *

gspath="\"c:/Program Files/gs/gs8.70/bin/gswin32c.exe\"".replace("/","\\")

class Page:

    def __init__(self,origfile,pagenumber):
        self._pagenumber = pagenumber
        self._file = None
        self._origfile = origfile
        self._noend = origfile[:-4]
        self.l = logging.getLogger(self.__class__.__name__)

    def save(self,filename=None):
        if filename is None:
            filename = "%s/%s-page%02d.tif"%\ (self._noend,self._noend,self._pagenumber)
            logging.info("Filename not given. Using %s",filename)
            if not os.path.exists(noend):
                self.l.debug("%s dir dint exits. Creating it.",noend)
                os.mkdir(noend)

        cmd = ' '.join([gspath,
                            '-dNOPAUSE',
                            '-q',
                            '-r300',
                            '-sDEVICE=tiffg4',
                            '-dBATCH',
                            '-sOutputFile=%s'%filename,
                            '-sPAPERSIZE=a4',
                            '-dFirstPage=%d'%self.pagenumber,
                            '-dLastPage=%d'%self.pagenumber,
                            file
                        ])
        po = Popen(cmd,shell=True,stdout=PIPE,stderr=STDOUT).stdout
        for l in po.readlines():
            self.l.debug("GS Output:%s",l)
        po.close()
        self._file = filename

    def save_nostaves(self,filename=None):
        if self._file is None:
            self.l.debug("No converted tif page. Forcing one now.")
            self.save()

        if filename is None:
            filename = self.genfilename()
            self.l.info("Filename not given. Using %s",filename)

         mi = MusicImage(self._file)
         mi.without_staves().save_PNG(filename)
         self._nostavesfile = filename

    def genfilename(self,base,postfix=""):
        filename = "%s/%s-page%02d%s.tif"%\
                (self._noend,self._noend,self._pagenumber,postfix)
        if not os.path.exists(noend):
            logging.debug("%s dir dint exits. Creating it.",noend)
            os.mkdir(noend)
        return filename

class Pdfsampler:

    def __init__(self,filename):
        self.filename = filename
        self.l = logging.getLogger(self.__class__.__name__)

    def randompages(self,count):
        doc = PDFDocument(self.filename)
        pages = doc.count_pages()
        chosen_pages = random.sample([i for i in xrange(1,pages+1)],min(pages,10))
        chosen_pages.sort()
        self.l.info("%s - %d pages. %s chosen",self.filename,pages,chosen_pages)
