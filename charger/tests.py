from django.test import TestCase
from django.core.exceptions import ValidationError
from django.urls import reverse
from .models import ChargerModel, ChargeSession, IndividualMeasurementModel
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