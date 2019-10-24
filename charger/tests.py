from django.test import TestCase
from django.core.exceptions import ValidationError
from django.urls import reverse
from .models import ChargerModel, ChargeSession, IndividualMeasurementModel
import json
import datetime
from django.utils import timezone
# Create your tests here.
def generate_test_recv_object(charger_id="a"*64, charge_session="a"*64, current=6, voltage=2774, emergency=0, milliamps_second=50):
	return {'charger-id': charger_id,
		'charge-session': charge_session,
		'current': current,
		'voltage': voltage,
		'emergency': emergency,
		'milliamps-second': milliamps_second
		}
class APITests(TestCase):
	def test_GETting_instant_measurement(self):
		a = ChargerModel(identifier_key = "a" * 64)
		a.save()
		response = self.client.get(
			reverse('charger:new_measurement'),
			generate_test_recv_object(),
			content_type="application/json"
			)
		self.assertEqual(response.status_code, 403)
		self.assertEqual(IndividualMeasurementModel.objects.count(), 0)
	def test_POSTing_instant_measurement(self):
		a = ChargerModel(identifier_key = "a" * 64)
		a.save()
		self.assertEqual(IndividualMeasurementModel.objects.count(), 0)
		response = self.client.post(
			reverse('charger:new_measurement'),
			generate_test_recv_object(),
			content_type="application/json"
			)
		self.assertEqual(response.status_code, 201)
		self.assertEqual(IndividualMeasurementModel.objects.count(), 1)
	def test_POSTing_instant_measurement_wrong_charger(self):
		a = ChargerModel(identifier_key = "a" * 64)
		a.save()
		response = self.client.post(
			reverse('charger:new_measurement'),
			generate_test_recv_object(charger_id = "b" * 64),
			content_type="application/json"
			)
		self.assertEqual(response.status_code, 403)
		self.assertEqual(IndividualMeasurementModel.objects.count(), 0)
	def test_measurement_objects_saved(self):
		a = ChargerModel(identifier_key = "a" * 64)
		a.save()
		b = ChargerModel(identifier_key = "b" * 64)
		b.save()
		response = self.client.post(
			reverse('charger:new_measurement'),
			generate_test_recv_object(charger_id="a"*64, charge_session="a"*64, current=6261, voltage=27374, emergency=1, milliamps_second=9999),
			content_type="application/json"
			)
		self.assertEqual(response.status_code, 201)
		self.assertEqual(IndividualMeasurementModel.objects.count(), 1)
	def test_measurement_currents_sum(self):
		a = ChargerModel(identifier_key = "a" * 64)
		a.save()
		self.assertEqual(IndividualMeasurementModel.objects.count(), 0)
		charge_session_name = "a"*16 + "b" * 16 + "q" * 24 + "z" * 8
		charge_session_name_2 = "b"*16 + "b" * 16 + "q" * 24 + "z" * 8
		currents = [100, 3995, 10201]
		response = self.client.post(
			reverse('charger:new_measurement'),
			generate_test_recv_object(charge_session=charge_session_name, milliamps_second=currents[0]),
			content_type="application/json"
			)
		self.assertEqual(response.status_code, 201)
		self.assertEqual(IndividualMeasurementModel.objects.count(), 1)
		self.assertEqual(ChargeSession.objects.get(identifier_key=charge_session_name).mas_sum, currents[0])
		response = self.client.post(
			reverse('charger:new_measurement'),
			generate_test_recv_object(charge_session=charge_session_name, milliamps_second=currents[1]),
			content_type="application/json"
			)
		self.assertEqual(response.status_code, 201)
		self.assertEqual(IndividualMeasurementModel.objects.count(), 2)
		self.assertEqual(ChargeSession.objects.get(identifier_key=charge_session_name).mas_sum, currents[0] + currents[1])
		response = self.client.post(
			reverse('charger:new_measurement'),
			generate_test_recv_object(charge_session=charge_session_name_2, milliamps_second=currents[2]),
			content_type="application/json"
			)
		self.assertEqual(response.status_code, 201)
		self.assertEqual(IndividualMeasurementModel.objects.count(), 3)
		self.assertEqual(ChargeSession.objects.get(identifier_key=charge_session_name).individualmeasurementmodel_set.count(), 2)
		self.assertEqual(ChargeSession.objects.get(identifier_key=charge_session_name_2).individualmeasurementmodel_set.count(), 1)
		self.assertEqual(ChargeSession.objects.get(identifier_key=charge_session_name).mas_sum, currents[0] + currents[1])
		self.assertEqual(ChargeSession.objects.get(identifier_key=charge_session_name_2).mas_sum, currents[2])
