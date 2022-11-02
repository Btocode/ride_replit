from rest_framework.test import APITestCase
from accounts import distance

class DistanceTest(APITestCase):
      
      def test_distance(self):
        calculated_distance = distance.distanceCalculator(23.145601, 89.208946, 23.155245, 89.205016)
        self.assertEqual(calculated_distance, 7398.381034801681)