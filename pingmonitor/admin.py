from django.contrib import admin
from .models import MonitoredThingModel, PingModel
# Register your models here.
admin.site.register(MonitoredThingModel)
admin.site.register(PingModel)