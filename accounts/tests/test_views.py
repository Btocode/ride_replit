import uuid
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient
from accounts.models import CustomUser, Driver, DriverData, UserData, Vehicle
import json
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts import models

from accounts.models import Driver, Stops, Trip, Admin, Child

user_model = get_user_model()


def create_users(num_of_user=1, email=None):
    users = []
    if email is not None:
        user = user_model.objects.create(first_name=f'First_name', last_name=f'last_name', phone='01757578',
                                         address='dhaka', email=email)
        user.set_password('123password')
        user.save()
        return user
    for _ in range(num_of_user):
        user = user_model.objects.create(first_name=f'First_name', last_name=f'last_name', phone='01757578',
                                         address='dhaka', email=str(uuid.uuid4()) + '@gmail.com')
        user.set_password('123password')
        user.save()
        users.append(user)
    return users


def create_trips(number_of_trips):
    users = create_users(number_of_trips)
    trips = []
    for c in range(number_of_trips):
        trips.append(Trip.objects.create(
            date='2020-4-12', user=users[c], booking_method='hourly', pickup_location='dhaka',
            pickup_time='13:23', drop_off_location='chittagong', number_of_passengers=5, payment_status='paid'
        ))
    return users, trips


def create_driver(num):
    users = create_users(num)
    img = Image.new('RGB', (250, 250))
    image = img.tobytes()
    drivers = []
    for c in range(num):
        driver = Driver.objects.create(
            user=users[c], driving_license_front_image=image, driving_license_back_image=image,
            national_insurance='1224',
            is_condemned_prior=False
        )
        drivers.append(driver)
    return drivers


def create_admin():
    user = create_users(email='admin@gmail.com')
    admin = Admin.objects.create(designation_name='test', user=user)
    return admin


def log_in(self, data):
    login = self.client.post(reverse('login'), data=data)
    data = login.json()["tokens"].replace("'", '"')
    temp = json.loads(data)

    token = temp['access']
    return token


def assign_vehicle(driver):
    img = Image.new('RGB', (250, 250))
    content = img.tobytes()
    data = {
        "year": "2020",
        "brand": "test",
        "Class": "test",
        "fitness": content,
        "plate_no": "5645654",
        "has_child_seat": False,
        "maximum_passengers": 4,
        "maximum_luggage": 3,
        "driven_mileage": 4124,
        "is_refurbished": True,
        "current_location": "22.714802, 88.4824967"
    }
    vehicle = Vehicle.objects.create(**data, owner=driver)
    return vehicle


class DriverVehicleTest(TestCase):
    def setUp(self) -> None:
        create_driver(1)
        create_admin()

    def test_driver_and_vehicle_info_is_being_returned(self):
        driver = Driver.objects.all()[0]
        assign_vehicle(driver)
        login_cred = {'email': 'admin@gmail.com', 'password': '123password'}
        token = log_in(self, login_cred)
        response = self.client.get(reverse('drivers_vehicle', args=(driver.id,)),
                                   content_type='application/json',
                                   **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)


