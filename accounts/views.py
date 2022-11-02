import base64

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from rest_framework import generics, permissions, status
from rest_framework.generics import get_object_or_404, UpdateAPIView, CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from . import assignDriver, assignVehicle

from .distance import distanceCalculator
from .helpers import create_user, send_data_to_central
from .models import (Child, Driver, DriverData, Paper, Stops, Trip,
                     UserData, UserOTP, UserToken, Vehicle, Rating, FevoriteDriverModel)
from .otp import generateOTP
from .permissions import IsDriver, IsAdmin, IsVerifiedDriver, is_admin, IsNotBlacklisted
from .serializers import (ChildSerializer, DriverDataSerializer,
                          DriverSerializer, LoginSerializer, LogoutSerializer,
                          PaperSerializer, StopSerializer,
                          TripRequestSerializer, UserDataSerializer,
                          UserSerializer, VehicleDetailsSerializer,
                          VehicleSerializer, RatingSerializer, MyTokenObtainPairSerializer, FevoriteDriverSerializer, EditTripsSerializer)
from .LocationIsValid import checkLocation

User = get_user_model()


class Authenticate(APIView):
    permission_classes = (AllowAny,)


# View for token generation
# Its customized to generate token for both users and drivers
# It contains custom added data to the token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# Class based view to Get User Details using Token Authentication
class UserDetailsView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        data = User.objects.all()
        serializer = UserSerializer(data, many=True)
        return Response(serializer.data)


# APi view for user Details
class UserDetailAPI(APIView):
    # authentication_classes = (TokenAuthentication, )
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        user = User.objects.all()
        serializer = UserSerializer(user, many=True)
        return Response(serializer.data)


# API view for Driver Details
class DriverDetailAPI(APIView):
    # authentication_classes = (TokenAuthentication, )
    permission_classes = (AllowAny,)

    # vehicle = Vehicle.objects.all()

    def get(self, request, *args, **kwargs):
        user = Driver.objects.all()
        serializer = DriverSerializer(user, many=True)
        return Response(serializer.data)


# Class based view to register user
class RegisterUserAPIView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserDataSerializer


class IndividualUserDetailAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = User.objects.get(email=request.user)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    # permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        res = serializer.data
        email = serializer.data['tokens']
        return Response(res, status=status.HTTP_200_OK)


class LogOutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'message': 'User logged out successfully'
        }, status=status.HTTP_200_OK)


