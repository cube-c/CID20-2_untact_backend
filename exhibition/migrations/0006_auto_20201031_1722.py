# Generated by Django 3.1.2 on 2020-10-31 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exhibition', '0005_exhibit_hash'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userwithtitle',
            name='title',
            field=models.CharField(blank=True, max_length=60),
        ),
    ]