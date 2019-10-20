from django.db import models
from django.utils import timezone
# Create your models here.
class SensorModel(models.Model):
	identifier_key = models.CharField(max_length=64, unique=True)
	sensor_name = models.CharField(max_length=64, default="", blank=True)
	def __str__(self):
		return self.sensor_name

class CurrentMeasurementModel(models.Model):
	specific_sensor = models.ForeignKey(SensorModel, on_delete=models.CASCADE)
	current = models.IntegerField(default=0)
	frequency = models.IntegerField(default=0)