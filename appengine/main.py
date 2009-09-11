import cgi
import logging
import os
import random
import datetime
from google.appengine.ext import webapp
from shardcounter import get_count

import author
import svsite
import work

from base_request_handler import BaseRequestHandler, Login, Logout,main

fetchit = False

class Main(BaseRequestHandler):
    def get(self):
        templatevars = {"title":"PreOMR"}
        cnames = ["Work","Author","Work-free-score","Work-mutopia",
                  "Work-musedata",
                  "Author-free-score","Author-musedata","Author-mutopia" ]

        templatevars["countcounts"] = len(cnames)
        templatevars["counts"] = [ { 'name':cn,'count':get_count(cn)} for cn in cnames ]
        self.generate("index.html",templatevars)

class BlobInDataStore(BaseRequestHandler):
    def get(self,id):
        self.enforce_admin()
        self.response.headers['Content-Type'] = 'application/pdf'
        expires_date = datetime.datetime.utcnow() + datetime.timedelta(365)
        expires_str = expires_date.strftime("%d %b %Y %H:%M:%S GMT")
        logging.debug("Expires: %s"%expires_str)
        # self.response.headers.add_header("Expires", expires_str)
        logging.debug("id %d",id)
        work = Work.get_by_id(int(id))
        self.response.out.write(work.data)


if __name__ == "__main__":
    application = webapp.WSGIApplication(
        [('/', Main), ('/work/create',work.WorkCreate),
         ('/author/create',author.AuthorCreate),
         ('/author/read',author.AuthorRead),
         ('/login', Login),
         ('/logout', Logout),
         ('^/site/create',svsite.SiteCreate),
         ('^/site/read',svsite.SiteRead),
         ('/blob/(.*)$',BlobInDataStore),
         ('/work/createlist',work.WorkCreateList)
        ], debug=True)
    main(application)
