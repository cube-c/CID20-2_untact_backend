# Generated by Django 3.1.3 on 2020-12-15 19:37

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exhibition', '0006_auto_20201127_0846'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exhibit',
            name='mesh',
            field=models.FileField(upload_to='mesh/', validators=[django.core.validators.FileExtensionValidator(['glb', 'gltf'])]),
        ),
    ]
