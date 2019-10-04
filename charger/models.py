from django.db import models
from django.utils import timezone
# Create your models here.
class ChargerModel(models.Model):
	identifier_key = models.CharField(max_length=64, unique=True)
	charger_name = models.CharField(max_length=64, default="", blank=True)
	def __str__(self):
		return self.charger_name

class ChargeSession(models.Model):
	specific_charger = models.ForeignKey(ChargerModel, on_delete=models.CASCADE)
	identifier_key = models.CharField(max_length=64, unique=True)

class IndividualMeasurementModel(models.Model):
	specific_session = models.ForeignKey(ChargeSession, on_delete=models.CASCADE)
	instantaneous_current = models.IntegerField(default=0)
	instantaneous_voltage = models.IntegerField(default=0)
	emergency_status = models.IntegerField(default=False)
	milliampere_second = models.IntegerField(default=0)
	timestamp = models.DateTimeField(default=timezone.now)