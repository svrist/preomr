
from google.appengine.ext import db

class Author(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty()
    info = db.TextProperty()
    site = db.TextProperty()
    siteurl = db.LinkProperty()

class Work(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty()
    link = db.LinkProperty()
    author = db.ReferenceProperty(Author)
    blobtype = db.StringProperty(choices = [
        "pdf", "tif","jpg","png" ])
    data = db.BlobProperty()

