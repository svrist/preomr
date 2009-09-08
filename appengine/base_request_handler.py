import logging
import os
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required

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

##################################################################################################


templatedir = "templates/"

default_template_vars = { "without_jquery": "no",
                          "with_config": "no",
                         "logouturl" : users.create_logout_url('/'),
                         "loggedin" : users.get_current_user is not None,
                        }


_DEBUG=True
