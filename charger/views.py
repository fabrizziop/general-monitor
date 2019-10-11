from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from .models import ChargerModel, ChargeSession, IndividualMeasurementModel
import json
# Create your views here.

@csrf_exempt
def new_measurement(request):
	if request.method == 'POST':
		#print(request.body)
		json_obj = json.loads(request.body)
		try:
			current_charger = ChargerModel.objects.get(identifier_key=json_obj["charger-id"])
		except ObjectDoesNotExist:
			return HttpResponse(status=403)
		try:
			charge_session = ChargeSession.objects.get(identifier_key=json_obj["charge-session"])
		except ObjectDoesNotExist:
			charge_session = ChargeSession(specific_charger=current_charger, identifier_key=json_obj["charge-session"])
			charge_session.save()
		#saving measurement
		measurement_to_save = IndividualMeasurementModel(specific_session=charge_session)
		measurement_to_save.instantaneous_current = json_obj["current"]
		measurement_to_save.instantaneous_voltage = json_obj["voltage"]
		measurement_to_save.milliampere_second = json_obj["milliamps-second"]
		measurement_to_save.emergency_status = json_obj["emergency"]
		charge_session.mas_sum = charge_session.mas_sum + measurement_to_save.milliampere_second
		charge_session.save()
		measurement_to_save.save()
		return HttpResponse(
			content_type='application/json',
			status=201)
	else:
		return HttpResponse(status=403)

def main_index(request):
	all_chargers = ChargerModel.objects.all()
	return render(request, 'charger/index.html',
		context={"all_chargers": all_chargers})

def main_react(request):
	return render(request, 'charger/index-react.html')

def get_last_data_api(request):
	if request.method != "GET":
		return HttpResponse(status=403)
	data_to_send = []
	for charger in ChargerModel.objects.all():
		try:
			last_session = charger.chargesession_set.latest('id')
			last_measurement = last_session.individualmeasurementmodel_set.latest('id')
			temp_data = {
				'charger_id': charger.identifier_key,
				'charger_name': charger.charger_name,
				'last_session_id': last_session.identifier_key,
				'last_session_mas': last_session.mas_sum,
				'last_measurement': {
					'voltage': last_measurement.instantaneous_voltage,
					'current': last_measurement.instantaneous_current,
					'emergency': last_measurement.emergency_status,
					'mas': last_measurement.milliampere_second,
					'timestamp': last_measurement.timestamp
				}
			}
		except ObjectDoesNotExist:
			return HttpResponse(status=500)
		data_to_send.append(temp_data)
	return JsonResponse({'all_chargers_data': data_to_send}, status=200)
