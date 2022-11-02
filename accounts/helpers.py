import json

import requests
from django.contrib.auth import get_user_model

from .models import UserData, DriverData, Driver

User = get_user_model()


def create_user(id_of_user_data):
    """
    Creates User and Driver from temporary Model UserData and DriverData.
    """
    data = UserData.objects.get(id=id_of_user_data)

    user = User(email=data.email, first_name=data.first_name, last_name=data.last_name,
                phone=data.phone, address=data.address, password=data.password)
    user.save()

    try:
        driver_data = DriverData.objects.get(user_data=data)
        driver = Driver(driving_license_front_image=driver_data.driving_license_front_image,
                        driving_license_back_image=driver_data.driving_license_back_image,
                        national_insurance=driver_data.national_insurance,
                        is_condemned_prior=driver_data.is_condemned_prior,
                        user=user, gender=driver_data.gender)
        driver.save()
        driver_data.delete()
    except DriverData.DoesNotExist:
        pass
    data.delete()
    try:
        driver = driver
    except UnboundLocalError:
        driver = None
    out = {'user': user,
           'driver': driver}
    return out


def send_data_to_central(instance):
    """
    Sends trip data to central server
    """
    trip_information = {
        "full_name": instance.user.first_name + " " + instance.user.last_name,
        "email": instance.user.email,
        "phone": instance.user.phone,
        "address": instance.user.address,
        "web_url": "https://www.google.com",
        "vehicle_type": instance.vehicle_type,
        "number_of_people": instance.number_of_passengers,
        "luggage": instance.luggage_amount,
        "max_weight": instance.luggage_weight,
        "child_seat": instance.child_set.all().count(),
        "pickup_point": instance.pickup_location,
        "destination": instance.drop_off_location,
        "date": str(instance.date),
        'pickup_time': str(instance.pickup_time),

    }
    stops = [stop.location for stop in instance.stops_set.all()]
    data = {
        'trip_data': trip_information,
        'stops': stops
    }
    external_api_url = 'http://127.0.0.1:7000/api/v1/request-trip/'
    data_json = json.dumps(data)
    # res = requests.post(external_api_url, json=json.loads(data_json))


