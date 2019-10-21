from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Avg
import datetime
from .models import SensorModel, CurrentMeasurementModel
import json
# Create your views here.

@csrf_exempt
def new_measurement(request):
	if request.method == 'POST':
		#print(request.body)
		json_obj = json.loads(request.body)
		try:
			current_sensor = SensorModel.objects.get(identifier_key=json_obj["sensor_id"])
		except ObjectDoesNotExist:
			return HttpResponse(status=403)
		#saving measurement
		new_measurement = CurrentMeasurementModel.objects.create(specific_sensor=current_sensor, 
			current=json_obj["current"], frequency=json_obj["frequency"])
		return HttpResponse(
			content_type='application/json',
			status=201)
	else:
		return HttpResponse(status=403)

def main_react(request):
	return render(request, 'ac_measurements/index-react.html')

def get_last_data_api(request):
	if request.method != "GET":
		return HttpResponse(status=403)
	data_to_send = []
	for sensor in SensorModel.objects.all():
		#checking if charger has any measurements:
		try:
			last_measurement = sensor.currentmeasurementmodel_set.latest('id')
			measurement_received_short_time_ago = (timezone.now() - last_measurement.timestamp) <= datetime.timedelta(minutes=5)
			last_five_minutes = sensor.currentmeasurementmodel_set.filter(timestamp__gte=(timezone.now() - datetime.timedelta(minutes=5)))
			last_hour = sensor.currentmeasurementmodel_set.filter(timestamp__gte=(timezone.now() - datetime.timedelta(hours=1)))
			last_five_minutes_average_current = last_five_minutes.aggregate(Avg('current'))['current__avg']
			last_hour_average_current = last_hour.aggregate(Avg('current'))['current__avg']
			temp_data = {
				'sensor_name': sensor.sensor_name,
				'last_current': last_measurement.current,
				'last_frequency': last_measurement.frequency,
				'timestamp': last_measurement.timestamp,
				'measurement_recent': measurement_received_short_time_ago,
				'last_5m': last_five_minutes_average_current,
				'last_hour': last_hour_average_current
			}
		except ObjectDoesNotExist:
			return HttpResponse(status=500)
		data_to_send.append(temp_data)
	return JsonResponse({'all_sensors_data': data_to_send}, status=200)

def get_historical_data_api(request):
	pass