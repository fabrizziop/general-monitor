from django.test import TestCase
from django.core.exceptions import ValidationError
from django.urls import reverse
from .models import ChargerModel, ChargeSession, IndividualMeasurementModel
# Create your tests here.

class APITests(TestCase):
	def test_POSTing_instant_measurement(self):
		a = ChargerModel(identifier_key = "a" * 64)
		a.save()
		response = self.client.post(
			reverse('charger:new_measurement'),
			{'charger-id': "a" * 64,
			'current': 10
			},
			content_type="application/json"
			)
		self.assertEqual(response.status_code, 201)
	def test_POSTing_instant_measurement_wrong_charger(self):
		a = ChargerModel(identifier_key = "a" * 64)
		a.save()
		response = self.client.post(
			reverse('charger:new_measurement'),
			{
			'charger-id': "b" * 64,
			'current': 10
			},
			content_type="application/json"
			)
		self.assertEqual(response.status_code, 403)

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