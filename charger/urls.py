from django.urls import path, include
from . import views

app_name = "charger"

urlpatterns = [
    path('new-measurement', views.new_measurement, name="new_measurement"),
]