from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from .models import ChargerModel, ChargeSession, IndividualMeasurementModel
import json
# Create your views here.

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
		measurement_to_save.save()
		return HttpResponse(
			content_type='application/json',
			status=201)
	else:
		return HttpResponse(status=403)

def get_charger_data(request):
	if request.method == 'GET':
		#print(request.body)
		json_obj = json.loads(request.body)
		try:
			current_charger = ChargerModel.objects.get(identifier_key=json_obj["charger-id"])
			print("OK")
		except ObjectDoesNotExist:
			return HttpResponse(status=404)
		measurement_to_save = IndividualMeasurementModel(specific_session=charge_session)
		measurement_to_save.instantaneous_current = json_obj["current"]
		measurement_to_save.milliampere_second = json_obj["milliamps-second"]
		measurement_to_save.save()
		return HttpResponse(
			content_type='application/json',
			status=201)
	else:
		return HttpResponse(status=403)

# def get_session_data(request):
# 	if request.method == 'POST':
# 		#print(request.body)
# 		json_obj = json.loads(request.body)
# 		try:
# 			current_charger = ChargerModel.objects.get(identifier_key=json_obj["charger-id"])
# 			print("OK")
# 		except ObjectDoesNotExist:
# 			return HttpResponse(status=403)
# 		try:
# 			charge_session = ChargeSession.objects.get(identifier_key=json_obj["charge-session"])
# 		except ObjectDoesNotExist:
# 			charge_session = ChargeSession(specific_charger=current_charger, identifier_key=json_obj["charge-session"])
# 			charge_session.save()
# 		#saving measurement
# 		measurement_to_save = IndividualMeasurementModel(specific_session=charge_session)
# 		measurement_to_save.instantaneous_current = json_obj["current"]
# 		measurement_to_save.milliampere_second = json_obj["milliamps-second"]
# 		measurement_to_save.save()
# 		return HttpResponse(
# 			content_type='application/json',
# 			status=201)
# 	else:
# 		return HttpResponse(status=403)

# def get_all_data(request):
# 	if request.method == 'POST':
# 		#print(request.body)
# 		json_obj = json.loads(request.body)
# 		try:
# 			current_charger = ChargerModel.objects.get(identifier_key=json_obj["charger-id"])
# 			print("OK")
# 		except ObjectDoesNotExist:
# 			return HttpResponse(status=403)
# 		try:
# 			charge_session = ChargeSession.objects.get(identifier_key=json_obj["charge-session"])
# 		except ObjectDoesNotExist:
# 			charge_session = ChargeSession(specific_charger=current_charger, identifier_key=json_obj["charge-session"])
# 			charge_session.save()
# 		#saving measurement
# 		measurement_to_save = IndividualMeasurementModel(specific_session=charge_session)
# 		measurement_to_save.instantaneous_current = json_obj["current"]
# 		measurement_to_save.milliampere_second = json_obj["milliamps-second"]
# 		measurement_to_save.save()
# 		return HttpResponse(
# 			content_type='application/json',
# 			status=201)
# 	else:
# 		return HttpResponse(status=403)

# def get_last_data(request):
# 	if request.method == 'GET':
# 		#print(request.body)
# 		json_obj = json.loads(request.body)
# 		try:
# 			current_charger = ChargerModel.objects.get(identifier_key=json_obj["charger-id"])
# 			print("OK")
# 		except ObjectDoesNotExist:
# 			return HttpResponse(status=403)
# 		try:
# 			charge_session = ChargeSession.objects.get(identifier_key=json_obj["charge-session"])
# 		except ObjectDoesNotExist:
# 			charge_session = ChargeSession(specific_charger=current_charger, identifier_key=json_obj["charge-session"])
# 			charge_session.save()
# 		#saving measurement
# 		measurement_to_save = IndividualMeasurementModel(specific_session=charge_session)
# 		measurement_to_save.instantaneous_current = json_obj["current"]
# 		measurement_to_save.milliampere_second = json_obj["milliamps-second"]
# 		measurement_to_save.save()
# 		return HttpResponse(
# 			content_type='application/json',
# 			status=201)
# 	else:
# 		return HttpResponse(status=403)