class CreateDriver(APIView):
    """
    Api for registering drivers.
    """

    def post(self, request, *args, **kwargs):
        first_name = request.data['first_name']
        last_name = request.data['last_name']
        email = request.data['email']
        phone = request.data['phone']
        address = request.data['address']
        password = request.data['password']
        data1 = {'first_name': first_name, 'last_name': last_name, 'email': email,
                 'phone': phone, 'address': address, 'password': password}
        user_data_serializer = UserDataSerializer(data=data1)
        driving_license_front_image = request.data['driving_license_front_image']
        driving_license_back_image = request.data['driving_license_back_image']
        binary_front_image = base64.b64encode(
            driving_license_front_image.read())
        binary_back_image = base64.b64encode(driving_license_back_image.read())
        national_insurance = request.data['national_insurance']
        is_condemned_prior = request.data['is_condemned_prior']
        gender = request.data['gender']
        data2 = {'driving_license_front_image': binary_front_image,
                 'driving_license_back_image': binary_back_image,
                 'national_insurance': national_insurance,
                 'is_condemned_prior': is_condemned_prior,
                 'gender': gender}
        driver_data_serializer = DriverDataSerializer(data=data2)
        if user_data_serializer.is_valid() and driver_data_serializer.is_valid():
            user_data = UserData(first_name=first_name, last_name=last_name, email=email,
                                 phone=phone, address=address, password=password)
            user_data.save()
            driver_data = DriverData(driving_license_front_image=binary_front_image,
                                     driving_license_back_image=binary_back_image,
                                     national_insurance=national_insurance,
                                     is_condemned_prior=is_condemned_prior, gender=gender,
                                     user_data=user_data)
            driver_data.save()
            return Response(user_data.id, status=status.HTTP_201_CREATED)
        driver_data_serializer.is_valid()
        errors = {
            'user data errors ': user_data_serializer.errors,
            'driver data errors': driver_data_serializer.errors
        }
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class VehicleAPIView(APIView):
    """
    API for registering vehicles.
    """
    permission_classes = [IsDriver]

    def post(self, request, *args, **kwargs):
        year = request.data['year']
        brand = request.data['brand']
        Class = request.data['Class']
        binary_fitness_image = base64.b64encode(request.data['fitness'].read())
        plate_no = request.data['plate_no']
        has_child_seat = request.data['has_child_seat']
        maximum_passengers = request.data['maximum_passengers']
        maximum_luggage = request.data['maximum_luggage']
        driven_mileage = request.data['driven_mileage']
        is_refurbished = request.data['is_refurbished']
        driver = request.user.driver

        data = {'year': year, 'brand': brand, 'Class': Class, 'fitness': binary_fitness_image,
                'plate_no': plate_no, 'has_child_seat': has_child_seat,
                'maximum_passengers': maximum_passengers, 'maximum_luggage': maximum_luggage,
                'driven_mileage': driven_mileage, 'is_refurbished': is_refurbished}
        vehicle_serializer = VehicleSerializer(data=data)
        if vehicle_serializer.is_valid():
            vehicle = Vehicle(year=year, brand=brand, Class=Class, fitness=binary_fitness_image,
                              plate_no=plate_no, has_child_seat=has_child_seat,
                              maximum_passengers=maximum_passengers, maximum_luggage=maximum_luggage,
                              driven_mileage=driven_mileage, is_refurbished=is_refurbished,
                              owner=driver)
            vehicle.save()

            for c in range(len(request.FILES.getlist("papers"))):
                paperImage = request.FILES.getlist("papers")
                paperName = request.data.getlist('paper_name')
                data = {
                    'paper_name': paperName[c],
                    'paper': base64.b64encode(paperImage[c].read())
                }

                serializer_class = PaperSerializer(data=data)
                if serializer_class.is_valid():
                    paper = Paper(
                        vehicle=vehicle,
                        paper_name=paperName[c],
                        paper=base64.b64encode(paperImage[c].read()),
                    )
                    paper.save()
            driver.status = 'Pending'
            driver.save()
            return Response({'message': "You have successfully completed your registration"},
                            status=status.HTTP_201_CREATED)
        return Response({'message': 'Unsuccessful vehicle post request'}, status=status.HTTP_400_BAD_REQUEST)


class DriversVehicle(APIView):
    """
    API for showing info of specific driver and his/her vehicles
    """

    permission_classes = [IsAdmin]

    def get(self, request, id):
        driver = get_object_or_404(Driver, id=id)
        vehicles = driver.vehicle_set.all()
        vehicle_serializer = VehicleDetailsSerializer(vehicles, many=True)
        driver_serializer = DriverSerializer(driver)
        data = {
            'driver info': driver_serializer.data,
            'vehicle info': vehicle_serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)


