from django.contrib import admin
from .models import ChargerModel, ChargeSession, IndividualMeasurementModel
# Register your models here.
admin.site.register(ChargerModel)
admin.site.register(ChargeSession)
admin.site.register(IndividualMeasurementModel)