from django.urls import path, include
from . import views

app_name = "ac_measurements"

urlpatterns = [
	#path('nojs/', views.main_index, name="main_index"),
	path('', views.main_react, name="main_react"),
    path('new-measurement', views.new_measurement, name="new_measurement"),
    #path('last-data', views.get_last_data_api, name="last_data"),
    #path('session-data', views.get_historical_data_api, name="historical_data")
]