# Generated by Django 3.1.2 on 2020-10-31 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exhibition', '0004_auto_20201031_1112'),
    ]

    operations = [
        migrations.AddField(
            model_name='exhibit',
            name='hash',
            field=models.CharField(blank=True, editable=False, max_length=32),
        ),
    ]