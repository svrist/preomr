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

from google.appengine.api.datastore_errors import BadValueError

from shardcounter import get_count, increment



from model import Work,Author

from base_request_handler import BaseRequestHandler, ErrorPage, templatedir, default_template_vars, Login, Logout

fetchit = False

def jsonout(resp,status = "Ok",msg = None,format=None,**kwargs):
       dat = { "status": status, "msg": msg%format }
       dat['mything'] = 1

       newt = {}
       newt.update(dat)
       newt.update(kwargs)

       logging.debug(newt)
       resp.content_type = "application/json"
       json.dump(newt, resp.out)



class Main(BaseRequestHandler):
    def get(self):
        templatevars = {"title":"PreOMR"}
        self.generate("index.html",templatevars)

class CreateAuthor(BaseRequestHandler):
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
                jsonout(resp = self.response,
                        status="dup",
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
            
            jsonout(resp = self.response,
                    status="ok",
                    msg="%s added as author with id: %d" ,
                    format=(auth.name,auth.key().id()),
                    id=auth.key().id(),
                    key = str(auth.key())
                   )
        except BadValueError, e:
            jsonout(resp = self.response,
                    status="error",
                    msg="BadValue: %s. (%s)",
                    format=(e,self.request.GET),
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

        q = Author.gql("WHERE name = :1",dat)
        if q.count(1) >0:
            auth = q.fetch(1)
            return auth[0]

        raise KeyError("%s not found in authors"%dat)


    def get(self):
        data = self.request.GET
        found = Work.gql("WHERE link = :1",data["url"])
        if found.count(1) > 0:
            work = found.fetch(1)[0]
            work.name = data['name']
            work.put()
            jsonout(self.response,
                    status="dup",
                    msg="%s already existed for %s with id %d",
                    format=(data['name'],work.author.name,work.key().id()),
                    key=str(work.key()),
                    id = work.key().id()
                   )
            return

        try: 
            a = None
            a = int(data['author'])
            author = self.get_author(a)
        except KeyError,strerror:
            jsonout(self.response,
                    status="fail",
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

        jsonout(self.response,
                status = "ok",
                msg = msg,
                id = work.key().id(),
                format = (),
                key =  str(work.key())
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
