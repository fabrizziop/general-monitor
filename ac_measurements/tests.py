from django.test import TestCase
from django.core.exceptions import ValidationError
from django.urls import reverse
from .models import SensorModel, CurrentMeasurementModel
import json
import datetime
from django.utils import timezone
# Create your tests here.
def generate_test_recv_object(sensor_id="a"*64, current=6, frequency=6000):
	return {'sensor_id': sensor_id,
		'current': current,
		'frequency': frequency,
		}
class APITests(TestCase):
	def test_GETting_instant_measurement(self):
		a = SensorModel(identifier_key = "a" * 64)
		a.save()
		response = self.client.get(
			reverse('ac_measurements:new_measurement'),
			generate_test_recv_object(),
			content_type="application/json"
			)
		self.assertEqual(response.status_code, 403)
		self.assertEqual(CurrentMeasurementModel.objects.count(), 0)
	def test_POSTing_instant_measurement(self):
		a = SensorModel(identifier_key = "a" * 64)
		a.save()
		self.assertEqual(CurrentMeasurementModel.objects.count(), 0)
		response = self.client.post(
			reverse('ac_measurements:new_measurement'),
			generate_test_recv_object(),
			content_type="application/json"
			)
		self.assertEqual(response.status_code, 201)
		self.assertEqual(CurrentMeasurementModel.objects.count(), 1)
	def test_POSTing_instant_measurement_wrong_sensor(self):
		a = SensorModel(identifier_key = "a" * 64)
		a.save()
		response = self.client.post(
			reverse('ac_measurements:new_measurement'),
			generate_test_recv_object(sensor_id = "b" * 64),
			content_type="application/json"
			)
		self.assertEqual(response.status_code, 403)
		self.assertEqual(CurrentMeasurementModel.objects.count(), 0)
	def test_measurement_objects_saved(self):
		a = SensorModel(identifier_key = "a" * 64)
		a.save()
		b = SensorModel(identifier_key = "b" * 64)
		b.save()
		response = self.client.post(
			reverse('ac_measurements:new_measurement'),
			generate_test_recv_object(sensor_id="a"*64, current=122, frequency=9999),
			content_type="application/json"
			)
		self.assertEqual(response.status_code, 201)
		self.assertEqual(CurrentMeasurementModel.objects.count(), 1)
		self.assertEqual(CurrentMeasurementModel.objects.first().current, 122)
		self.assertEqual(CurrentMeasurementModel.objects.first().frequency, 9999)
		self.assertEqual(CurrentMeasurementModel.objects.first().specific_sensor, a)
		response = self.client.post(
			reverse('ac_measurements:new_measurement'),
			generate_test_recv_object(sensor_id="b"*64, current=99, frequency=1),
			content_type="application/json"
			)
		self.assertEqual(response.status_code, 201)
		self.assertEqual(CurrentMeasurementModel.objects.count(), 2)
		self.assertEqual(CurrentMeasurementModel.objects.last().current, 99)
		self.assertEqual(CurrentMeasurementModel.objects.last().frequency, 1)
		self.assertEqual(CurrentMeasurementModel.objects.last().specific_sensor, b)

class ReactViewTests(TestCase):
	def test_react_view_correct_template(self):
		response = self.client.get(reverse('ac_measurements:main_react'))
		self.assertTemplateUsed(response, 'ac_measurements/index-react.html')

