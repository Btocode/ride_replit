from rest_framework.test import APITestCase
from accounts import LocationIsValid

class LocationIsValidTest(APITestCase):
    
    def test_locationIsValid(self):
      location_is_valid = LocationIsValid.checkLocation("23.145601, 89.208946")
      location_is_not_valid = LocationIsValid.checkLocation("23.14560sdsada")
      location_exception = LocationIsValid.checkLocation("asdasdasdasd")
      # self.assertFalse(location_exception)
      self.assertFalse(location_is_not_valid)
      self.assertTrue(location_is_valid)
      
