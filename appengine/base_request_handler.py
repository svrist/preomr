import logging
import os
import random
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from django.utils import simplejson as json
from django.core import serializers

class BaseRequestHandler(webapp.RequestHandler):
    def handle_exception(self, exception, debug_mode):
        import sys
        import traceback
        from google.appengine.api import mail

        _sender = 'svrist@gmail.com'

        lines = ''.join(traceback.format_exception(*sys.exc_info ()))
        logging.error(lines)
        logging.debug("Sent to %s"%_sender)
        mail.send_mail_to_admins(sender=_sender,
        subject='Caught Exception',body=lines)
        template_values = {}

        if users.is_current_user_admin():
            template_values['traceback'] = lines

        self.generate("error.html",template_values)

    @login_required
    def enforce_admin(self):
        if not users.is_current_user_admin():
            self.redirect("/error")


    """Supplies a common template generation function"""
    def generate(self,template_name,template_values={}):
        values = {
                  'request': self.request,
                  'debug': self.request.get('deb'),
                  'application_name': 'Series Mashup'
                  }
        values.update(default_template_vars)
        values.update(template_values)
        directory = os.path.dirname(__file__)
        path = os.path.join(directory,os.path.join('templates',template_name))
        self.response.out.write(template.render(path,values,debug=_DEBUG))

    def jsonout(self,status = "Ok",msg = None,format=(),**kwargs):
        dat = { "status": status, "msg": msg%format }
        newt = {}
        newt.update(dat)
        newt.update(kwargs)
        self.response.content_type = "application/json"
        json.dump(newt, self.response.out)


class ErrorPage(BaseRequestHandler):
    def get(self):
        self.generate("not_setup.html",{'without_jquery':'yes'})

class Login(BaseRequestHandler):
    @login_required
    def get(self):
        self.redirect("/")

class Logout(BaseRequestHandler):
    def get(self):
        self.redirect(users.create_logout_url('/')) 

def real_main(application):
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(application)

def profiling_main(application):
    import cProfile, pstats, StringIO
    prof = cProfile.Profile()
    prof = prof.runctx("real_main(application)", globals(), locals())
    stream = StringIO.StringIO()
    stats = pstats.Stats(prof, stream=stream)
    stats.sort_stats("time")  # Or cumulative
    stats.print_stats(160)  # 80 = how many to print
    # The rest is optional.
    #stats.print_callees()
    #stats.print_callers()
    logging.info("Profile data:\n%s", stream.getvalue())


def main(application):
    ## Profiling on 10% of hits. 4 is 100% random choosen by dice roll!
    if random.randint(0,10) == 4:
        profiling_main(application)
    else:
        real_main(application)

##################################################################################################



templatedir = "templates/"

default_template_vars = { "logouturl" : users.create_logout_url('/'),
                         "loggedin" : not users.get_current_user() is None,
                         "admin" : users.is_current_user_admin(),
                         "user" : users.get_current_user(),
                         "loginurl" : users.create_login_url('/'),
                         "users" : users,
                         "title": "PreOMR",
                        }
_DEBUG=True
