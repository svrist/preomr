from google.appengine.ext.db import djangoforms
from model import SavedList

class SavedListForm(djangoforms.ModelForm):
    class Meta:
        model = SavedList
        exclude=['created','updated','keys','ids']