class ValidateToken(APIView):
    def post(self, request):
        token = request.data['token']
        id = request.data['id']
        user_data = get_object_or_404(UserData, id=id)
        userToken = get_object_or_404(
            UserToken, user_data=user_data, token=token)
        created = userToken.creation_time

        if userToken.is_valid:
            userToken.delete()
            create_user(id)
            return Response({'message': 'Token is valid, You have successfully completed your registration'},
                            status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Token is invalid'}, status=status.HTTP_400_BAD_REQUEST)


class ResendToken(APIView):
    def post(self, request):
        id = request.data['id']
        user = get_object_or_404(UserData, id=id)
        # Generating new token
        new_token = generateOTP()
        # Removing all previous token from the database
        tokenModel = UserToken.objects.filter(user_data=user)
        tokenModel.delete()
        # Saving new token to the database
        token = UserToken.objects.create(user_data=user, token=new_token)
        token.save()
        send_mail(
            # title:
            "You are one step behind of becoming a registered driver",
            # message:
            "Your Registration token is: " + new_token,
            # from:
            settings.EMAIL_HOST_USER,
            # to:
            [user.email]
        )
        return Response({'message': 'Token has been sent to your email'}, status=status.HTTP_200_OK)


#  This function is used to create OTP in purpose of reseting password
class ResetPasswordAPIView(APIView):
    def post(self, request):
        email = request.data['email']
        user = get_object_or_404(User, email=email)
        if user:
            # Generating New OTP
            otp = generateOTP()

            # Deleting ALL previous OTPs
            otpModel = UserOTP.objects.filter(user_data=user)
            otpModel.delete()

            # Saving New OTP to DB
            otpToBeSaved = UserOTP.objects.create(user_data=user, otp=otp)
            otpToBeSaved.save()
            send_mail(
                # title:
                "Password reset otp",
                # message:
                "Your passwprd reset otp is: " + otp,
                # from:
                settings.EMAIL_HOST_USER,
                # to:
                [email]
            )
            return Response({'message': 'New password reset token has been sent to your email'},
                            status=status.HTTP_200_OK)
        return Response({'message': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)


# Validating OTP for password reset
class ValidateResetPasswordOTP(APIView):
    def post(self, request):
        otp = request.data['otp']
        email = request.data['email']
        user = get_object_or_404(User, email=email)
        userOTP = get_object_or_404(UserOTP, user_data=user, otp=otp)
        created = userOTP.creation_time

        if userOTP.is_valid and userOTP.is_used == False:
            userOTP.is_used = True
            userOTP.save()
            return Response({'message': 'OTP is valid'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'OTP is invalid'}, status=status.HTTP_400_BAD_REQUEST)


# Resetting password reset OTP
class ResendOTP(APIView):
    def post(self, request):
        email = request.data['email']
        user = get_object_or_404(User, email=email)
        # Generating new token
        new_otp = generateOTP()
        # Removing all previous OTPs from the database
        otpModel = UserOTP.objects.filter(user_data=user)
        otpModel.delete()
        # Saving new token to the database
        otp = UserOTP.objects.create(user_data=user, otp=new_otp)
        otp.save()
        send_mail(
            # title:
            "Password reset otp",
            # message:
            "Your passwprd reset otp is: " + new_otp,
            # from:
            settings.EMAIL_HOST_USER,
            # to:
            [email]
        )
        return Response({'message': 'OTP Succeccfully sent'}, status=status.HTTP_200_OK)


# API FOR CHANGING PASSWORD
class ChangePassword(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']
        user = get_object_or_404(User, email=email)
        otp = get_object_or_404(UserOTP, user_data=user)
        if otp.is_used and otp.is_valid:
            user.set_password(password)
            user.save()
            otp.delete()
            return Response({'message': 'Password has been changed'}, status=status.HTTP_200_OK)

        else:
            return Response({'message': 'OTP Authentication failed or expired'}, status=status.HTTP_400_BAD_REQUEST)


class CheckEmailIfExists(APIView):
    """
    Checks if given user is already being used by  a user.
    """

    def post(self, request):
        email = request.data['email']
        user = get_object_or_404(User, email=email)
        if user:
            return Response({'message': 'Email exists'}, status=status.HTTP_200_OK)
        return Response({'message': 'Email does not exist'}, status=status.HTTP_400_BAD_REQUEST)


# Create trip Request API View
class CreateTripRequestAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated & IsNotBlacklisted]

    def post(self, request):

        serializers_data = {
            'pickup_location': request.data['pickup_location'],
            'drop_off_location': request.data['drop_off_location'],
            'pickup_time': request.data['pickup_time'],
            'booking_method': request.data['booking_method'],
            'date': request.data['date'],
            'number_of_passengers': request.data['number_of_passengers'],
            'luggage_weight': request.data['luggage_weight'],
            'luggage_amount': request.data['luggage_amount'],
            'is_child_seat': request.data['is_child_seat'],
        }
        if request.data['booking_method'] == 'hourly':
            serializers_data['hours'] = request.data['hours']

        serializer_class = TripRequestSerializer(data=serializers_data)
        user = request.user
        if user and serializer_class.is_valid():
            trip_request = Trip.objects.create(user=user, **serializers_data)
            if request.data['is_child_seat']:
                for child in request.data['childs']:
                    child_serializer = ChildSerializer(data={
                        'age': child['age'],
                    })

                    if child_serializer.is_valid():
                        child = Child.objects.create(
                            trip=trip_request,
                            age=child_serializer.data['age'],
                        )
                        child.save()
                if child_serializer.errors:
                    return Response(child_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                if request.data['stops'] is not None:
                    for stop in request.data['stops']:
                        stop_serializer = StopSerializer(data={
                            'location': stop["location"],
                        })
                        if stop_serializer.is_valid():
                            stop = Stops.objects.create(
                                trip=trip_request,
                                location=stop_serializer.data['location']
                            )
                            stop.save()
                        if stop_serializer.errors:
                            return Response({'message': 'Stop serializer errors', 'errors': stop_serializer.errors},
                                            status=status.HTTP_400_BAD_REQUEST)
            vehicles = Vehicle.objects.all()
            pickup_location1 = serializers_data['pickup_location']

            if request.data["selected_driver_id"]:
                driverIsValid = False
                selected_driver = ""
                try:
                    selected_driver = Driver.objects.get(
                        id=request.data["selected_driver_id"])
                    driverIsValid = True
                except Exception as e:
                    return Response({'message': 'Driver does not exist'}, status=status.HTTP_400_BAD_REQUEST)
                if selected_driver and driverIsValid:
                    driver = selected_driver
                    trip_request.driver = selected_driver
                    trip_request.assigned_vehicle = assignVehicle.getVehicle(
                        driver)
                    if trip_request.driver and trip_request.assigned_vehicle:
                        trip_request.save()
                        return Response({
                            'message': 'Trip request has been created',
                            'trip_id': trip_request.id,
                            "Driver Name": trip_request.driver.user.first_name,
                            "Vehicle name": trip_request.assigned_vehicle.brand,
                            # "Vehicle id": trip_request.assigned_vehicle.id,
                        }, status=status.HTTP_201_CREATED)
            else:
                pass

            if request.data['preferred_gender'] and (request.data['preferred_gender'] == 'Male' or request.data['preferred_gender'] == 'Female' or request.data['preferred_gender'] == 'Others'):
                drivers = Driver.objects.filter(
                    gender=request.data['preferred_gender'])
                try:
                    driver, distance = assignDriver.getDriver(drivers, pickup_location1, child_seat=request.data['is_child_seat'],
                                                              required_vehicle_type=request.data['vehicle_type'])
                    trip_request.driver = driver
                    trip_request.assigned_vehicle = assignVehicle.getVehicle(
                        driver)
                except Exception as e:
                    return Response({'message': 'No driver available 1'}, status=status.HTTP_400_BAD_REQUEST)
                trip_request.driver = driver
                trip_request.assigned_vehicle = assignVehicle.getVehicle(
                    driver)
                if trip_request.driver and trip_request.assigned_vehicle:
                    trip_request.save()
                    return Response({
                        'message': 'Trip request has been created',
                        'trip_id': trip_request.id,
                        "Driver Name": trip_request.driver.user.first_name,
                        "Vehicle name": trip_request.assigned_vehicle.brand,
                        "distance":  str(round(distance, 3)) + " km",
                        # "Vehicle id": trip_request.assigned_vehicle.id,
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({'message': 'No Vehicle found for this driver'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                drivers = Driver.objects.all()
                try:
                    driver, distance = assignDriver.getDriver(drivers, pickup_location1, child_seat=request.data['is_child_seat'],
                                                              required_vehicle_type=request.data['vehicle_type'])
                    trip_request.driver = driver
                    trip_request.assigned_vehicle = assignVehicle.getVehicle(
                        driver)
                except Exception as e:
                    return Response({'message': 'No driver available 2'}, status=status.HTTP_400_BAD_REQUEST)
                trip_request.driver = driver
                trip_request.assigned_vehicle = assignVehicle.getVehicle(
                    driver)
                if trip_request.driver and trip_request.assigned_vehicle:
                    trip_request.save()
                    return Response({
                        'message': 'Trip request has been created',
                        'trip_id': trip_request.id,
                        "Driver Name": trip_request.driver.user.first_name,
                        "Vehicle name": trip_request.assigned_vehicle.brand,
                        "distance": str(round(distance, 3)) + " km",
                        # "Vehicle id": trip_request.assigned_vehicle.id,
                    }, status=status.HTTP_201_CREATED)

        return Response({'message': 'Request Not Completed'}, status=status.HTTP_400_BAD_REQUEST)


class CreateStaticTripRequestAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated & IsNotBlacklisted]

    def post(self, request):

        serializers_data = {
            'pickup_location': request.data['pickup_location'],
            'drop_off_location': request.data['drop_off_location'],
            'pickup_time': request.data['pickup_time'],
            'booking_method': request.data['booking_method'],
            'date': request.data['date'],
            'number_of_passengers': request.data['number_of_passengers'],
            'luggage_weight': request.data['luggage_weight'],
            'luggage_amount': request.data['luggage_amount'],
            'is_child_seat': request.data['is_child_seat'],
        }
        if request.data['booking_method'] == 'hourly':
            serializers_data['hours'] = request.data['hours']

        serializer_class = TripRequestSerializer(data=serializers_data)
        user = request.user
        if user and serializer_class.is_valid():
            trip_request = Trip.objects.create(user=user, **serializers_data)
            if request.data['is_child_seat']:
                for child in request.data['childs']:
                    child_serializer = ChildSerializer(data={
                        'age': child['age'],
                    })

                    if child_serializer.is_valid():
                        child = Child.objects.create(
                            trip=trip_request,
                            age=child_serializer.data['age'],
                        )
                        child.save()
                if child_serializer.errors:
                    return Response(child_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                if request.data['stops'] is not None:
                    for stop in request.data['stops']:
                        stop_serializer = StopSerializer(data={
                            'location': stop["location"],
                        })
                        if stop_serializer.is_valid():
                            stop = Stops.objects.create(
                                trip=trip_request,
                                location=stop_serializer.data['location']
                            )
                            stop.save()
                        if stop_serializer.errors:
                            return Response({'message': 'Stop location is not valid'}, status=status.HTTP_400_BAD_REQUEST)
            trip_request.trip_status = 'pending'
            trip_request.save()
            return Response({
                'message': 'Trip request has been created',
                'trip_id': trip_request.id,
            }, status=status.HTTP_201_CREATED)

        return Response({'message': 'Request Not Completed'}, status=status.HTTP_400_BAD_REQUEST)


class FindRiderApiView(APIView):
    permission_classes = [permissions.IsAuthenticated & IsNotBlacklisted]

    def post(self, request):
        user = request.user
        if user:
            user = request.user
            if request.data['trip_id']:
                trip_request = Trip.objects.get(
                    id=request.data['trip_id'], user=user)
                if trip_request:
                    if trip_request.status == 'pending':
                        if request.data['random'] and request.data['gender']:
                            # Random Driver Selection based on gender
                            assigned_driver = getDriver()
                        elif request.data['fev_driver'] and request.data['gender']:
                            # Driver Selection based on fev_driver

                            assigned_driver = getDriver()

                        elif request.data['random']:
                            # Select a driver randomly from all drivers
                            assigned_driver = getDriver()

                trip_request.driver = assigned_driver
                trip_request.status = 'ongoing'
                trip_request.save()

            else:
                return Response({'message': 'Trip ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)


class FevoriteDriverApiView(APIView):
    permission_classes = [permissions.IsAuthenticated & IsNotBlacklisted]

    def post(self, request):
        user = request.user
        if user:
            drivers = FevoriteDriverModel.objects.filter(user=user)
            serializer_class = FevoriteDriverSerializer(drivers, many=True)
            res = serializer_class.data
            try:
                if request.data['gender'] and (request.data['gender'] == 'Male' or request.data['gender'] == 'Female' or request.data['gender'] == 'Others'):
                    driver_data = []
                    for item in res:
                        if item['gender'] == request.data["gender"]:
                            driver_data.append(item)
                    return Response({'message': 'Fevorite Driver List', 'data': driver_data}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'Fevorite Driver List', 'data': res}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'message': 'Fevorite Driver List', 'data': res}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)


class CancelTrip(APIView):
    """
    Cancels trip request.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, requests, trip_id):
        trip = get_object_or_404(Trip, id=trip_id)
        if trip.trip_status == 'completed':
            return Response(status=status.HTTP_403_FORBIDDEN)
        try:
            driver = trip.driver.user
        except AttributeError:
            driver = None
        if requests.user == trip.user or is_admin(requests.user) or (driver is not None and requests.user == driver):
            trip.trip_status = 'cancelled'
            trip.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_403_FORBIDDEN)


class UserRatesDriver(APIView):
    """
    Implements the functionality of User giving rating to Drivers.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, trip_id):
        trip = get_object_or_404(Trip, id=trip_id)
        if trip.trip_status != 'completed':
            return Response(status=status.HTTP_403_FORBIDDEN)
        user_obj = request.user
        if user_obj.rating_set.filter(trip=trip).exists():
            return Response(status=status.HTTP_403_FORBIDDEN)
        if trip.user != user_obj:
            return Response(status=status.HTTP_403_FORBIDDEN)
        rating_serializer = RatingSerializer(data=request.data)
        if rating_serializer.is_valid():
            rating_serializer.save(rating_from=user_obj,
                                   rated_to=trip.driver.user, trip=trip)
            return Response(rating_serializer.data, status=status.HTTP_201_CREATED)
        return Response(rating_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DriverRatesUser(APIView):
    """
    Implements the functionality of driver giving ratings to users.
    """
    permission_classes = [IsVerifiedDriver]

    def post(self, request, trip_id):
        trip = get_object_or_404(Trip, id=trip_id)
        if trip.trip_status != 'completed':
            return Response(status=status.HTTP_403_FORBIDDEN)
        user_obj = request.user
        if user_obj.rating_set.filter(trip=trip).exists():
            return Response(status=status.HTTP_403_FORBIDDEN)
        if trip.driver.user != user_obj:
            return Response(status=status.HTTP_403_FORBIDDEN)
        rating_serializer = RatingSerializer(data=request.data)
        if rating_serializer.is_valid():
            rating_serializer.save(rating_from=user_obj,
                                   rated_to=trip.user, trip=trip)
            return Response(rating_serializer.data, status=status.HTTP_201_CREATED)
        return Response(rating_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EditTrips(UpdateAPIView):
    """
    Edits Trip information
    """
    permission_classes = [IsAdmin]
    serializer_class = EditTripsSerializer

    def get_object(self):
        return get_object_or_404(Trip, id=self.kwargs['id'])


class UpdateTripAPIView(APIView):
    """
    Edits Trip information
    """
    permission_classes = [IsAdmin]

    def patch(self, request, id):
        trip = get_object_or_404(Trip, id=self.kwargs['id'])
        try:
            driver_id = request.data['driver']
            driver = get_object_or_404(Driver, id=driver_id)
        except Exception as e:
            return Response({'message': 'Driver not found'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            vehicle_id = request.data['assigned_vehicle']
            vehicle = get_object_or_404(Vehicle, id=vehicle_id)
        except Exception as e:
            return Response({'message': 'Vehicle not found'}, status=status.HTTP_400_BAD_REQUEST)

        trip_status = request.data['trip_status']
        trip.driver = driver
        trip.assigned_vehicle = vehicle
        trip.trip_status = trip_status
        trip.save()
        return Response({'message': trip.trip_status}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EditChildData(UpdateAPIView):
    """
    Edits child's info of a trip
    """
    permission_classes = [IsAdmin]
    serializer_class = ChildSerializer

    def get_object(self):
        return get_object_or_404(Child, pk=self.kwargs['pk'])


class EditStops(UpdateAPIView):
    """
    Edits Stops info.
    """
    permission_classes = [IsAdmin]
    serializer_class = StopSerializer

    def get_object(self):
        return get_object_or_404(Stops, pk=self.kwargs['pk'])


class ToggleBlockedStatus(APIView):
    """
    Toggles Users Balcklisted state.
    """
    permission_classes = [IsAdmin]

    def get(self, request, id):
        user = get_object_or_404(User, id=id)
        user.blacklisted = not user.blacklisted
        user.save()
        return Response(status=status.HTTP_200_OK)
