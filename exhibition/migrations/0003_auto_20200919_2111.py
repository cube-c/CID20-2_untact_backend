# Generated by Django 3.1.1 on 2020-09-19 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exhibition', '0002_auto_20200919_2103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exhibit',
            name='name',
            field=models.CharField(default='', max_length=100),
        ),
    ]
