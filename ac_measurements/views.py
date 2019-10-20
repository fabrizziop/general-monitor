from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
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
	return render(request, 'charger/index-react.html')

def get_last_data_api(request):
	pass

def get_historical_data_api(request):
	pass