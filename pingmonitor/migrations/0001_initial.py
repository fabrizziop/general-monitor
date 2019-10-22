# Generated by Django 2.2.5 on 2019-10-22 02:20

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MonitoredThingModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier_key', models.CharField(max_length=64, unique=True)),
                ('thing_name', models.CharField(blank=True, default='', max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='PingModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_up', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('specific_thing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pingmonitor.MonitoredThingModel')),
            ],
        ),
    ]
