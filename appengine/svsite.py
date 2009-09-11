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
from shardcounter import get_count, increment
from model import Site

class SiteCreate(BaseRequestHandler):

    def get(self):
        self.enforce_admin()
        name = self.request.get("name")
        if name is None or "" == name: 
            self.jsonout(status="error",
                    msg="No name specified",
                   )
            return
        name = name.strip()
        sq = Site.gql("WHERE name = :1",name)
        s = sq.get()
        if s is None:
            s = Site(name=name)
            s.put()
            increment("Site")
            msg = "site %s added with id %d"
            format = (s.name,s.key().id())
            self.jsonout(status="ok",msg=msg,format=format,
                    key=str(s.key()),
                    id=s.key().id()
                   )
        else:
            self.jsonout(status="dup",
                         msg="%s already existed as site with id %d",
                         format=(name,s.key().id()),
                         id=s.key().id(),
                         key=str(s.key())
                        )

class SiteRead(BaseRequestHandler):
    def get(self):
        templatevars = {"title":"PREOMR - sites"}
        sites = [ (s,get_count("Work-%s"%s.name)) for s in
                                           Site.all().fetch(100)]
        templatevars['sites'] = sites
        total = sum( [ s[1] for s in sites ] )
        templatevars["totalhere"] = total
        templatevars["overalltotal"] = get_count("Work")
        self.generate("sites.html",templatevars)
