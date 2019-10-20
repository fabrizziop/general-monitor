from django.contrib import admin
from .models import SensorModel, CurrentMeasurementModel
# Register your models here.
admin.site.register(SensorModel)
admin.site.register(CurrentMeasurementModel)