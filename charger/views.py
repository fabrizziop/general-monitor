from django.shortcuts import render
from django.http import HttpResponse
from .models import ChargerModel, ChargeSession, IndividualMeasurementModel
import json
# Create your views here.

def new_measurement(request):
	if request.method == 'POST':
		print(request.body)
		json_obj = json.loads(request.body)
		charger_count = ChargerModel.objects.filter(identifier_key=json_obj["charger-id"]).count()
		if charger_count > 0:
			return HttpResponse(
				content_type='application/json',
				status=201)
		else:
			return HttpResponse(status=403)
	else:
		return HttpResponse(status=403)