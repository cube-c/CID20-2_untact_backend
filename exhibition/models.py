from django.db import models
from django.contrib.auth.models import AbstractUser

class UserWithTitle(AbstractUser):
    title = models.CharField(max_length=150, blank=True)

class Position(models.Model):
    position_id = models.CharField(max_length=3, primary_key=True)
    posx = models.FloatField()
    posy = models.FloatField()
    posz = models.FloatField()
    roty = models.FloatField()

    def __str__(self):
        return self.position_id

class Exhibit(models.Model):
    name = models.CharField(max_length=100)
    mesh = models.FileField(upload_to='mesh/')
    summary = models.TextField(max_length=200)
    info = models.TextField(max_length=2000)
    position = models.ForeignKey(Position, on_delete=models.PROTECT)

    def __str__(self):
        return self.name