class CreateTripRequestApiViewTest(TestCase):
    def setUp(self) -> None:
        create_users(1)
        drivers = create_driver(5)
        for driver in drivers:
            assign_vehicle(driver)

    def test_trip_is_being_created_without_child_and_stops_info(self):
        data = {
            'pickup_location': '37.4220936, -122.083922',
            'drop_off_location': 'drop_off_location',
            'pickup_time': '12:23',
            'booking_method': 'one way',
            'date': '2022-4-23',
            'number_of_passengers': 2,
            'luggage_weight': 12,
            'luggage_amount': 1,
            'is_child_seat': False,
            'gender': 'male'
        }
        user = user_model.objects.all()[0]
        login_cred = {'email': user.email, 'password': '123password'}
        token = log_in(self, login_cred)
        response = self.client.post(reverse('trip_request'), content_type='application/json', data=data,
                                    **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)

    def test_trip_is_being_created_with_childs_and_stops_info(self):
        data = {
            'pickup_location': '37.4220936, -122.083922',
            'drop_off_location': 'drop_off_location',
            'pickup_time': '12:23',
            'booking_method': 'one way',
            'date': '2022-4-23',
            'number_of_passengers': 2,
            'luggage_weight': 12,
            'luggage_amount': 1,
            'is_child_seat': True,
            'gender': 'male',
            "childs": [
                {
                    "age": 10,
                    "height": 5
                },
                {
                    "age": 14,
                    "height": 3
                }
            ],
            "stops": [
                {
                    "location": "Mohakhali"
                },
                {
                    "location": "Dhaka"
                },
                {
                    "location": "Airport"
                }
            ]
        }
        user = user_model.objects.all()[0]
        login_cred = {'email': user.email, 'password': '123password'}
        token = log_in(self, login_cred)
        response = self.client.post(reverse('trip_request'), content_type='application/json', data=data,
                                    **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)

    def test_is_being_created_with_hourly_booking_method(self):
        data = {
            'pickup_location': '37.4220936, -122.083922',
            'drop_off_location': 'drop_off_location',
            'pickup_time': '12:23',
            'booking_method': 'hourly',
            'hours': 2,
            'date': '2022-4-23',
            'number_of_passengers': 2,
            'luggage_weight': 12,
            'luggage_amount': 1,
            'is_child_seat': False,
            'gender': 'male'
        }
        user = user_model.objects.all()[0]
        login_cred = {'email': user.email, 'password': '123password'}
        token = log_in(self, login_cred)
        response = self.client.post(reverse('trip_request'), content_type='application/json', data=data,
                                    **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)

    def trip_cant_be_booked_if_user_is_black_listed(self):
        data = {
            'pickup_location': '37.4220936, -122.083922',
            'drop_off_location': 'drop_off_location',
            'pickup_time': '12:23',
            'booking_method': 'hourly',
            'hours': 2,
            'date': '2022-4-23',
            'number_of_passengers': 2,
            'luggage_weight': 12,
            'luggage_amount': 1,
            'is_child_seat': False,
            'gender': 'male'
        }
        user = user_model.objects.all()[0]
        user.blacklisted = True
        user.save()
        login_cred = {'email': user.email, 'password': '123password'}
        token = log_in(self, login_cred)
        response = self.client.post(reverse('trip_request'), content_type='application/json', data=data,
                                    **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, 403)


class CheckEmailIfExistsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_users(10)

    def test_checks_if_exists(self):
        user = user_model.objects.all()[0]
        data = {'email': user.email}
        response = self.client.post(reverse('check_email'), data=data)
        self.assertEqual(response.status_code, 200)

        data = {'email': 'email12@gmail.com'}
        response = self.client.post(reverse('check_email'), data=data)
        self.assertEqual(response.status_code, 404)


