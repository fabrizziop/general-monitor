# Generated by Django 2.2.5 on 2019-10-21 01:54

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('ac_measurements', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='currentmeasurementmodel',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]