class ModelTests(TestCase):

	def test_charger_model_uniqueness(self):
		a = ChargerModel(identifier_key = "a" * 64)
		a.full_clean()
		a.save()
		with self.assertRaises(ValidationError):
			b = ChargerModel(identifier_key = "a" * 64)
			b.full_clean()
			b.save()

	def test_charge_session_uniqueness(self):
		a = ChargerModel(identifier_key = "a" * 64)
		a.full_clean()
		a.save()
		with self.assertRaises(ValidationError):
			b = ChargeSession(specific_charger = a, identifier_key = "a" * 64)
			b.full_clean()
			b.save()
			c = ChargeSession(specific_charger = a, identifier_key = "a" * 64)
			c.full_clean()
			c.save()

	def test_indiv_meas_model_foreign_key(self):
		a = ChargerModel(identifier_key = "a" * 64)
		a.full_clean()
		a.save()
		b = ChargeSession(specific_charger = a, identifier_key = "a" * 64)
		b.full_clean()
		b.save()
		c = IndividualMeasurementModel(specific_session=b)
		c.full_clean()
		c.save()
		d = IndividualMeasurementModel(specific_session=b)
		d.full_clean()
		d.save()
		self.assertIn(c, list(b.individualmeasurementmodel_set.all()))
		self.assertIn(d, list(b.individualmeasurementmodel_set.all()))

class IndexViewTests(TestCase):
	def test_index_view_correct_template(self):
		response = self.client.get(reverse('charger:main_index'))
		self.assertTemplateUsed(response, 'charger/index.html')

class ReactViewTests(TestCase):
	def test_react_view_correct_template(self):
		response = self.client.get(reverse('charger:main_react'))
		self.assertTemplateUsed(response, 'charger/index-react.html')

