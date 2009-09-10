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

from google.appengine.api.datastore_errors import BadValueError

from base_request_handler import BaseRequestHandler
from model import Author
from shardcounter import get_count, increment

class AuthorCreate(BaseRequestHandler):
    def get(self):
        siteurl = self.request.get("site-url").strip()
        name = self.request.get("name").strip()
        site = self.request.get("site").strip()
        try:
            exist = Author.gql("WHERE name = :1 and site = :2",
                               name,
                               site)
            if exist.count(1) > 0:
                a = exist.fetch(1)[0]
                a.siteurl = siteurl
                self.jsonout(status="dup",
                             msg="%s existed with id %d",
                             format=(a.name,a.key().id()),
                             id=a.key().id(),
                             key=str(a.key())
                            )
                return

            auth = Author(
                name = name,
                site = site,
                siteurl = siteurl,
            )
            auth.put()
            increment("Author")
            increment("Author-%s"%site)
            
            self.jsonout(status="ok",
                         msg="%s added as author with id: %d" ,
                         format=(auth.name,auth.key().id()),
                         id=auth.key().id(),
                         key = str(auth.key())
                        )
        except BadValueError, e:
            self.jsonout(status="error",
                         msg="BadValue: %s. (%s)",
                         format=(e,self.request.GET),
                        )

class AuthorRead(BaseRequestHandler):
    def get(self):
        self.jsonout(status="error",msg="AuthorReadNotImplementedYet")

def get_author(dat):
    if isinstance(dat,int):
        auth = Author.get_by_id(dat)
        if not auth is None:
            return auth

        q = Author.gql("WHERE name = :1",dat)
        if q.count(1) >0:
            auth = q.fetch(1)
            return auth[0]

        raise KeyError("%s not found in authors"%dat)

