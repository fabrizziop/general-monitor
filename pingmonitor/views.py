from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Avg
import datetime
from .models import MonitoredThingModel, PingModel
import json
# Create your views here.

@csrf_exempt
def new_measurement(request):
	if request.method == 'POST':
		#print(request.body)
		json_obj = json.loads(request.body)
		for ping_monitor_object in json_obj["ping_measurements"]:
			try:
				current_thing = MonitoredThingModel.objects.get(identifier_key=ping_monitor_object["thing_id"])
			except ObjectDoesNotExist:
				return HttpResponse(status=403)
			#saving measurement
			new_measurement = PingModel.objects.create(specific_thing=current_thing, 
				is_up=ping_monitor_object["is_up"])
		return HttpResponse(
			content_type='application/json',
			status=201)
	else:
		return HttpResponse(status=403)

def main_react(request):
	return render(request, 'pingmonitor/index-react.html')

def get_last_data_api(request):
	if request.method != "GET":
		return HttpResponse(status=403)
	data_to_send = []
	for thing in MonitoredThingModel.objects.all():
		#checking if charger has any measurements:
		try:
			last_measurement = thing.pingmodel_set.latest('id')
			measurement_received_short_time_ago = (timezone.now() - last_measurement.timestamp) <= datetime.timedelta(minutes=5)
			last_five_minutes = thing.pingmodel_set.filter(timestamp__gte=(timezone.now() - datetime.timedelta(minutes=5)))
			last_hour = thing.pingmodel_set.filter(timestamp__gte=(timezone.now() - datetime.timedelta(hours=1)))
			last_five_minutes_avg = last_five_minutes.aggregate(Avg('is_up'))['is_up__avg']
			last_five_minutes_average_uptime = int(last_five_minutes_avg*10000) if last_five_minutes_avg != None else 0
			last_hour_avg = last_hour.aggregate(Avg('is_up'))['is_up__avg']
			last_hour_average_uptime = int(last_hour_avg*10000) if last_hour_avg != None else 0
			temp_data = {
				'thing_name': thing.thing_name,
				'is_up': last_measurement.is_up,
				'timestamp': last_measurement.timestamp,
				'measurement_recent': measurement_received_short_time_ago,
				'last_5m': last_five_minutes_average_uptime,
				'last_hour': last_hour_average_uptime
			}
		except ObjectDoesNotExist:
			return HttpResponse(status=500)
		data_to_send.append(temp_data)
	return JsonResponse({'all_things_data': data_to_send}, status=200)
