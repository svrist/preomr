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
import logging
import author as A
from shardcounter import increment,get_count
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

class WorkRead(BaseRequestHandler):
    def get(self,id):
        pass


class WorkReadCached(BaseRequestHandler):
    def get(self,id):
        pass

class Cache(BaseRequestHandler):
    def get(self,id):
        work = Work.get_by_id(int(id))
        rpc = urlfetch.create_rpc()
        blob = urlfetch.make_fetch_call(rpc,work.link)
        data = rpc.get_result().content
        l = len(data)
        if len(data) < 100000:
            work.data = data
            work.put()
            msg = "%s  - %d byte data saved in store with id %d"
            msg = msg % (work.name,l,work.key().id())
        else:
            msg = "%s - %d byte is too much for datastore. Not inserting pdf. Id %d"
            msg = msg % (work.name,l,work.key().id())

        self.jsonout(status="ok",msg=msg)



class WorkReadList(BaseRequestHandler):
    def get(self,id):
        keylist = SavedList.get_by_id(int(id))
        templatevars = {"works":Work.get(keylist.keys)}
        templatevars["overalltotal"] = get_count("Work")
        templatevars["totalhere"] = len(keylist.keys)
        templatevars["listname"] = keylist.name
        self.generate("listofworks.html",templatevars)
        pass
