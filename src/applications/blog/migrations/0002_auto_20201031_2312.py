# Generated by Django 3.1.2 on 2020-10-31 20:12

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2020, 10, 31, 20, 12, 30, 41751, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='post',
            name='visible',
            field=models.BooleanField(default=True),
        ),
    ]
