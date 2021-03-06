from django.db import models

class Invitation(models.Model):
    host = models.ForeignKey('exhibition.UserWithTitle', related_name='host', on_delete=models.CASCADE)
    guest = models.ForeignKey('exhibition.UserWithTitle', related_name='guest', on_delete=models.CASCADE)
    invited_on = models.DateTimeField()

    class Meta:
        unique_together = (("host", "guest"), )