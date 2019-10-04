from django.urls import path, include
from . import views

app_name = "charger"

urlpatterns = [
	path('', views.main_index, name="main_index"),
    path('new-measurement', views.new_measurement, name="new_measurement"),
]