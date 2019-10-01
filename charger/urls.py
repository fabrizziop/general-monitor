from django.urls import path, include
from . import views
urlpatterns = [
    path('new-measurement', views.new_measurement),
]