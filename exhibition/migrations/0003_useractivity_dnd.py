# Generated by Django 3.1.2 on 2020-10-29 22:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exhibition', '0002_useractivity'),
    ]

    operations = [
        migrations.AddField(
            model_name='useractivity',
            name='dnd',
            field=models.BooleanField(default=False),
        ),
    ]