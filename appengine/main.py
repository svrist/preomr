import cgi
import logging
import os
import random
import datetime
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp.util import login_required
from django.utils import simplejson as json

from google.appengine.api import urlfetch

from google.appengine.api import urlfetch



from model import Work,Author

from base_request_handler import BaseRequestHandler, ErrorPage, templatedir, default_template_vars, Login, Logout

def jsonout(out,status = "Ok",msg = None,format=None,**kwargs):
       dat = { "status": status, "msg": msg%format }
       dat['mything'] = 1

       newt = {}
       newt.update(dat)
       newt.update(kwargs)

       logging.debug(newt)
       json.dump(newt, out)



class Main(BaseRequestHandler):
    def get(self):
        templatevars = {"title":"PreOMR"}
        self.generate("index.html",templatevars)

class CreateAuthor(BaseRequestHandler):
    def get(self):
        name = self.request.get("name")
        info = self.request.get("info")
        site = self.request.get("site")
        auth = Author(name=name,info=info,site=site)
        auth.put()
        jsonout(out = self.response.out,
                status="ok",
                msg="Author added with id: %d" ,
                format=(auth.key().id()),
                id=auth.key().id(),
                key = str(auth.key())
               )

class BlobInDataStore(BaseRequestHandler):
    def get(self,id):
        self.enforce_admin()
        self.response.headers['Content-Type'] = 'application/pdf'
        expires_date = datetime.datetime.utcnow() + datetime.timedelta(365)
        expires_str = expires_date.strftime("%d %b %Y %H:%M:%S GMT")
        logging.debug("Expires: %s"%expires_str)
        self.response.headers.add_header("Expires", expires_str)
        logging.debug("id %d",id)
        work = Work.get_by_id(int(id))
        self.response.out.write(work.data)

class AddWork(BaseRequestHandler):

    def get_author(self,dat):
        if isinstance(dat,int):
            auth = Author.get_by_id(dat)
            if not auth is None:
                return auth
            else:
                raise KeyError("%s not found in authors"%id)

        q = Author.gql("WHERE name = :1",dat)

        if q.count(1) >0:
            auth = q.fetch(1)
            return auth


    def get(self):
        data = self.request.GET
        found = Work.gql("WHERE link = :1",data["url"])
        if found.count(1) > 0:
            work = found.fetch(1)
            jsonout(self.response.out,
                    status="dup",
                    msg="Work already existed with id %d",
                    format=(work.key().id()),
                    key=str(work.key())
                   )
            return

        try: 
            a = None
            a = data['author']
            author = self.get_author(a)
        except KeyError,strerror:
            jsonout(out = self.response.out,
                    status="fail",
                    msg="Author not found(%s:%s). Use /author/create" ,
                    format=(a,strerror))
            return

        rpc = urlfetch.create_rpc()
        blob = urlfetch.make_fetch_call(rpc,data['url'])

        work = Work(
            link = data['url'],
            blobtype= data['type'],
            author = author,
        )
        work.data = rpc.get_result().content
        work.put()
        self.response.content_type = "application/json"
        json.dump({ "status": "ok",\
                  "msg": ("%d byte data saved in store with id %d"\
                          % (len(work.data),work.key().id())),\
                   "dbid": str(work.key().id())
                                    },
                  self.response.out
                 )








def main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(application)



def real_main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(application)

def profiling_main():
    import cProfile, pstats, StringIO
    prof = cProfile.Profile()
    prof = prof.runctx("real_main()", globals(), locals())
    stream = StringIO.StringIO()
    stats = pstats.Stats(prof, stream=stream)
    stats.sort_stats("time")  # Or cumulative
    stats.print_stats(160)  # 80 = how many to print
    # The rest is optional.
    #stats.print_callees()
    #stats.print_callers()
    logging.info("Profile data:\n%s", stream.getvalue())


def main():
    ## Profiling on 10% of hits. 4 is 100% random choosen by dice roll!
    if random.randint(0,10) == 4:
        profiling_main()
    else:
        real_main()



if __name__ == "__main__":
    application = webapp.WSGIApplication(
        [('/', Main), ('/add',AddWork),
         ('/author/create',CreateAuthor),
         ('/login', Login),
         ('/logout', Logout),
         ('/blob/(.*)$',BlobInDataStore)
        ], debug=True)
    main()
