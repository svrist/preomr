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

from base_request_handler import BaseRequestHandler
from model import Work,SavedList
import random
import logging
import author as A
from shardcounter import get_count, increment
from google.appengine.api import urlfetch
from google.appengine.ext import db

fetchit = False

class WorkCreate(BaseRequestHandler):
    def get(self):
        data = self.request.GET
        found = Work.gql("WHERE link = :1",data["url"])
        if found.count(1) > 0:
            work = found.fetch(1)[0]
            work.name = data['name']
            work.put()
            self.jsonout(status="dup",
                    msg="%s already existed for %s with id %d",
                    format=(data['name'],work.author.name,work.key().id()),
                    key=str(work.key()),
                    id = work.key().id()
                   )
            return

        try: 
            a = None
            a = int(data['author'])
            author = A.get_author(a)
        except KeyError,strerror:
            self.jsonout(status="fail",
                    msg="Author not found(%s:%s). Use /author/create" ,
                    format=(a,strerror))
            return
        work = Work(
            link = data['url'],
            blobtype= data['type'],
            name = data['name'],
            author = author,
            site = author.site,
        )
        work.put()
        increment("Work")
        increment("Work-%d"%author.key().id())
        increment("Work-%s"%author.site)

        if fetchit:
            rpc = urlfetch.create_rpc()
            blob = urlfetch.make_fetch_call(rpc,data['url'])
            data = rpc.get_result().content
            l = len(data)
            if len(data) < 100000:
                work.data = data
                work.put()
                msg = "%s  - %d byte data saved in store with id %d"
            else:
                msg = "%s - %d byte is too much for datastore. Not inserting pdf. Id %d"
            msg = msg % (work.name,l,work.key())
        else:
            msg = "%s - Fetching disabled. %s - Id %d"%(work.name,work.link,work.key().id())

        self.jsonout(status = "ok",
                     msg = msg,
                     id = work.key().id(),
                     format = (),
                     key =  str(work.key())
                    )


class WorkCreateList(BaseRequestHandler):
    def get(self):
        count = self.request.get("count")
        site = self.request.get("site")
        name = self.request.get("name").strip()
        if count is None or count is "":
            count = 10

        if site is None or site is "":
            workcount=int(get_count("Work"))
        else:
            workcount=int(get_count("Work-%s"%site))

        logging.debug("%d",workcount)
        self.response.out.write("Workcount %d, count %d"%(workcount,count))
        numberlist = random.sample(range(0,workcount-1),count)
        numberlist.sort()
        self.response.out.write("Numberlist %s"%numberlist)
        wq = db.GqlQuery("SELECT __key__ FROM Work ORDER BY name")
        keylist = [ wq.fetch(1,c)[0] for c in numberlist ]
        self.response.out.write("Works %s"%keylist)
        s = SavedList(name=name,keys=keylist,size=len(keylist))
        s.put()
        self.response.out.write("SavedList: %d"%s.key().id())


