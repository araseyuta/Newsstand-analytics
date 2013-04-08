from appengine_django.models import BaseModel
from google.appengine.ext import db
from django import forms

class SKU(BaseModel):
  SKU = db.StringProperty()
  price = db.IntegerProperty()
  ParentIdentifier = db.StringProperty()
  AppleID = db.IntegerProperty() 
  
class User(BaseModel):
  email = db.StringProperty()
  user_id = db.StringProperty()
  nickname = db.StringProperty()
  datetime = db.DateTimeProperty()