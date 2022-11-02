from rest_framework.test import APITestCase
from accounts.otp import generateOTP

class OTPTest(APITestCase):
    
    def test_generate_otp(self):
      otp = len(generateOTP())
      self.assertEqual(otp, 4)
      
      