from .models import Driver, Vehicle, Paper, DriverData, UserData, Trip, Child, Stops, Rating,FevoriteDriverModel
from .LocationIsValid import checkLocation
from .distance import distanceCalculator



def getVehicle(driver):
  vehicle = Vehicle.objects.filter(owner=driver).first()
  return vehicle