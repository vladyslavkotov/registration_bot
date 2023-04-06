from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
   userpic = models.ImageField(default='/userpics/default.jpg', upload_to='userpics')
