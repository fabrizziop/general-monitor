from django.db import models
from django.utils import timezone
# Create your models here.
class MonitoredThingModel(models.Model):
	identifier_key = models.CharField(max_length=64, unique=True)
	thing_name = models.CharField(max_length=64, default="", blank=True)
	def __str__(self):
		return self.thing_name

class PingModel(models.Model):
	specific_thing = models.ForeignKey(MonitoredThingModel, on_delete=models.CASCADE)
	is_up = models.SmallIntegerField(default=0)
	timestamp = models.DateTimeField(default=timezone.now)