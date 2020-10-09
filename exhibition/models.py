from django.db import models

class Exhibit(models.Model):
    name = models.CharField(max_length=100, default='')
    mesh = models.FileField(upload_to='mesh/')
    info = models.TextField(default='')
    posx = models.FloatField(default=0)
    posy = models.FloatField(default=0)
    posz = models.FloatField(default=0)
    roty = models.FloatField(default=0)

    def __str__(self):
        return self.name