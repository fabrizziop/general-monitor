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
	return render(request, 'ac_measurements/index-react.html')

def get_last_data_api(request):
	if request.method != "GET":
		return HttpResponse(status=403)
	data_to_send = []
	for charger in ChargerModel.objects.all():
		#checking if charger has any measurements:
		try:
			last_session = charger.chargesession_set.latest('id')
			last_measurement = last_session.individualmeasurementmodel_set.latest('id')
			measurement_received_short_time_ago = (timezone.now() - last_measurement.timestamp) <= datetime.timedelta(minutes=5)
			temp_data = {
				'charger_name': charger.charger_name,
				'last_session_id': last_session.identifier_key,
				'last_session_mas': last_session.mas_sum,
				'last_session_begin': last_session.individualmeasurementmodel_set.first().timestamp,
				'measurement_recent': measurement_received_short_time_ago,
				'current_outage': {
					'valid': False,
					'emergency': False,
					'timestamp': False,
				},
				'previous_outage': {
					'valid': False,
					'emergency': False,
					'timestamp_start': False,
					'timestamp_end': False,
				},
				'last_measurement': {
					'voltage': last_measurement.instantaneous_voltage,
					'current': last_measurement.instantaneous_current,
					'emergency': last_measurement.emergency_status,
					'mas': last_measurement.milliampere_second,
					'timestamp': last_measurement.timestamp
				}
			}
			current_outage_filter = last_session.individualmeasurementmodel_set.filter(emergency_status__gt=0)
			if current_outage_filter.count() > 0:
				current_outage_cause = current_outage_filter.first()
				temp_data['current_outage'] = {
					'valid': True,
					'emergency': current_outage_cause.emergency_status,
					'timestamp': current_outage_cause.timestamp
				}
			previous_outage_filter = charger.chargesession_set.filter(individualmeasurementmodel__emergency_status__gt=0).distinct().exclude(id=last_session.id)
			if previous_outage_filter.count() > 0:
				previous_outage_session = previous_outage_filter.all().last()
				previous_outage_cause = previous_outage_session.individualmeasurementmodel_set.filter(emergency_status__gt=0).first()
				outage_end_session = charger.chargesession_set.get(id=previous_outage_session.id+1)
				outage_end_measurements = outage_end_session.individualmeasurementmodel_set.filter(emergency_status=0)
				if outage_end_measurements.count() == 0:
					outage_end_time = False
				else:
					outage_end_time = outage_end_measurements.first().timestamp
				temp_data['previous_outage'] = {
					'valid': True,
					'emergency': previous_outage_cause.emergency_status,
					'timestamp_start': previous_outage_cause.timestamp,
					'timestamp_end': outage_end_time
				}
		except ObjectDoesNotExist:
			return HttpResponse(status=500)
		data_to_send.append(temp_data)
	return JsonResponse({'all_chargers_data': data_to_send}, status=200)

def get_historical_data_api(request):
	pass