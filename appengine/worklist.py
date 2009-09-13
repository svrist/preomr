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
from google.appengine.ext import db
from base_request_handler import BaseRequestHandler
from shardcounter import increment,get_count
from model import Work,SavedList,SavedListForm
import random

class Create(BaseRequestHandler):
    def get(self):
        pagesize = 1000
        count = int(self.request.get("size",default_value=10))
        site = self.request.get("site",default_value=None)
        name = self.request.get("name",default_value=None)
        if name is None:
            self.jsonout(status="error",msg="Name is not specified for list")
            return
        else:
            name = name.strip()

        wq = db.Query(Work,keys_only=True).order("__key__")

        if site is None:
            workcount=int(get_count("Work"))
        else:
            wq.filter("site =",site)
            workcount=int(get_count("Work-%s"%site))

        if count > workcount:
            self.jsonout(status="error",msg="Tried to find %s out of %s. Not possible", 
                         format=(count,workcount))
            return


        # select $count from the complete set
        numberlist = random.sample(range(0,workcount-1),count)
        numberlist.sort()

        #initbuckets
        buckets = [ [] for i in xrange(int(max(numberlist)/pagesize)+1) ]
        for k in numberlist:
            thisb = int(k/pagesize)
            buckets[thisb].append(k-(thisb*pagesize))
        logging.debug("Numbers: %s. Buckets %s",numberlist,buckets)

        #page through results.
        result = []
        baseq =  wq
        for b,l in enumerate(buckets):
            if len(l) > 0:
                result += [ wq.fetch(limit=1,offset=e)[0] for e in l ]

            if b < len(buckets)-1: # not the last bucket
                lastkey  = wq.fetch(1,pagesize-1)[0]
                wq = baseq.filter("__key__ >",lastkey)

        s = SavedList(name=name,keys=result,size=len(result),site=site,ids=numberlist)
        increment("/work/list")
        if not site is None:
            increment("/work/%s/list"%site)
        s.put()
        self.jsonout(status="ok", msg="Created list %s with %d items.List id %d",
                     format=(s.name,s.size,s.key().id()),id=s.key().id())

class Read(BaseRequestHandler):
    def get(self):
        count = self.request.get("count",default_value=10)
        templatevars = {}
        l = SavedList.all().order("-created").fetch(count)
        templatevars["list"] = l
        templatevars["totalhere"] = len(l)
        templatevars["overalltotal"] = get_count("/work/list")
        self.generate("readlist.html",templatevars)


class CreateForm(BaseRequestHandler):
    def get(self):
        templatevars = {"form":SavedListForm()}
        self.generate("createlist.html",templatevars)