class ToggleBlockStatusTest(TestCase):
    def setUp(self) -> None:
        create_users(10)
        create_admin()

    def test_toggles_user_block_status(self):
        login_cred = {'email': 'admin@gmail.com', 'password': '123password'}
        token = log_in(self, login_cred)
        users = user_model.objects.all()
        for user in users:
            response = self.client.get(reverse('toggle_block_status', args=(user.id,)),
                                       content_type='application/json',
                                       **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
            self.assertEqual(response.status_code, 200)
            user.refresh_from_db()
            self.assertEqual(user.blacklisted, True)
            response = self.client.get(reverse('toggle_block_status', args=(user.id,)),
                                       content_type='application/json',
                                       **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
            self.assertEqual(response.status_code, 200)
            user.refresh_from_db()
            self.assertEqual(user.blacklisted, False)

    def test_user_cant_block_if_not_admin(self):
        for user in user_model.objects.all():
            if not hasattr(user, 'admin'):
                current_user = user
                break
        user = user_model.objects.all()[0]
        login_cred = {'email': current_user.email, 'password': '123password'}
        token = log_in(self, login_cred)
        user2 = user_model.objects.all()[1]
        response = self.client.get(reverse('toggle_block_status', args=(user2.id,)),
                                   content_type='application/json',
                                   **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, 403)


class EditTripsTest(TestCase):
    def setUp(self) -> None:
        create_admin()
        create_trips(10)
        create_users(1)

    def test_editing_trip_info(self):
        login_cred = {'email': 'admin@gmail.com', 'password': '123password'}
        token = log_in(self, login_cred)
        data = {'pickup_location': 'Mars'}
        for trip in Trip.objects.all():
            response = self.client.patch(reverse('edit_trips', args=(trip.id,)),
                                         content_type='application/json', data=data,
                                         **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
            self.assertEqual(response.status_code, 200)
            trip.refresh_from_db()
            self.assertEqual(trip.pickup_location, 'Mars')

    def test_users_cant_edit_trips_if_not_admin(self):
        for user in user_model.objects.all():
            if not hasattr(user, 'admin'):
                current_user = user
                break
        login_cred = {'email': current_user.email, 'password': '123password'}
        token = log_in(self, login_cred)
        data = {'pickup_location': 'Mars'}
        trip = Trip.objects.all()[0]
        response = self.client.patch(reverse('edit_trips', args=(trip.id,)),
                                     content_type='application/json', data=data,
                                     **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, 403)


class EditStopsTest(TestCase):

    def setUp(self) -> None:
        create_users(1)
        create_admin()
        _, trip = create_trips(1)
        Stops.objects.create(trip=trip[0], location='barishal')

    def test_edit_stops(self):
        login_cred = {'email': 'admin@gmail.com', 'password': '123password'}
        token = log_in(self, login_cred)
        data = {'location': 'Sirajgonj'}
        for stop in Stops.objects.all():
            response = self.client.patch(reverse('edit_stops', args=(stop.id,)),
                                         content_type='application/json', data=data,
                                         **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
            self.assertEqual(response.status_code, 200)
            stop.refresh_from_db()
            self.assertEqual(stop.location, 'Sirajgonj')

    def test_user_cant_edit_stops_if_not_admin(self):
        for user in user_model.objects.all():
            if not hasattr(user, 'admin'):
                current_user = user
                break
        login_cred = {'email': current_user.email, 'password': '123password'}
        token = log_in(self, login_cred)
        data = {'location': 'Sirajgonj'}
        for stop in Stops.objects.all():
            response = self.client.patch(reverse('edit_stops', args=(stop.id,)),
                                         content_type='application/json', data=data,
                                         **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
            self.assertEqual(response.status_code, 403)


class EditChildDataTest(TestCase):

    def setUp(self) -> None:
        create_users(1)
        create_admin()
        _, trip = create_trips(1)
        Child.objects.create(trip=trip[0], age='3')

    def test_edit_child_info(self):
        login_cred = {'email': 'admin@gmail.com', 'password': '123password'}
        token = log_in(self, login_cred)
        data = {'age': 4}
        for child in Child.objects.all():
            response = self.client.patch(reverse('edit_child_info', args=(child.id,)),
                                         content_type='application/json', data=data,
                                         **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
            self.assertEqual(response.status_code, 200)
            child.refresh_from_db()
            self.assertEqual(child.age, 4)

    def test_users_cant_edit_child_info_if_not_admin(self):
        for user in user_model.objects.all():
            if not hasattr(user, 'admin'):
                current_user = user
                break
        login_cred = {'email': current_user.email, 'password': '123password'}
        token = log_in(self, login_cred)
        data = {'age': 4}
        child = Child.objects.all()[0]
        response = self.client.patch(reverse('edit_child_info', args=(child.id,)),
                                     content_type='application/json', data=data,
                                     **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, 403)


class DriverRatesUser(TestCase):

    def setUp(self) -> None:
        create_driver(2)
        create_trips(1)

    def test_driver_rates_user(self):
        trip = Trip.objects.all()[0]
        driver = Driver.objects.all()[0]
        trip.driver = driver
        trip.driver.status = 'verified'
        trip.driver.save()
        trip.trip_status = 'completed'
        trip.save()
        login_cred = {'email': driver.user.email, 'password': '123password'}
        token = log_in(self, login_cred)
        data = {'rating': 5,
                'review': 'good'}
        response = self.client.post(reverse('driver_rates_user', args=(trip.id,)), content_type='application/json',
                                    data=data, **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, 201)

    def test_rating_cant_be_done_if_trip_isnt_completed(self):
        trip = Trip.objects.all()[0]
        driver = Driver.objects.all()[0]
        driver.status = 'verified'
        driver.save()
        trip.driver = driver
        trip.driver.status = 'verified'
        trip.save()
        login_cred = {'email': driver.user.email, 'password': '123password'}
        token = log_in(self, login_cred)
        data = {'rating': 5,
                'review': 'good'}
        response = self.client.post(reverse('driver_rates_user', args=(trip.id,)), content_type='application/json',
                                    data=data, **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, 403)

    def test_rating_cant_be_done_if_driver_already_rated(self):
        trip = Trip.objects.all()[0]
        driver = Driver.objects.all()[0]
        driver.status = 'verified'
        driver.save()
        trip.driver = driver
        trip.trip_status = 'completed'
        trip.save()
        login_cred = {'email': driver.user.email, 'password': '123password'}
        token = log_in(self, login_cred)
        data = {'rating': 5,
                'review': 'good'}
        response = self.client.post(reverse('driver_rates_user', args=(trip.id,)), content_type='application/json',
                                    data=data, **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        second_response = self.client.post(reverse('driver_rates_user', args=(trip.id,)),
                                           content_type='application/json',
                                           data=data, **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(second_response.status_code, 403)

    def test_driver_cant_rate_if_they_are_not_trip_driver(self):
        trip = Trip.objects.all()[0]
        driver = Driver.objects.all()[0]
        driver.status = 'verified'
        driver.save()
        trip.driver = driver
        trip.trip_status = 'completed'
        trip.save()
        another_driver = Driver.objects.all()[1]
        login_cred = {'email': another_driver.user.email, 'password': '123password'}
        token = log_in(self, login_cred)
        data = {'rating': 5,
                'review': 'good'}
        response = self.client.post(reverse('driver_rates_user', args=(trip.id,)), content_type='application/json',
                                    data=data, **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, 403)

    def test_rating_cant_be_done_if_rating_isnt_within_valid_range(self):
        trip = Trip.objects.all()[0]
        driver = Driver.objects.all()[0]
        driver.status = 'verified'
        driver.save()
        trip.driver = driver
        trip.trip_status = 'completed'
        trip.save()
        login_cred = {'email': driver.user.email, 'password': '123password'}
        token = log_in(self, login_cred)
        data = {'rating': -2,
                'review': 'good'}
        data2 = {'rating': 11,
                 'review': 'good'}
        response = self.client.post(reverse('driver_rates_user', args=(trip.id,)), content_type='application/json',
                                    data=data, **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        response2 = self.client.post(reverse('driver_rates_user', args=(trip.id,)), content_type='application/json',
                                     data2=data2, **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response2.status_code, 400)


class VehicleRegisterTest(TestCase):
    def setUp(self) -> None:
        create_driver(1)

    def test_vehicle_register(self):
        driver = Driver.objects.all()[0]
        img = Image.new('RGB', (250, 250))
        content = img.tobytes()
        imagefile = SimpleUploadedFile('test', content=content, content_type='image/jpeg')
        # imagefile = SimpleUploadedFile('accounts/tests/images/2.jpg', b''),
        data = {
            "year": "2020",
            "brand": "test",
            "Class": "test",
            "fitness": imagefile,
            "plate_no": "5645654",
            "has_child_seat": False,
            "maximum_passengers": 4,
            "maximum_luggage": 3,
            "driven_mileage": 4124,
            "is_refurbished": True,
            "papers": imagefile,
            "papers": imagefile,
            "paper_name": "test",
            "paper_name": "test",
        }
        login_cred = {'email': driver.user.email, 'password': '123password'}
        token = log_in(self, login_cred)
        response = self.client.post(reverse('register_vehicle'), format='multipart',
                                    data=data, **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, 201)


class UserRatesDriver(TestCase):

    def setUp(self) -> None:
        create_driver(2)
        create_trips(1)
        create_users(1)

    def test_user_rates_driver(self):
        trip = Trip.objects.all()[0]
        driver = Driver.objects.all()[0]
        trip.driver = driver
        trip.trip_status = 'completed'
        trip.save()
        login_cred = {'email': trip.user.email, 'password': '123password'}
        token = log_in(self, login_cred)
        data = {'rating': 5,
                'review': 'good'}
        response = self.client.post(reverse('user_rates_driver', args=(trip.id,)), content_type='application/json',
                                    data=data, **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, 201)

    def test_rating_cant_be_done_if_trip_isnt_completed(self):
        trip = Trip.objects.all()[0]
        driver = Driver.objects.all()[0]
        trip.driver = driver
        trip.save()
        login_cred = {'email': trip.user.email, 'password': '123password'}
        token = log_in(self, login_cred)
        data = {'rating': 5,
                'review': 'good'}
        response = self.client.post(reverse('user_rates_driver', args=(trip.id,)), content_type='application/json',
                                    data=data, **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, 403)

    def test_rating_cant_be_done_if_user_already_rated(self):
        trip = Trip.objects.all()[0]
        driver = Driver.objects.all()[0]
        trip.driver = driver
        trip.trip_status = 'completed'
        trip.save()
        login_cred = {'email': trip.user.email, 'password': '123password'}
        token = log_in(self, login_cred)
        data = {'rating': 5,
                'review': 'good'}
        response = self.client.post(reverse('user_rates_driver', args=(trip.id,)), content_type='application/json',
                                    data=data, **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        second_response = self.client.post(reverse('user_rates_driver', args=(trip.id,)),
                                           content_type='application/json',
                                           data=data, **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(second_response.status_code, 403)

    def test_user_cant_rate_if_they_are_not_trip_user(self):
        trip = Trip.objects.all()[0]
        driver = Driver.objects.all()[0]
        trip.driver = driver
        trip.trip_status = 'completed'
        trip.save()
        another_driver = Driver.objects.all()[1]
        current_user = None
        for user in user_model.objects.all():
            if user != trip.user:
                current_user = user
                break
        login_cred = {'email': current_user.email, 'password': '123password'}
        token = log_in(self, login_cred)
        data = {'rating': 5,
                'review': 'good'}
        response = self.client.post(reverse('user_rates_driver', args=(trip.id,)), content_type='application/json',
                                    data=data, **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, 403)

    def test_rating_cant_be_done_if_rating_isnt_within_valid_range(self):
        trip = Trip.objects.all()[0]
        driver = Driver.objects.all()[0]
        trip.driver = driver
        trip.trip_status = 'completed'
        trip.save()
        login_cred = {'email': trip.user.email, 'password': '123password'}
        token = log_in(self, login_cred)
        data = {'rating': -2,
                'review': 'good'}
        data2 = {'rating': 11,
                 'review': 'good'}
        response = self.client.post(reverse('user_rates_driver', args=(trip.id,)), content_type='application/json',
                                    data=data, **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        response2 = self.client.post(reverse('user_rates_driver', args=(trip.id,)), content_type='application/json',
                                     data2=data2, **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response2.status_code, 400)


class CancelTripTest(TestCase):
    def setUp(self) -> None:
        create_trips(1)
        create_users(1)
        create_admin()
        create_driver(1)

    def test_admin_cancels_trip(self):
        trip = Trip.objects.all()[0]
        login_cred = {'email': 'admin@gmail.com', 'password': '123password'}
        token = log_in(self, login_cred)
        response = self.client.get(reverse('cancel_trip', args=(trip.id,)), content_type='application/json',
                                   **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)

    def test_driver_cancels_trip(self):
        trip = Trip.objects.all()[0]
        trip.driver = Driver.objects.all()[0]
        trip.save()
        login_cred = {'email': trip.driver.user.email, 'password': '123password'}
        token = log_in(self, login_cred)
        response = self.client.get(reverse('cancel_trip', args=(trip.id,)), content_type='application/json',
                                   **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)

    def test_user_cancels_trip(self):
        trip = Trip.objects.all()[0]
        login_cred = {'email': trip.user.email, 'password': '123password'}
        token = log_in(self, login_cred)
        response = self.client.get(reverse('cancel_trip', args=(trip.id,)), content_type='application/json',
                                   **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)

    def test_completed_trip_cant_be_changed(self):
        trip = Trip.objects.all()[0]
        trip.trip_status = 'completed'
        trip.save()
        login_cred = {'email': trip.user.email, 'password': '123password'}
        token = log_in(self, login_cred)
        response = self.client.get(reverse('cancel_trip', args=(trip.id,)), content_type='application/json',
                                   **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, 403)

    def test_trip_cant_be_cancelled_if_user_not_trip_user_or_driver_or_admin(self):
        trip = Trip.objects.all()[0]
        trip.trip_status = 'completed'
        trip.save()
        user = create_users(1)[0]
        login_cred = {'email': user.email, 'password': '123password'}
        token = log_in(self, login_cred)
        response = self.client.get(reverse('cancel_trip', args=(trip.id,)), content_type='application/json',
                                   **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, 403)


class ViewsTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        img = Image.new('RGB', (250, 250))
        image = img.tobytes()
        self.user = CustomUser.objects.create_user(
            email="test@gmail.com", password="test1234")
        self.driver = Driver.objects.create(user=self.user, national_insurance="34523874", is_condemned_prior=True,
                                            is_occupied=False,
                                            is_verified=True, status="Verified", driving_license_back_image=image,
                                            driving_license_front_image=image)
        self.driver.save()
        self.user.save()
        
    def test_user_login(self, email="test@gmail.com", password="test1234"):
        client = Client()
        response = client.post(
            reverse('login'), {'email': email, 'password': password})

        self.assertEqual(response.status_code, 200)

    def test_user_details_view(self):
        client = Client()
        response = client.get(reverse('all_users'))

        self.assertEqual(response.status_code, 200)

    def test_driver_detail_view(self):
        client = Client()
        response = client.get(reverse('all_drivers'))

        self.assertEqual(response.status_code, 200)

    def test_individual_user_view(self):
        client = Client()

        res = client.post(reverse('login'), {
            'email': "test@gmail.com", 'password': "test1234"})
        token = json.loads(res.data['tokens'].replace("'", '"'))[
            'access'].strip()

        response = self.client.get(reverse('get_user'),
                                   content_type='application/json',
                                   **{'HTTP_AUTHORIZATION': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)

    def test_logout_view(self):
        client = Client()

        res = client.post(reverse('login'), {
            'email': "test@gmail.com", 'password': "test1234"})
        refresh_token = json.loads(res.data['tokens'].replace("'", '"'))[
            'refresh'].strip()
        access_token = json.loads(res.data['tokens'].replace("'", '"'))[
            'access'].strip()
        data = json.dumps(
            {
                "refresh": refresh_token,
            }
        )
        response = self.client.post(reverse('logout'), data, content_type='application/json', **{
            'HTTP_AUTHORIZATION': f'Bearer {access_token}'})
        self.assertEqual(response.status_code, 200)

    def test_create_driver_view(self):
        client = Client()
        imagefile = SimpleUploadedFile('accounts/tests/images/1.jpeg', b''),

        data = {
            "first_name": "test",
            "last_name": "test",
            "email": "test@email.com",
            "phone": "afsan@12345",
            "address": "test address",
            "password": "tesafsr35423rweasdasrewet534q2542t1234",
            "driving_license_front_image": imagefile,
            "driving_license_back_image": imagefile,
            "national_insurance": "34523874",
            "is_condemned_prior": False,
            "gender": "Male",
        }
        headers = {'content_type': 'multipart/form-data'}
        response = client.post(reverse('create_driver'),
                               data=data, headers=headers)
        self.assertEqual(response.status_code, 201)

    def test_driver_object_cant_be_created_with_invalid_data_input(self):
        client = Client()
        imagefile = SimpleUploadedFile('accounts/tests/images/1.jpeg', b''),

        data = {
            "first_name": "test",
            "last_name": "test",
            "email": "testemail.com",
            "phone": "afsan@12345",
            "address": "test address",
            "password": "tesafsr35423rweasdasrewet534q2542t1234",
            "driving_license_front_image": imagefile,
            "driving_license_back_image": imagefile,
            "national_insurance": "34523874",
            "is_condemned_prior": False,
            "gender": "Male",
        }
        headers = {'content_type': 'multipart/form-data'}
        response = client.post(reverse('create_driver'),
                               data=data, headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_vehicle_api_view(self):
        client = Client()
        res = client.post(reverse('login'), {
            'email': "test@gmail.com", 'password': "test1234"})
        owner = CustomUser.objects.get(email="test@gmail.com")
        refresh_token = json.loads(res.data['tokens'].replace("'", '"'))[
            'refresh'].strip()
        access_token = json.loads(res.data['tokens'].replace("'", '"'))[
            'access'].strip()

        imagefile = SimpleUploadedFile('accounts/tests/images/2.jpeg', b''),

        data = {
            "year": "2020",
            "brand": "test",
            "owner": owner,
            "Class": "test",
            "fitness": imagefile,
            "plate_no": "5645654",
            "has_child_seat": False,
            "maximum_passengers": 4,
            "maximum_luggage": 3,
            "driven_mileage": 412454,
            "is_refurbished": True,
            "papers": imagefile,
            "papers": imagefile,
            "paper_name": "test",
            "paper_name": "test",
        }
        # headers={'content_type':'multipart/form-data',
        #          'Authorization': f'Bearer {access_token}'}
        # response = client.post(reverse('register_vehicle'), json=data, headers=headers)
        response = self.client.post(reverse('register_vehicle'), data=data,
                                    format="multipart", **{'HTTP_AUTHORIZATION': f'Bearer {access_token}'})
        self.assertEqual(response.status_code, 201)

    def test_validate_token(self):
        client = Client()
        data = {
            "email": "talktoafsan@gmail.com",
            "first_name": "Afsan",
            "last_name": "Saeed",
            "phone": "01756755575",
            "address": "Dhaka",
            "password": "afsan@12345"

        }
        headers = {'content_type': 'multipart/form-data'}
        response = client.post(reverse('signup'), data=data, headers=headers)
        user_data = models.UserData(id=response.data['id'])
        token = models.UserToken.objects.get(user_data=user_data)
        data2 = {
            "id": response.data['id'],
            "token": token
        }
        response = client.post(reverse('validate_token'),
                               data=data2, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_reset_password_api_view(self):
        client = Client()

        res = client.post(reverse('login'), {
            'email': "test@gmail.com", 'password': "test1234"})
        refresh_token = json.loads(res.data['tokens'].replace("'", '"'))[
            'refresh'].strip()
        access_token = json.loads(res.data['tokens'].replace("'", '"'))[
            'access'].strip()
        data = {
            "email": "test@gmail.com"
        }
        headers = {'content_type': 'multipart/form-data'}
        response = client.post(reverse('password_reset'), data=data, headers=headers)
        user = models.CustomUser.objects.get(email="test@gmail.com")
        token = models.UserOTP.objects.get(user_data=user)
        data2 = {
            "email": "test@gmail.com",
            "otp": token.otp,
        }
        response1 = client.post(reverse('password_reset_validation'), data=data2, headers=headers)

        data3 = {
            "email": "test@gmail.com"
        }
        response3 = client.post(reverse('password_resend'), data=data3, headers=headers)

        data4 = {
            "email": "test@gmail.com",
            "password": "test1234",
        }
        response4 = client.post(reverse('password_reset_confirm'), data=data4, headers=headers)
        if response4.status_code == 200:
            user = models.CustomUser.objects.get(email="test@gmail.com")
            user.set_password("test1234")
            user.save()
            self.assertEqual(response4.status_code, 200)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response3.status_code, 200)

    def test_email_if_user_exists(self):
        client = Client()
        data = {
            "email": "test@gmail.com"
        }
        headers = {'content_type': 'multipart/form-data'}
        response = client.post(reverse('check_email'), data=data, headers=headers)
        self.assertEqual(response.status_code, 200)
