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