# Generated by Django 3.1.3 on 2020-11-27 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exhibition', '0005_remove_userwithtitle_last_activity_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userwithtitle',
            name='status',
        ),
        migrations.AddField(
            model_name='userwithtitle',
            name='is_dnd',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userwithtitle',
            name='is_online',
            field=models.BooleanField(default=False),
        ),
    ]
