from django.test import TestCase
from django.core.exceptions import ValidationError
from django.urls import reverse
from .models import MonitoredThingModel, PingModel
import json
import datetime
from django.utils import timezone

class APITests(TestCase):
	def test_GETting_instant_measurement(self):
		a = MonitoredThingModel(identifier_key = "a" * 64)
		a.save()
		response = self.client.get(
			reverse('pingmonitor:new_measurement'),
			{"ping_measurements": [
				{
				"thing_id": "a"*64,
				"is_up": False
				}
				]
			},
			content_type="application/json"
			)
		self.assertEqual(response.status_code, 403)
		self.assertEqual(PingModel.objects.count(), 0)
	def test_POSTing_instant_measurement(self):
		a = MonitoredThingModel(identifier_key = "a" * 64)
		a.save()
		self.assertEqual(PingModel.objects.count(), 0)
		response = self.client.post(
			reverse('pingmonitor:new_measurement'),
			{"ping_measurements": [
				{
				"thing_id": "a"*64,
				"is_up": False
				}
				]
			},
			content_type="application/json"
			)
		self.assertEqual(response.status_code, 201)
		self.assertEqual(PingModel.objects.count(), 1)
	def test_POSTing_instant_measurement_wrong_sensor(self):
		a = MonitoredThingModel(identifier_key = "a" * 64)
		a.save()
		response = self.client.post(
			reverse('pingmonitor:new_measurement'),
			{"ping_measurements": [
				{
				"thing_id": "b"*64,
				"is_up": False
				}
				]
			},
			content_type="application/json"
			)
		self.assertEqual(response.status_code, 403)
		self.assertEqual(PingModel.objects.count(), 0)
	def test_measurement_objects_saved(self):
		a = MonitoredThingModel(identifier_key = "a" * 64)
		a.save()
		b = MonitoredThingModel(identifier_key = "b" * 64)
		b.save()
		response = self.client.post(
			reverse('pingmonitor:new_measurement'),
			{"ping_measurements": [
				{
				"thing_id": "a"*64,
				"is_up": False
				}
				]
			},
			content_type="application/json"
			)
		self.assertEqual(response.status_code, 201)
		self.assertEqual(PingModel.objects.count(), 1)
		self.assertEqual(PingModel.objects.first().is_up, False)
		self.assertEqual(PingModel.objects.first().specific_thing, a)
		response = self.client.post(
			reverse('pingmonitor:new_measurement'),
			{"ping_measurements": [
				{
				"thing_id": "b"*64,
				"is_up": True
				}
				]
			},
			content_type="application/json"
			)
		self.assertEqual(response.status_code, 201)
		self.assertEqual(PingModel.objects.count(), 2)
		self.assertEqual(PingModel.objects.last().is_up, True)
		self.assertEqual(PingModel.objects.last().specific_thing, b)

class ReactViewTests(TestCase):
	def test_react_view_correct_template(self):
		response = self.client.get(reverse('pingmonitor:main_react'))
		self.assertTemplateUsed(response, 'pingmonitor/index-react.html')

