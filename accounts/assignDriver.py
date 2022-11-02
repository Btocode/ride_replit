from .models import Driver, Vehicle, Paper, DriverData, UserData, Trip, Child, Stops, Rating,FevoriteDriverModel

from .LocationIsValid import checkLocation
from .distance import distanceCalculator
from rest_framework.response import Response
from rest_framework import status
from .assignVehicle import getVehicle



def getDriver(drivers, pickup_location1, child_seat, required_vehicle_type):
    filtered_drivers = []
    for driver in drivers:
        vehicle = getVehicle(driver)

        if vehicle.vehicle_type == required_vehicle_type:
            if vehicle.has_child_seat == child_seat:
                filtered_drivers.append(driver)
        else:
            pass
    if filtered_drivers and pickup_location1:
        distance = []
        for driver in filtered_drivers:

            driver_location = driver.driver_location
            if checkLocation(pickup_location1) and checkLocation(driver_location):
                pickup_location = pickup_location1.split(",")

                driver_location = driver_location.split(",")
                lat1 = float(pickup_location[0])
                lat2 = float(driver_location[0])
                lon1 = float(pickup_location[1])
                lon2 = float(driver_location[1])
                calculated_distance = distanceCalculator(lat1, lat2, lon1, lon2)
                dic = {
                    "distance_from_location": calculated_distance,
                    "driver_id": str(driver.id),
                }
                distance.append(dic)
            else:
                continue

        # distance.sort()
        sortedDict = sorted(distance, key=lambda d: d['distance_from_location'])

        try:
            driver_instance = Driver.objects.get(id=sortedDict[0]['driver_id'].strip())
            return driver_instance, sortedDict[0]['distance_from_location']

        except Exception as e:
            return Response({'message': 'No driver available right now'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return "Driver Not Found"
  