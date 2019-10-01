from django.db import models
from django.utils import timezone
# Create your models here.
class ChargerModel(models.Model):
	identifier_key = models.CharField(max_length=64, unique=True)

class IndividualMeasurementModel(models.Model):
	specific_charger = models.ForeignKey(ChargerModel, on_delete=models.CASCADE)
	timestamp = models.DateTimeField(default=timezone.now)