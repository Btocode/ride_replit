import uuid

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.timezone import timedelta

from rest_framework_simplejwt.tokens import RefreshToken

from .managers import CustomUserManager


class UserData(models.Model):
    """
    Temporary model for holding data for user model.
    """
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    email = models.EmailField()
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    password = models.CharField(_("password"), max_length=128)

    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        return super().save(*args, **kwargs)


class DriverData(models.Model):
    """
    Temporary model for holding data for Driver Model.
    """
    user_data = models.OneToOneField(UserData, on_delete=models.CASCADE)
    driving_license_front_image = models.BinaryField()
    driving_license_back_image = models.BinaryField()
    national_insurance = models.CharField(max_length=50)
    is_condemned_prior = models.BooleanField()
    gender = models.CharField(max_length=15)


class CustomUser(AbstractUser):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    username = None
    email = models.EmailField(_('email address'), unique=True)

    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    sum_of_ratings = models.FloatField(default=0)
    number_of_ratings = models.FloatField(default=0)
    blacklisted = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('first_name', 'last_name', 'phone', 'address')
    # REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    @property
    def rating(self):
        try:
            return self.sum_of_ratings / self.number_of_ratings
        except ZeroDivisionError:
            return 0


class UserToken(models.Model):
    user_data = models.ForeignKey(UserData, on_delete=models.CASCADE)
    token = models.CharField(max_length=4, blank=True, null=True)
    creation_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token

    @property
    def is_valid(self):
        """
        checks token validity
        """
        token_life_time = 5
        return self.creation_time + timedelta(minutes=token_life_time) > timezone.now()


class UserOTP(models.Model):
    user_data = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp = models.CharField(max_length=4, blank=True, null=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return self.otp

    @property
    def is_valid(self):
        """
        checks tokens validity
        """
        otp_life_time = 5
        return self.creation_time + timedelta(minutes=otp_life_time) > timezone.now()


STATUS = (
    ('Not Verified', 'Not verified'),
    ('Pending', 'Pending'),
    ('Verified', 'Verified'),
)
GENDER = (
    ("Male", "Male"),
    ("Female", "Female"),
    ("Others", "Others")
)


class Driver(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gender = models.CharField(max_length=15, choices=GENDER, default="Male")
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    driving_license_front_image = models.BinaryField()
    driving_license_back_image = models.BinaryField()
    national_insurance = models.CharField(max_length=50)
    is_condemned_prior = models.BooleanField()
    total_earned = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    is_occupied = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    trips = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS, default='Not Verified')
    driver_location = models.CharField(max_length=100, blank=True, null=True)


AUTHORITIES = (
    ('superuser', 'Super User'),
    ('operator', 'Operator')
)


class Admin(models.Model):
    authority_level = models.CharField(max_length=30, choices=AUTHORITIES, default='operator')
    designation_name = models.CharField(max_length=50)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

VEHICLE_TYPE = (
    ('Lite', 'Lite'),
    ('Standard', 'Standard'),
    ('Premium', 'Premium'),
    ('Ubuntu', 'Ubuntu'),
    ('Squad', 'Squad'),
)


class Vehicle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(Driver, on_delete=models.CASCADE)
    year = models.CharField(max_length=30)
    brand = models.CharField(max_length=50)
    Class = models.CharField(max_length=30)
    fitness = models.BinaryField()
    plate_no = models.CharField(max_length=50)
    has_child_seat = models.BooleanField()
    maximum_passengers = models.IntegerField()
    maximum_luggage = models.IntegerField()
    driven_mileage = models.BigIntegerField()
    is_refurbished = models.BooleanField()
    vehicle_type = models.CharField(max_length=30, choices=VEHICLE_TYPE, default='Lite')



class Paper(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    paper_name = models.CharField(max_length=50)
    paper = models.BinaryField()


BOOKING_METHOD = (
    ('hourly', 'Hourly'),
    ('one way', 'One Way'),
    ('two way', 'Two Way')
)

TRIP_STATUS = (
    ('pending', 'Pending'),
    ('ongoing', 'Ongoing'),
    ('past cancelled', 'Past Cancelled'),
    ('completed', 'Completed'),
)
VEHICLE_TYPE = (
    ('Lite', 'Lite'),
    ('Standard', 'Standard'),
    ('Premium', 'Premium'),
    ('Ubuntu', 'Ubuntu'),
    ('Squad', 'Squad'),
)


class Trip(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, null=True, blank=True)
    assigned_vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, null=True, blank=True)
    trip_status = models.CharField(max_length=30, choices=TRIP_STATUS, default='pending')
    booking_method = models.CharField(max_length=30, choices=BOOKING_METHOD)
    hours = models.IntegerField(null=True, blank=True)
    pickup_location = models.CharField(max_length=250)
    pickup_time = models.TimeField()
    is_discounted = models.BooleanField(default=False)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    drop_off_location = models.CharField(max_length=250)
    number_of_passengers = models.IntegerField()
    luggage_weight = models.IntegerField(null=True, blank=True)
    luggage_amount = models.IntegerField(null=True, blank=True)
    luggage_size = models.CharField(max_length=100, null=True, blank=True)
    is_child_seat = models.BooleanField(default=False)
    payment_status = models.CharField(max_length=100)
    preferred_drivers_gender = models.CharField(max_length=15, choices=GENDER, null=True, blank=True)
    cancelled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='cancelled_by')
    vehicle_type = models.CharField(max_length=100, choices=VEHICLE_TYPE, default='Lite')
    has_fevorite_driver = models.BooleanField(default=False)
    choose_random_driver = models.BooleanField(default=False)


class Rating(models.Model):
    rating_from = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    rated_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='rated')
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    review = models.TextField(blank=True)


class Child(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    age = models.IntegerField()


class Stops(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    location = models.CharField(max_length=250)


class DriverIsVerified(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_ni_verified = models.BooleanField(default=False)
    is_condemnation_verified = models.BooleanField(default=False)
    is_license_verified = models.BooleanField(default=False)
    is_vehicle_verified = models.BooleanField(default=False)
    is_payment_verified = models.BooleanField(default=False)


class UserIsVerified(models.Model):
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)


class FevoriteDriverModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)