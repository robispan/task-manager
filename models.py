from google.appengine.ext import ndb


class Tasks(ndb.Model):
    task = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
    archived = ndb.BooleanProperty(default=False)
