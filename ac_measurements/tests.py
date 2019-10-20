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
	# def test_POSTing_instant_measurement_wrong_charger(self):
	# 	a = ChargerModel(identifier_key = "a" * 64)
	# 	a.save()
	# 	response = self.client.post(
	# 		reverse('charger:new_measurement'),
	# 		generate_test_recv_object(charger_id = "b" * 64),
	# 		content_type="application/json"
	# 		)
	# 	self.assertEqual(response.status_code, 403)
	# 	self.assertEqual(IndividualMeasurementModel.objects.count(), 0)
	# def test_measurement_objects_saved(self):
	# 	a = ChargerModel(identifier_key = "a" * 64)
	# 	a.save()
	# 	b = ChargerModel(identifier_key = "b" * 64)
	# 	b.save()
	# 	response = self.client.post(
	# 		reverse('charger:new_measurement'),
	# 		generate_test_recv_object(charger_id="a"*64, charge_session="a"*64, current=6261, voltage=27374, emergency=1, milliamps_second=9999),
	# 		content_type="application/json"
	# 		)
	# 	self.assertEqual(response.status_code, 201)
	# 	self.assertEqual(IndividualMeasurementModel.objects.count(), 1)
	# def test_measurement_currents_sum(self):
	# 	a = ChargerModel(identifier_key = "a" * 64)
	# 	a.save()
	# 	self.assertEqual(IndividualMeasurementModel.objects.count(), 0)
	# 	charge_session_name = "a"*16 + "b" * 16 + "q" * 24 + "z" * 8
	# 	charge_session_name_2 = "b"*16 + "b" * 16 + "q" * 24 + "z" * 8
	# 	currents = [100, 3995, 10201]
	# 	response = self.client.post(
	# 		reverse('charger:new_measurement'),
	# 		generate_test_recv_object(charge_session=charge_session_name, milliamps_second=currents[0]),
	# 		content_type="application/json"
	# 		)
	# 	self.assertEqual(response.status_code, 201)
	# 	self.assertEqual(IndividualMeasurementModel.objects.count(), 1)
	# 	self.assertEqual(ChargeSession.objects.get(identifier_key=charge_session_name).mas_sum, currents[0])
	# 	response = self.client.post(
	# 		reverse('charger:new_measurement'),
	# 		generate_test_recv_object(charge_session=charge_session_name, milliamps_second=currents[1]),
	# 		content_type="application/json"
	# 		)
	# 	self.assertEqual(response.status_code, 201)
	# 	self.assertEqual(IndividualMeasurementModel.objects.count(), 2)
	# 	self.assertEqual(ChargeSession.objects.get(identifier_key=charge_session_name).mas_sum, currents[0] + currents[1])
	# 	response = self.client.post(
	# 		reverse('charger:new_measurement'),
	# 		generate_test_recv_object(charge_session=charge_session_name_2, milliamps_second=currents[2]),
	# 		content_type="application/json"
	# 		)
	# 	self.assertEqual(response.status_code, 201)
	# 	self.assertEqual(IndividualMeasurementModel.objects.count(), 3)
	# 	self.assertEqual(ChargeSession.objects.get(identifier_key=charge_session_name).individualmeasurementmodel_set.count(), 2)
	# 	self.assertEqual(ChargeSession.objects.get(identifier_key=charge_session_name_2).individualmeasurementmodel_set.count(), 1)
	# 	self.assertEqual(ChargeSession.objects.get(identifier_key=charge_session_name).mas_sum, currents[0] + currents[1])
	# 	self.assertEqual(ChargeSession.objects.get(identifier_key=charge_session_name_2).mas_sum, currents[2])
