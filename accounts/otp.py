import math, random


# function to generate OTP
def generateOTP():
    """
    Generates 4 digit random otp
    """
    digits = "0123456789"
    OTP = ""

    # length of password can be changed
    # by changing value in range
    for i in range(4):
        OTP += digits[math.floor(random.random() * 10)]

    return OTP
