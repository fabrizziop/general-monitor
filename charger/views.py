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
			print("OK")
		except ObjectDoesNotExist:
			return HttpResponse(status=403)
		try:
			charge_session = ChargeSession.objects.get(identifier_key=json_obj["charge-session"])
		except ObjectDoesNotExist:
			charge_session = ChargeSession(specific_charger=current_charger, identifier_key=json_obj["charge-session"])
			charge_session.save()
		return HttpResponse(
			content_type='application/json',
			status=201)
	else:
		return HttpResponse(status=403)