class LastDataAPITests(TestCase):
	def test_only_get_is_allowed(self):
		response = self.client.post(reverse('pingmonitor:last_data'),
			{'blah': 1},
			content_type="application/json"
			)
		self.assertEqual(response.status_code, 403)
	def test_get_latest_data_when_there_are_no_monitored_things(self):
		model_a = MonitoredThingModel.objects.create(identifier_key = "a" * 64)
		response = self.client.get(reverse('pingmonitor:last_data'))
		self.assertEqual(response.status_code, 500)
	def test_latest_measurements_are_reported(self):
		model_a = MonitoredThingModel.objects.create(identifier_key = "a" * 64, thing_name = "f00f")
		f = PingModel.objects.create(specific_thing = model_a, 
			is_up=False,
			timestamp=timezone.now()-datetime.timedelta(minutes=40))
		g = PingModel.objects.create(specific_thing = model_a, 
			is_up=False,
			timestamp=timezone.now()-datetime.timedelta(minutes=35))
		response = self.client.get(reverse('pingmonitor:last_data'))
		self.assertEqual(response.status_code, 200)
		response_decoded_json = json.loads(response.content.decode('utf-8'))
		response_main_obj = response_decoded_json['all_things_data']
		self.assertEqual(response_main_obj[0]['thing_name'], model_a.thing_name)
		self.assertEqual(response_main_obj[0]['is_up'], g.is_up)
		self.assertEqual(response_main_obj[0]['timestamp'][:19]+"Z", g.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
		self.assertEqual(response_main_obj[0]['measurement_recent'], False)
	def test_old_measurement_is_reported_as_not_recent(self):
		model_a = MonitoredThingModel.objects.create(identifier_key = "a" * 64, thing_name = "f00f")
		f = PingModel.objects.create(specific_thing = model_a, 
			is_up=False,
			timestamp=timezone.now()-datetime.timedelta(minutes=40))
		g = PingModel.objects.create(specific_thing = model_a, 
			is_up=False,
			timestamp=timezone.now()-datetime.timedelta(minutes=35))
		response = self.client.get(reverse('pingmonitor:last_data'))
		self.assertEqual(response.status_code, 200)
		response_decoded_json = json.loads(response.content.decode('utf-8'))
		response_main_obj = response_decoded_json['all_things_data']
		self.assertEqual(response_main_obj[0]['measurement_recent'], False)
	def test_new_measurement_is_reported_as_recent(self):
		model_a = MonitoredThingModel.objects.create(identifier_key = "a" * 64, thing_name = "f00f")
		f = PingModel.objects.create(specific_thing = model_a, 
			is_up=False,
			timestamp=timezone.now()-datetime.timedelta(minutes=40))
		g = PingModel.objects.create(specific_thing = model_a, 
			is_up=False,
			timestamp=timezone.now()-datetime.timedelta(minutes=4, seconds=50))
		response = self.client.get(reverse('pingmonitor:last_data'))
		self.assertEqual(response.status_code, 200)
		response_decoded_json = json.loads(response.content.decode('utf-8'))
		response_main_obj = response_decoded_json['all_things_data']
		self.assertEqual(response_main_obj[0]['measurement_recent'], True)
	def test_more_than_one_sensor(self):
		model_a = MonitoredThingModel.objects.create(identifier_key = "a" * 64, thing_name = "f00f")
		model_b = MonitoredThingModel.objects.create(identifier_key = "b" * 64, thing_name = "f00f")
		c = PingModel.objects.create(specific_thing = model_a, 
			is_up=False,
			timestamp=timezone.now()-datetime.timedelta(minutes=30))
		d = PingModel.objects.create(specific_thing = model_a, 
			is_up=True,
			timestamp=timezone.now()-datetime.timedelta(minutes=10))
		e = PingModel.objects.create(specific_thing = model_a, 
			is_up=True,
			timestamp=timezone.now()-datetime.timedelta(minutes=4))
		f = PingModel.objects.create(specific_thing = model_b, 
			is_up=True,
			timestamp=timezone.now()-datetime.timedelta(minutes=40))
		g = PingModel.objects.create(specific_thing = model_b, 
			is_up=False,
			timestamp=timezone.now()-datetime.timedelta(minutes=35))
		response = self.client.get(reverse('pingmonitor:last_data'))
		self.assertEqual(response.status_code, 200)
		response_decoded_json = json.loads(response.content.decode('utf-8'))
		response_main_obj = response_decoded_json['all_things_data']
		self.assertEqual(response_main_obj[0]['thing_name'], model_a.thing_name)
		self.assertEqual(response_main_obj[0]['is_up'], e.is_up)
		self.assertEqual(response_main_obj[0]['timestamp'][:19]+"Z", e.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
		self.assertEqual(response_main_obj[0]['measurement_recent'], True)
		self.assertEqual(response_main_obj[1]['thing_name'], model_b.thing_name)
		self.assertEqual(response_main_obj[1]['is_up'], g.is_up)
		self.assertEqual(response_main_obj[1]['timestamp'][:19]+"Z", g.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
		self.assertEqual(response_main_obj[1]['measurement_recent'], False)
	def test_last_five_minutes_no_measurement(self):
		model_a = MonitoredThingModel.objects.create(identifier_key = "a" * 64, thing_name = "f00f")
		f = PingModel.objects.create(specific_thing = model_a, 
			is_up=False,
			timestamp=timezone.now()-datetime.timedelta(minutes=40))
		g = PingModel.objects.create(specific_thing = model_a, 
			is_up=False,
			timestamp=timezone.now()-datetime.timedelta(minutes=10, seconds=50))
		response = self.client.get(reverse('pingmonitor:last_data'))
		self.assertEqual(response.status_code, 200)
		response_decoded_json = json.loads(response.content.decode('utf-8'))
		response_main_obj = response_decoded_json['all_things_data']
		self.assertEqual(response_main_obj[0]['measurement_recent'], False)
		self.assertEqual(response_main_obj[0]['last_hour'], False)
		self.assertEqual(response_main_obj[0]['last_5m'], 0)
	def test_last_hour_no_measurement(self):
		model_a = MonitoredThingModel.objects.create(identifier_key = "a" * 64, thing_name = "f00f")
		f = PingModel.objects.create(specific_thing = model_a, 
			is_up=False,
			timestamp=timezone.now()-datetime.timedelta(hours=40))
		g = PingModel.objects.create(specific_thing = model_a, 
			is_up=False,
			timestamp=timezone.now()-datetime.timedelta(hours=10))
		response = self.client.get(reverse('pingmonitor:last_data'))
		self.assertEqual(response.status_code, 200)
		response_decoded_json = json.loads(response.content.decode('utf-8'))
		response_main_obj = response_decoded_json['all_things_data']
		self.assertEqual(response_main_obj[0]['measurement_recent'], False)
		self.assertEqual(response_main_obj[0]['last_hour'], 0)
		self.assertEqual(response_main_obj[0]['last_5m'], 0)
	def test_last_five_minutes_with_measurements(self):
		model_a = MonitoredThingModel.objects.create(identifier_key = "a" * 64, thing_name = "f00f")
		f = PingModel.objects.create(specific_thing = model_a, 
			is_up=True,
			timestamp=timezone.now()-datetime.timedelta(minutes=10))
		g = PingModel.objects.create(specific_thing = model_a, 
			is_up=True,
			timestamp=timezone.now()-datetime.timedelta(minutes=4))
		h = PingModel.objects.create(specific_thing = model_a, 
			is_up=False,
			timestamp=timezone.now()-datetime.timedelta(minutes=3))
		response = self.client.get(reverse('pingmonitor:last_data'))
		self.assertEqual(response.status_code, 200)
		response_decoded_json = json.loads(response.content.decode('utf-8'))
		response_main_obj = response_decoded_json['all_things_data']
		self.assertEqual(response_main_obj[0]['measurement_recent'], True)
		self.assertEqual(response_main_obj[0]['last_5m'], 5000)
	def test_last_hour_with_measurements(self):
		model_a = MonitoredThingModel.objects.create(identifier_key = "a" * 64, thing_name = "f00f")
		f = PingModel.objects.create(specific_thing = model_a, 
			is_up=True,
			timestamp=timezone.now()-datetime.timedelta(hours=2))
		g = PingModel.objects.create(specific_thing = model_a, 
			is_up=True,
			timestamp=timezone.now()-datetime.timedelta(minutes=54))
		h = PingModel.objects.create(specific_thing = model_a, 
			is_up=False,
			timestamp=timezone.now()-datetime.timedelta(minutes=43))
		response = self.client.get(reverse('pingmonitor:last_data'))
		self.assertEqual(response.status_code, 200)
		response_decoded_json = json.loads(response.content.decode('utf-8'))
		response_main_obj = response_decoded_json['all_things_data']
		self.assertEqual(response_main_obj[0]['measurement_recent'], False)
		self.assertEqual(response_main_obj[0]['last_hour'], 5000)
