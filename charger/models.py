from django.db import models
from django.utils import timezone
# Create your models here.
class ChargerModel(models.Model):
	identifier_key = models.CharField(max_length=64, unique=True)

class ChargeSession(models.Model):
	specific_charger = models.ForeignKey(ChargerModel, on_delete=models.CASCADE)
	identifier_key = models.CharField(max_length=64, unique=True)

class IndividualMeasurementModel(models.Model):
	specific_session = models.ForeignKey(ChargeSession, on_delete=models.CASCADE)
	instantaneous_current = models.IntegerField(default=0)
	timestamp = models.DateTimeField(default=timezone.now)