# Generated by Django 3.1.3 on 2020-11-21 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exhibition', '0002_auto_20201121_0854'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userwithtitle',
            name='channel_id',
            field=models.CharField(blank=True, max_length=32),
        ),
    ]