class LastDataAPITests(TestCase):
	def test_only_get_is_allowed(self):
		response = self.client.post(reverse('ac_measurements:last_data'),
			{'blah': 1},
			content_type="application/json"
			)
		self.assertEqual(response.status_code, 403)
	def test_get_latest_session_data_when_there_are_no_sessions(self):
		model_a = SensorModel.objects.create(identifier_key = "a" * 64)
		response = self.client.get(reverse('ac_measurements:last_data'))
		self.assertEqual(response.status_code, 500)
	def test_latest_measurements_are_reported(self):
		model_a = SensorModel.objects.create(identifier_key = "a" * 64, sensor_name = "f00f")
		f = CurrentMeasurementModel.objects.create(specific_sensor = model_a, 
			current=100,
			frequency=2800,
			timestamp=timezone.now()-datetime.timedelta(minutes=40))
		g = CurrentMeasurementModel.objects.create(specific_sensor = model_a, 
			current=100,
			frequency=2800,
			timestamp=timezone.now()-datetime.timedelta(minutes=35))
		response = self.client.get(reverse('ac_measurements:last_data'))
		self.assertEqual(response.status_code, 200)
		response_decoded_json = json.loads(response.content.decode('utf-8'))
		response_main_obj = response_decoded_json['all_sensors_data']
		self.assertEqual(response_main_obj[0]['sensor_name'], model_a.sensor_name)
		self.assertEqual(response_main_obj[0]['last_current'], g.current)
		self.assertEqual(response_main_obj[0]['last_frequency'], g.frequency)
		self.assertEqual(response_main_obj[0]['timestamp'][:19]+"Z", g.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
		self.assertEqual(response_main_obj[0]['measurement_recent'], False)
	def test_old_measurement_is_reported_as_not_recent(self):
		model_a = SensorModel.objects.create(identifier_key = "a" * 64, sensor_name = "f00f")
		f = CurrentMeasurementModel.objects.create(specific_sensor = model_a, 
			current=100,
			frequency=2800,
			timestamp=timezone.now()-datetime.timedelta(minutes=40))
		g = CurrentMeasurementModel.objects.create(specific_sensor = model_a, 
			current=200,
			frequency=200,
			timestamp=timezone.now()-datetime.timedelta(minutes=35))
		response = self.client.get(reverse('ac_measurements:last_data'))
		self.assertEqual(response.status_code, 200)
		response_decoded_json = json.loads(response.content.decode('utf-8'))
		response_main_obj = response_decoded_json['all_sensors_data']
		self.assertEqual(response_main_obj[0]['sensor_name'], model_a.sensor_name)
		self.assertEqual(response_main_obj[0]['last_current'], g.current)
		self.assertEqual(response_main_obj[0]['last_frequency'], g.frequency)
		self.assertEqual(response_main_obj[0]['timestamp'][:19]+"Z", g.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
		self.assertEqual(response_main_obj[0]['measurement_recent'], False)
	def test_new_measurement_is_reported_as_recent(self):
		model_a = SensorModel.objects.create(identifier_key = "a" * 64, sensor_name = "f00f")
		f = CurrentMeasurementModel.objects.create(specific_sensor = model_a, 
			current=100,
			frequency=2800,
			timestamp=timezone.now()-datetime.timedelta(minutes=35))
		g = CurrentMeasurementModel.objects.create(specific_sensor = model_a, 
			current=10,
			frequency=280,
			timestamp=timezone.now()-datetime.timedelta(minutes=4))
		response = self.client.get(reverse('ac_measurements:last_data'))
		self.assertEqual(response.status_code, 200)
		response_decoded_json = json.loads(response.content.decode('utf-8'))
		response_main_obj = response_decoded_json['all_sensors_data']
		self.assertEqual(response_main_obj[0]['sensor_name'], model_a.sensor_name)
		self.assertEqual(response_main_obj[0]['last_current'], g.current)
		self.assertEqual(response_main_obj[0]['last_frequency'], g.frequency)
		self.assertEqual(response_main_obj[0]['timestamp'][:19]+"Z", g.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
		self.assertEqual(response_main_obj[0]['measurement_recent'], True)
	def test_more_than_one_sensor(self):
		model_a = SensorModel.objects.create(identifier_key = "a" * 64, sensor_name = "f00f")
		model_b = SensorModel.objects.create(identifier_key = "b" * 64, sensor_name = "f00f")
		c = CurrentMeasurementModel.objects.create(specific_sensor = model_a, 
			current=10,
			frequency=200,
			timestamp=timezone.now()-datetime.timedelta(minutes=10))
		d = CurrentMeasurementModel.objects.create(specific_sensor = model_b, 
			current=100,
			frequency=2800,
			timestamp=timezone.now()-datetime.timedelta(minutes=1))
		response = self.client.get(reverse('ac_measurements:last_data'))
		self.assertEqual(response.status_code, 200)
		response_decoded_json = json.loads(response.content.decode('utf-8'))
		response_main_obj = response_decoded_json['all_sensors_data']
		self.assertEqual(response_main_obj[0]['sensor_name'], model_a.sensor_name)
		self.assertEqual(response_main_obj[0]['last_current'], c.current)
		self.assertEqual(response_main_obj[0]['last_frequency'], c.frequency)
		self.assertEqual(response_main_obj[0]['timestamp'][:19]+"Z", c.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
		self.assertEqual(response_main_obj[0]['measurement_recent'], False)
		self.assertEqual(response_main_obj[1]['sensor_name'], model_b.sensor_name)
		self.assertEqual(response_main_obj[1]['last_current'], d.current)
		self.assertEqual(response_main_obj[1]['last_frequency'], d.frequency)
		self.assertEqual(response_main_obj[1]['timestamp'][:19]+"Z", d.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
		self.assertEqual(response_main_obj[1]['measurement_recent'], True)