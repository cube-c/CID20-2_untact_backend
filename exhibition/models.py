from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, User
from annoying.fields import AutoOneToOneField
from datetime import datetime
import hashlib

class UserWithTitle(AbstractUser):
    title = models.CharField(max_length=60, blank=True)

class Position(models.Model):
    position_id = models.CharField(max_length=3, unique=True)
    posx = models.FloatField()
    posy = models.FloatField()
    posz = models.FloatField()
    roty = models.FloatField()

    class Meta:
        ordering = ['position_id']

    def __str__(self):
        return self.position_id
    
class Exhibit(models.Model):
    name = models.CharField(max_length=38)
    mesh = models.FileField(upload_to='mesh/')
    summary = models.TextField(max_length=121)
    info = models.TextField(max_length=487)
    position = models.OneToOneField(Position, on_delete=models.SET_NULL, null=True, blank=True)
    hash = models.CharField(max_length=32, blank=True, editable=False)

    def __str__(self):
        return self.name
    
    def data(self):
        return {
            'name': self.name,
            'mesh': self.mesh.name,
            'hash': self.hash,
            'summary': self.summary,
            'info': self.info,
            'position_id': self.position.position_id,
            'posx': self.position.posx,
            'posy': self.position.posy,
            'posz': self.position.posz,
            'roty': self.position.roty,
        }
    
    def save(self, *args, **kwargs):
        with self.mesh.open('rb') as file:
            hash = hashlib.md5()
            if file.multiple_chunks():
                for chunk in file.chunks():
                    hash.update(chunk)
            else:
                hash.update(file.read())
            self.hash = hash.hexdigest()
            super(Exhibit, self).save(*args, **kwargs)

class UserActivity(models.Model):
    last_activity_ip = models.GenericIPAddressField()
    last_activity_date = models.DateTimeField(default = datetime(1950,1,1))
    user = AutoOneToOneField(settings.AUTH_USER_MODEL, primary_key = True, on_delete=models.CASCADE)
    dnd = models.BooleanField(default = False) #Do not distrub

    def date(self):
        return {
            'last_activity_ip' : self.last_activity_ip,
            'last_activity_date' : self.last_activity_date,
            'user' : self.user,
            'dnd' : self.dnd,
        }