class LastDataAPITests(TestCase):
	def test_only_get_is_allowed(self):
		response = self.client.post(reverse('charger:last_data'),
			{'blah': 1},
			content_type="application/json"
			)
		self.assertEqual(response.status_code, 403)
	def test_get_latest_session_data_when_there_are_no_sessions(self):
		model_a = ChargerModel.objects.create(identifier_key = "a" * 64)
		response = self.client.get(reverse('charger:last_data'))
		self.assertEqual(response.status_code, 500)

	def test_get_latest_session_data_expected_ok(self):
		model_a = ChargerModel.objects.create(identifier_key = "a" * 64, charger_name = "f00f")
		model_b = ChargerModel.objects.create(identifier_key = "b" * 64, charger_name = "l0l")
		c = ChargeSession.objects.create(specific_charger = model_a, identifier_key = "b" * 64, mas_sum=100)
		d = ChargeSession.objects.create(specific_charger = model_b, identifier_key = "c" * 64, mas_sum=20)
		e = ChargeSession.objects.create(specific_charger = model_b, identifier_key = "d" * 64, mas_sum=10)
		f = IndividualMeasurementModel.objects.create(specific_session = c, 
			instantaneous_current=100,
			instantaneous_voltage=2800,
			emergency_status=1)
		g = IndividualMeasurementModel.objects.create(specific_session = d, 
			instantaneous_current=20,
			instantaneous_voltage=200,
			emergency_status=0)
		h = IndividualMeasurementModel.objects.create(specific_session = e, 
			instantaneous_current=10,
			instantaneous_voltage=1,
			emergency_status=3,
			timestamp=timezone.now()-datetime.timedelta(days=2))
		i = IndividualMeasurementModel.objects.create(specific_session = e, 
			instantaneous_current=9999,
			instantaneous_voltage=9888,
			emergency_status=4)
		response = self.client.get(reverse('charger:last_data'))
		self.assertEqual(response.status_code, 200)
		response_decoded_json = json.loads(response.content.decode('utf-8'))
		response_main_obj = response_decoded_json['all_chargers_data']
		self.assertEqual(response_main_obj[0]['charger_name'], model_a.charger_name)
		self.assertEqual(response_main_obj[0]['last_session_id'], c.identifier_key)
		self.assertEqual(response_main_obj[0]['last_session_mas'], c.mas_sum)
		self.assertEqual(response_main_obj[0]['last_session_begin'][:19]+"Z", f.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
		self.assertEqual(response_main_obj[0]['last_measurement']['voltage'], f.instantaneous_voltage)
		self.assertEqual(response_main_obj[0]['last_measurement']['current'], f.instantaneous_current)
		self.assertEqual(response_main_obj[0]['last_measurement']['emergency'], f.emergency_status)
		self.assertEqual(response_main_obj[0]['last_measurement']['mas'], f.milliampere_second)
		self.assertEqual(response_main_obj[0]['last_measurement']['timestamp'][:19]+"Z", f.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
		self.assertEqual(response_main_obj[1]['charger_name'], model_b.charger_name)
		self.assertEqual(response_main_obj[1]['last_session_id'], e.identifier_key)
		self.assertEqual(response_main_obj[1]['last_session_mas'], e.mas_sum)
		self.assertEqual(response_main_obj[1]['last_session_begin'][:19]+"Z", h.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
		self.assertEqual(response_main_obj[1]['last_measurement']['voltage'], i.instantaneous_voltage)
		self.assertEqual(response_main_obj[1]['last_measurement']['current'], i.instantaneous_current)
		self.assertEqual(response_main_obj[1]['last_measurement']['emergency'], i.emergency_status)
		self.assertEqual(response_main_obj[1]['last_measurement']['mas'], i.milliampere_second)
		self.assertEqual(response_main_obj[1]['last_measurement']['timestamp'][:19]+"Z", i.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
		#print(response_decoded_json)

	def test_get_current_outage_cause(self):
		model_a = ChargerModel.objects.create(identifier_key = "a" * 64, charger_name = "f00f")
		c = ChargeSession.objects.create(specific_charger = model_a, identifier_key = "b" * 64, mas_sum=100)
		d = ChargeSession.objects.create(specific_charger = model_a, identifier_key = "c" * 64, mas_sum=20)
		e = ChargeSession.objects.create(specific_charger = model_a, identifier_key = "d" * 64, mas_sum=10)
		f = IndividualMeasurementModel.objects.create(specific_session = c, 
			instantaneous_current=100,
			instantaneous_voltage=2800,
			emergency_status=1)
		g = IndividualMeasurementModel.objects.create(specific_session = d, 
			instantaneous_current=20,
			instantaneous_voltage=200,
			emergency_status=0)
		h = IndividualMeasurementModel.objects.create(specific_session = e, 
			instantaneous_current=10,
			instantaneous_voltage=1,
			emergency_status=0,
			timestamp=timezone.now()-datetime.timedelta(days=3))
		i = IndividualMeasurementModel.objects.create(specific_session = e, 
			instantaneous_current=9999,
			instantaneous_voltage=9888,
			emergency_status=0,
			timestamp=timezone.now()-datetime.timedelta(days=2))
		j = IndividualMeasurementModel.objects.create(specific_session = e, 
			instantaneous_current=8888,
			instantaneous_voltage=7777,
			emergency_status=1,
			timestamp=timezone.now()-datetime.timedelta(days=1))
		k = IndividualMeasurementModel.objects.create(specific_session = e, 
			instantaneous_current=2222,
			instantaneous_voltage=2222,
			emergency_status=2)
		response = self.client.get(reverse('charger:last_data'))
		self.assertEqual(response.status_code, 200)
		response_decoded_json = json.loads(response.content.decode('utf-8'))
		response_main_obj = response_decoded_json['all_chargers_data']
		self.assertEqual(response_main_obj[0]['charger_name'], model_a.charger_name)
		self.assertEqual(response_main_obj[0]['current_outage']['valid'], True)
		self.assertEqual(response_main_obj[0]['current_outage']['emergency'], j.emergency_status)
		self.assertEqual(response_main_obj[0]['current_outage']['timestamp'][:19]+"Z", j.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))

	def test_get_current_outage_false_condition(self):
		model_a = ChargerModel.objects.create(identifier_key = "a" * 64, charger_name = "f00f")
		c = ChargeSession.objects.create(specific_charger = model_a, identifier_key = "b" * 64, mas_sum=100)
		d = ChargeSession.objects.create(specific_charger = model_a, identifier_key = "c" * 64, mas_sum=20)
		e = ChargeSession.objects.create(specific_charger = model_a, identifier_key = "d" * 64, mas_sum=10)
		f = IndividualMeasurementModel.objects.create(specific_session = c, 
			instantaneous_current=100,
			instantaneous_voltage=2800,
			emergency_status=1)
		g = IndividualMeasurementModel.objects.create(specific_session = d, 
			instantaneous_current=20,
			instantaneous_voltage=200,
			emergency_status=1)
		h = IndividualMeasurementModel.objects.create(specific_session = e, 
			instantaneous_current=10,
			instantaneous_voltage=1,
			emergency_status=0,
			timestamp=timezone.now()-datetime.timedelta(days=3))
		i = IndividualMeasurementModel.objects.create(specific_session = e, 
			instantaneous_current=9999,
			instantaneous_voltage=9888,
			emergency_status=0,
			timestamp=timezone.now()-datetime.timedelta(days=2))
		j = IndividualMeasurementModel.objects.create(specific_session = e, 
			instantaneous_current=8888,
			instantaneous_voltage=7777,
			emergency_status=0,
			timestamp=timezone.now()-datetime.timedelta(days=1))
		k = IndividualMeasurementModel.objects.create(specific_session = e, 
			instantaneous_current=2222,
			instantaneous_voltage=2222,
			emergency_status=0)
		response = self.client.get(reverse('charger:last_data'))
		self.assertEqual(response.status_code, 200)
		response_decoded_json = json.loads(response.content.decode('utf-8'))
		response_main_obj = response_decoded_json['all_chargers_data']
		self.assertEqual(response_main_obj[0]['charger_name'], model_a.charger_name)
		self.assertEqual(response_main_obj[0]['current_outage']['valid'], False)
		self.assertEqual(response_main_obj[0]['current_outage']['emergency'], False)
		self.assertEqual(response_main_obj[0]['current_outage']['timestamp'], False)
		self.assertEqual(response_main_obj[0]['previous_outage']['valid'], True)

	def test_get_previous_outage_cause(self):
		model_a = ChargerModel.objects.create(identifier_key = "a" * 64, charger_name = "f00f")
		c = ChargeSession.objects.create(specific_charger = model_a, identifier_key = "b" * 64, mas_sum=100)
		d = ChargeSession.objects.create(specific_charger = model_a, identifier_key = "c" * 64, mas_sum=20)
		e = ChargeSession.objects.create(specific_charger = model_a, identifier_key = "d" * 64, mas_sum=10)
		f = IndividualMeasurementModel.objects.create(specific_session = c, 
			instantaneous_current=100,
			instantaneous_voltage=2800,
			emergency_status=1,
			timestamp=timezone.now()-datetime.timedelta(days=5))
		g = IndividualMeasurementModel.objects.create(specific_session = d, 
			instantaneous_current=20,
			instantaneous_voltage=200,
			emergency_status=0,
			timestamp=timezone.now()-datetime.timedelta(days=4))
		h = IndividualMeasurementModel.objects.create(specific_session = e, 
			instantaneous_current=10,
			instantaneous_voltage=1,
			emergency_status=0,
			timestamp=timezone.now()-datetime.timedelta(days=3))
		i = IndividualMeasurementModel.objects.create(specific_session = e, 
			instantaneous_current=9999,
			instantaneous_voltage=9888,
			emergency_status=0,
			timestamp=timezone.now()-datetime.timedelta(days=2))
		j = IndividualMeasurementModel.objects.create(specific_session = e, 
			instantaneous_current=8888,
			instantaneous_voltage=7777,
			emergency_status=0,
			timestamp=timezone.now()-datetime.timedelta(days=1))
		k = IndividualMeasurementModel.objects.create(specific_session = e, 
			instantaneous_current=2222,
			instantaneous_voltage=2222,
			emergency_status=0)
		response = self.client.get(reverse('charger:last_data'))
		self.assertEqual(response.status_code, 200)
		response_decoded_json = json.loads(response.content.decode('utf-8'))
		response_main_obj = response_decoded_json['all_chargers_data']
		self.assertEqual(response_main_obj[0]['charger_name'], model_a.charger_name)
		self.assertEqual(response_main_obj[0]['current_outage']['valid'], False)
		self.assertEqual(response_main_obj[0]['previous_outage']['valid'], True)
		self.assertEqual(response_main_obj[0]['previous_outage']['emergency'], f.emergency_status)
		self.assertEqual(response_main_obj[0]['previous_outage']['timestamp_start'][:19]+"Z", f.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
		self.assertEqual(response_main_obj[0]['previous_outage']['timestamp_end'][:19]+"Z", g.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))

	def test_get_previous_outage_cause_without_end(self):
		model_a = ChargerModel.objects.create(identifier_key = "a" * 64, charger_name = "f00f")
		c = ChargeSession.objects.create(specific_charger = model_a, identifier_key = "b" * 64, mas_sum=100)
		d = ChargeSession.objects.create(specific_charger = model_a, identifier_key = "c" * 64, mas_sum=20)
		e = ChargeSession.objects.create(specific_charger = model_a, identifier_key = "d" * 64, mas_sum=10)
		f = IndividualMeasurementModel.objects.create(specific_session = c, 
			instantaneous_current=100,
			instantaneous_voltage=2800,
			emergency_status=0,
			timestamp=timezone.now()-datetime.timedelta(days=5))
		g = IndividualMeasurementModel.objects.create(specific_session = d, 
			instantaneous_current=20,
			instantaneous_voltage=200,
			emergency_status=2,
			timestamp=timezone.now()-datetime.timedelta(days=4))
		h = IndividualMeasurementModel.objects.create(specific_session = e, 
			instantaneous_current=10,
			instantaneous_voltage=1,
			emergency_status=1,
			timestamp=timezone.now()-datetime.timedelta(days=3))
		i = IndividualMeasurementModel.objects.create(specific_session = e, 
			instantaneous_current=9999,
			instantaneous_voltage=9888,
			emergency_status=1,
			timestamp=timezone.now()-datetime.timedelta(days=2))
		j = IndividualMeasurementModel.objects.create(specific_session = e, 
			instantaneous_current=8888,
			instantaneous_voltage=7777,
			emergency_status=1,
			timestamp=timezone.now()-datetime.timedelta(days=1))
		k = IndividualMeasurementModel.objects.create(specific_session = e, 
			instantaneous_current=2222,
			instantaneous_voltage=2222,
			emergency_status=1)
		response = self.client.get(reverse('charger:last_data'))
		self.assertEqual(response.status_code, 200)
		response_decoded_json = json.loads(response.content.decode('utf-8'))
		response_main_obj = response_decoded_json['all_chargers_data']
		self.assertEqual(response_main_obj[0]['charger_name'], model_a.charger_name)
		self.assertEqual(response_main_obj[0]['current_outage']['valid'], True)
		self.assertEqual(response_main_obj[0]['previous_outage']['valid'], True)
		self.assertEqual(response_main_obj[0]['previous_outage']['emergency'], g.emergency_status)
		self.assertEqual(response_main_obj[0]['previous_outage']['timestamp_start'][:19]+"Z", g.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
		self.assertEqual(response_main_obj[0]['previous_outage']['timestamp_end'], False)

	def test_old_measurement_is_reported_as_not_recent(self):
		model_a = ChargerModel.objects.create(identifier_key = "a" * 64, charger_name = "f00f")
		c = ChargeSession.objects.create(specific_charger = model_a, identifier_key = "b" * 64, mas_sum=100)
		d = ChargeSession.objects.create(specific_charger = model_a, identifier_key = "c" * 64, mas_sum=20)
		f = IndividualMeasurementModel.objects.create(specific_session = c, 
			instantaneous_current=100,
			instantaneous_voltage=2800,
			emergency_status=0,
			timestamp=timezone.now()-datetime.timedelta(minutes=35))
		g = IndividualMeasurementModel.objects.create(specific_session = d, 
			instantaneous_current=20,
			instantaneous_voltage=200,
			emergency_status=0,
			timestamp=timezone.now()-datetime.timedelta(minutes=30))
		h = IndividualMeasurementModel.objects.create(specific_session = d, 
			instantaneous_current=10,
			instantaneous_voltage=1,
			emergency_status=0,
			timestamp=timezone.now()-datetime.timedelta(minutes=25))
		i = IndividualMeasurementModel.objects.create(specific_session = d, 
			instantaneous_current=9999,
			instantaneous_voltage=9888,
			emergency_status=0,
			timestamp=timezone.now()-datetime.timedelta(minutes=20))
		response = self.client.get(reverse('charger:last_data'))
		self.assertEqual(response.status_code, 200)
		response_decoded_json = json.loads(response.content.decode('utf-8'))
		response_main_obj = response_decoded_json['all_chargers_data']
		self.assertEqual(response_main_obj[0]['charger_name'], model_a.charger_name)
		self.assertEqual(response_main_obj[0]['last_session_id'], d.identifier_key)
		self.assertEqual(response_main_obj[0]['measurement_recent'], False)

	def test_new_measurement_is_reported_as_recent(self):
		model_a = ChargerModel.objects.create(identifier_key = "a" * 64, charger_name = "f00f")
		c = ChargeSession.objects.create(specific_charger = model_a, identifier_key = "b" * 64, mas_sum=100)
		d = ChargeSession.objects.create(specific_charger = model_a, identifier_key = "c" * 64, mas_sum=20)
		f = IndividualMeasurementModel.objects.create(specific_session = c, 
			instantaneous_current=100,
			instantaneous_voltage=2800,
			emergency_status=0,
			timestamp=timezone.now()-datetime.timedelta(minutes=35))
		g = IndividualMeasurementModel.objects.create(specific_session = d, 
			instantaneous_current=20,
			instantaneous_voltage=200,
			emergency_status=0,
			timestamp=timezone.now()-datetime.timedelta(minutes=30))
		h = IndividualMeasurementModel.objects.create(specific_session = d, 
			instantaneous_current=10,
			instantaneous_voltage=1,
			emergency_status=0,
			timestamp=timezone.now()-datetime.timedelta(minutes=25))
		i = IndividualMeasurementModel.objects.create(specific_session = d, 
			instantaneous_current=9999,
			instantaneous_voltage=9888,
			emergency_status=0,
			timestamp=timezone.now()-datetime.timedelta(minutes=2))
		response = self.client.get(reverse('charger:last_data'))
		self.assertEqual(response.status_code, 200)
		response_decoded_json = json.loads(response.content.decode('utf-8'))
		response_main_obj = response_decoded_json['all_chargers_data']
		self.assertEqual(response_main_obj[0]['charger_name'], model_a.charger_name)
		self.assertEqual(response_main_obj[0]['last_session_id'], d.identifier_key)
		self.assertEqual(response_main_obj[0]['measurement_recent'], True)

class HistoricalDataAPITests(TestCase):
	def test_only_get_is_allowed(self):
		response = self.client.post(reverse('charger:historical_data'),
			{'blah': 1},
			content_type="application/json"
			)
		self.assertEqual(response.status_code, 403)
	def test_get_data_when_there_are_no_sessions(self):
		model_a = ChargerModel.objects.create(identifier_key = "a" * 64)
		response = self.client.get(reverse('charger:historical_data'))
		self.assertEqual(response.status_code, 200)

	def test_without_emergency_in_session(self):
		model_a = ChargerModel.objects.create(identifier_key = "a" * 64, charger_name = "f00f")
		c = ChargeSession.objects.create(specific_charger = model_a, identifier_key = "b" * 64, mas_sum=100)
		f1 = IndividualMeasurementModel.objects.create(specific_session = c, 
			instantaneous_current=800,
			instantaneous_voltage=2800,
			emergency_status=0,
			timestamp=timezone.now()-datetime.timedelta(days=10))
		f2 = IndividualMeasurementModel.objects.create(specific_session = c, 
			instantaneous_current=700,
			instantaneous_voltage=2700,
			emergency_status=0,
			timestamp=timezone.now()-datetime.timedelta(days=9))
		response = self.client.get(reverse('charger:historical_data'))
		self.assertEqual(response.status_code, 200)
		response_decoded_json = json.loads(response.content.decode('utf-8'))
		response_main_obj = response_decoded_json['historical_data']
		self.assertEqual(response_main_obj[0]['charger_name'], model_a.charger_name)
		self.assertEqual(response_main_obj[0]['session_list'][0]['session_name'], c.identifier_key)
		self.assertEqual(response_main_obj[0]['session_list'][0]['emergency_valid'], False)

	def test_with_emergency_in_session(self):
		model_a = ChargerModel.objects.create(identifier_key = "a" * 64, charger_name = "f00f")
		c = ChargeSession.objects.create(specific_charger = model_a, identifier_key = "b" * 64, mas_sum=100)
		f1 = IndividualMeasurementModel.objects.create(specific_session = c, 
			instantaneous_current=800,
			instantaneous_voltage=2800,
			emergency_status=0,
			timestamp=timezone.now()-datetime.timedelta(days=10))
		f2 = IndividualMeasurementModel.objects.create(specific_session = c, 
			instantaneous_current=700,
			instantaneous_voltage=2700,
			emergency_status=1,
			timestamp=timezone.now()-datetime.timedelta(days=9))
		response = self.client.get(reverse('charger:historical_data'))
		self.assertEqual(response.status_code, 200)
		response_decoded_json = json.loads(response.content.decode('utf-8'))
		response_main_obj = response_decoded_json['historical_data']
		self.assertEqual(response_main_obj[0]['charger_name'], model_a.charger_name)
		self.assertEqual(response_main_obj[0]['session_list'][0]['session_name'], c.identifier_key)
		self.assertEqual(response_main_obj[0]['session_list'][0]['emergency_valid'], True)
		self.assertEqual(response_main_obj[0]['session_list'][0]['emergency_date'][:19]+"Z", f2.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))

	def test_get_historical_data_two_chargers(self):
		model_a = ChargerModel.objects.create(identifier_key = "a" * 64, charger_name = "f00f")
		model_b = ChargerModel.objects.create(identifier_key = "b" * 64, charger_name = "l0l")
		c = ChargeSession.objects.create(specific_charger = model_a, identifier_key = "b" * 64, mas_sum=100)
		d = ChargeSession.objects.create(specific_charger = model_b, identifier_key = "c" * 64, mas_sum=20)
		e = ChargeSession.objects.create(specific_charger = model_b, identifier_key = "d" * 64, mas_sum=10)
		f1 = IndividualMeasurementModel.objects.create(specific_session = c, 
			instantaneous_current=800,
			instantaneous_voltage=2800,
			emergency_status=0,
			timestamp=timezone.now()-datetime.timedelta(days=10))
		f2 = IndividualMeasurementModel.objects.create(specific_session = c, 
			instantaneous_current=700,
			instantaneous_voltage=2700,
			emergency_status=1,
			timestamp=timezone.now()-datetime.timedelta(days=9))
		f3 = IndividualMeasurementModel.objects.create(specific_session = c, 
			instantaneous_current=600,
			instantaneous_voltage=2600,
			emergency_status=1,
			timestamp=timezone.now()-datetime.timedelta(days=8))
		g1 = IndividualMeasurementModel.objects.create(specific_session = d, 
			instantaneous_current=500,
			instantaneous_voltage=2500,
			emergency_status=0,
			timestamp=timezone.now()-datetime.timedelta(days=7))
		g2 = IndividualMeasurementModel.objects.create(specific_session = d, 
			instantaneous_current=400,
			instantaneous_voltage=2400,
			emergency_status=0,
			timestamp=timezone.now()-datetime.timedelta(days=6))
		g3 = IndividualMeasurementModel.objects.create(specific_session = d, 
			instantaneous_current=300,
			instantaneous_voltage=2300,
			emergency_status=0,
			timestamp=timezone.now()-datetime.timedelta(days=5))
		h1 = IndividualMeasurementModel.objects.create(specific_session = e, 
			instantaneous_current=200,
			instantaneous_voltage=2200,
			emergency_status=0,
			timestamp=timezone.now()-datetime.timedelta(days=4))
		h2 = IndividualMeasurementModel.objects.create(specific_session = e, 
			instantaneous_current=100,
			instantaneous_voltage=2100,
			emergency_status=0,
			timestamp=timezone.now()-datetime.timedelta(days=3))
		h3 = IndividualMeasurementModel.objects.create(specific_session = e, 
			instantaneous_current=50,
			instantaneous_voltage=2000,
			emergency_status=0,
			timestamp=timezone.now()-datetime.timedelta(days=2))
		response = self.client.get(reverse('charger:historical_data'))
		self.assertEqual(response.status_code, 200)
		response_decoded_json = json.loads(response.content.decode('utf-8'))
		response_main_obj = response_decoded_json['historical_data']
		self.assertEqual(response_main_obj[1]['charger_name'], model_b.charger_name)
		self.assertEqual(response_main_obj[1]['session_list'][0]['session_name'], e.identifier_key)
		self.assertEqual(response_main_obj[1]['session_list'][0]['emergency_valid'], False)
		self.assertEqual(response_main_obj[1]['session_list'][0]['mas_sum'], e.mas_sum)
		self.assertEqual(response_main_obj[1]['session_list'][0]['start_date'][:19]+"Z", h1.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
		self.assertEqual(response_main_obj[1]['session_list'][0]['end_date'][:19]+"Z", h3.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))

		self.assertEqual(response_main_obj[1]['charger_name'], model_b.charger_name)
		self.assertEqual(response_main_obj[1]['session_list'][1]['session_name'], d.identifier_key)

		self.assertEqual(response_main_obj[0]['charger_name'], model_a.charger_name)
		self.assertEqual(response_main_obj[0]['session_list'][0]['session_name'], c.identifier_key)
		self.assertEqual(response_main_obj[0]['session_list'][0]['emergency_valid'], True)
		self.assertEqual(response_main_obj[0]['session_list'][0]['mas_sum'], c.mas_sum)
		self.assertEqual(response_main_obj[0]['session_list'][0]['start_date'][:19]+"Z", f1.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
		self.assertEqual(response_main_obj[0]['session_list'][0]['end_date'][:19]+"Z", f3.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
		self.assertEqual(response_main_obj[0]['session_list'][0]['emergency_date'][:19]+"Z", f2.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))