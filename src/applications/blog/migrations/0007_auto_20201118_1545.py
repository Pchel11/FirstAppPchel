# Generated by Django 3.1.3 on 2020-11-18 12:45

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_auto_20201111_2158'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2020, 11, 18, 12, 45, 29, 250951, tzinfo=utc)),
        ),
    ]
