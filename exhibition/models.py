from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.core.validators import FileExtensionValidator
from datetime import datetime
from untact.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, AWS_S3_SIGNATURE_VERSION, AWS_S3_REGION_NAME
import hashlib
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

class UserWithTitle(AbstractUser):
    title = models.CharField(max_length=60, blank=True)
    is_online = models.BooleanField(default=False)
    is_dnd = models.BooleanField(default=False)
    channel_id = models.CharField(max_length=32, blank=True)
    consumer = models.CharField(max_length=96, blank=True)

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
    name = models.CharField(max_length=40)
    mesh = models.FileField(upload_to='mesh/', validators=[FileExtensionValidator(['glb', 'gltf'])])
    summary = models.TextField(max_length=121)
    info = models.TextField(max_length=487)
    position = models.OneToOneField(Position, on_delete=models.SET_NULL, null=True, blank=True)
    hash = models.CharField(max_length=32, blank=True, editable=False)

    def __str__(self):
        return self.name
    
    def data(self):
        try:
            client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                config=Config(signature_version=AWS_S3_SIGNATURE_VERSION, region_name=AWS_S3_REGION_NAME))
            response = client.generate_presigned_url('get_object',
                Params={'Bucket': 'untact-museum', 'Key': self.mesh.name}, ExpiresIn=3600)
        except ClientError:
            response = ""
        return {
            'name': self.name,
            'mesh': response,
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