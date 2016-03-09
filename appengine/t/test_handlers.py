import unittest
import webapp2
import webtest
from google.appengine.ext import testbed



class AppTest(unittest.TestCase):
    def setUp(self):
        # Create a WSGI application.
        # Wrap the app with WebTest TestApp.
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_user_stub()
        from main import Main
        app = webapp2.WSGIApplication([('/', Main)])
        self.testapp = webtest.TestApp(app)

    def tearDown(self):
        self.testbed.deactivate()

    # Test the handler.
    def testHelloWorldHandler(self):
        response = self.testapp.get('/')
        self.assertEqual(response.status_int, 200)
        text_in = 'Optical Music Recognition for structural information'
        assert text_in in response.normal_body, response.normal_body
        self.assertEqual(response.content_type, 'text/html')
