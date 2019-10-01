from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import ChargerModel, IndividualMeasurementModel
# Create your tests here.

class APITests(TestCase):
	def test_POSTing_instant_measurement(self):
		response = self.client.post(
			'/new-measurement',
			{
			'current': 10
			}
			)

class ModelTests(TestCase):

	def test_charger_model_uniqueness(self):
		a = ChargerModel(identifier_key = "a" * 64)
		a.full_clean()
		a.save()
		with self.assertRaises(ValidationError):
			b = ChargerModel(identifier_key = "a" * 64)
			b.full_clean()
			b.save()

	def test_indiv_meas_model_foreign_key(self):
		a = ChargerModel(identifier_key = "a" * 64)
		a.full_clean()
		a.save()
		b = IndividualMeasurementModel(specific_charger=a)
		b.full_clean()
		b.save()
		c = IndividualMeasurementModel(specific_charger=a)
		c.full_clean()
		c.save()
		self.assertIn(b, list(a.individualmeasurementmodel_set.all()))
		self.assertIn(c, list(a.individualmeasurementmodel_set.all()))