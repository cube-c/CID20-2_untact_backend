from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, User
from datetime import datetime

class UserWithTitle(AbstractUser):
    title = models.CharField(max_length=150, blank=True)

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

    def __str__(self):
        return self.name
    
    def data(self):
        return {
            'name': self.name,
            'mesh': self.mesh.name,
            'summary': self.summary,
            'info': self.info,
            'position_id': self.position.position_id,
            'posx': self.position.posx,
            'posy': self.position.posy,
            'posz': self.position.posz,
            'roty': self.position.roty,
        }

class UserActivity(models.Model):
    last_activity_ip = models.GenericIPAddressField()
    last_activity_date = models.DateTimeField(default = datetime(1950,1,1))
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    dnd = models.BooleanField(default = False) #Do not distrub