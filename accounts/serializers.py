from django.contrib import auth
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


from .models import Driver, Vehicle, Paper, DriverData, UserData, Trip, Child, Stops, Rating,FevoriteDriverModel


User = get_user_model()


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['id'] = user.id
        token['email'] = user.email
        token['types'] = user.types
        token['address'] = user.address
        token['phone'] = user.phone

        return token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", 'phone', 'address', 'rating']


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=5)
    password = serializers.CharField(max_length=68, min_length=4, write_only=True)
    user_id = serializers.IntegerField(read_only=True)
    tokens = serializers.CharField(max_length=255, min_length=5, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'user_id', 'tokens']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        user = auth.authenticate(email=email, password=password)
        if user:
            return {
                'email': user.email,
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'tokens': user.tokens,
            }
        else:
            raise AuthenticationFailed('Invalid credentials, try again')
        return super().validate(attrs)


class LogoutSerializer(serializers.ModelSerializer):
    refresh = serializers.CharField()
    default_error_messages = {
        'bad_token': 'Token is expired or invalid'
    }

    class Meta:
        model = User
        fields = ['refresh']

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except Exception:
            self.fail('bad_token')


class DriverSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    total_earned = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_occupied = serializers.BooleanField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    rating = serializers.IntegerField(max_value=10, min_value=0, read_only=True)
    trips = serializers.IntegerField(read_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Driver
        fields = ['id', 'driving_license_front_image', 'driving_license_back_image', 'national_insurance',
                  'is_condemned_prior', 'total_earned', 'is_occupied', 'is_verified', 'rating',
                  'trips', 'first_name', 'last_name', 'status', 'gender'
                  ]


class PaperSerializer(serializers.ModelSerializer):
    vehicle = serializers.CharField(source='vehicle.id', read_only=True)

    class Meta:
        model = Paper
        fields = ['vehicle', 'paper_name', 'paper']


class VehicleSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.user.email')

    class Meta:
        model = Vehicle
        fields = ["id", "owner", "year", 'brand', 'Class', 'fitness', 'plate_no', 'has_child_seat',
                  'maximum_passengers', 'maximum_luggage', 'driven_mileage', 'is_refurbished']


class VehicleDetailsSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.user.email')
    papers = PaperSerializer(many=True, read_only=True, source='paper_set')

    class Meta:
        model = Vehicle
        fields = ["id", "owner", "year", 'brand', 'Class', 'fitness', 'plate_no', 'has_child_seat',
                  'maximum_passengers', 'maximum_luggage', 'driven_mileage', 'is_refurbished', 'papers']


class DriverDataSerializer(serializers.ModelSerializer):
    user_data = serializers.ReadOnlyField(source='user_data.id')

    class Meta:
        model = DriverData
        fields = ['driving_license_front_image', 'driving_license_back_image',
                  'national_insurance', 'is_condemned_prior',
                  'user_data'
                  ]


class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = '__all__'


class TripRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ['pickup_location', 'drop_off_location', 'pickup_time', 'date', 'hours', 'number_of_passengers',
                  'luggage_weight', 'luggage_amount', 'is_child_seat', 'vehicle_type']

class EditTripsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = '__all__'


class StopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stops
        fields = ['location']


class ChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = ['age']


class RatingSerializer(serializers.ModelSerializer):
    rating_from = serializers.ReadOnlyField(source='rating_from.first_name')
    rated_to = serializers.ReadOnlyField(source='rated_to.first_name')
    trip = serializers.ReadOnlyField(source='trip.id')

    class Meta:
        model = Rating
        fields = '__all__'
class FevoriteDriverSerializer(serializers.ModelSerializer):
    first_name = serializers.ReadOnlyField(source='driver.user.first_name')
    last_name = serializers.ReadOnlyField(source='driver.user.last_name')
    email = serializers.ReadOnlyField(source='driver.user.email')
    phone = serializers.ReadOnlyField(source='driver.user.phone')
    location = serializers.ReadOnlyField(source="driver.driver_location")
    gender = serializers.ReadOnlyField(source="driver.gender")

    class Meta:
        model = FevoriteDriverModel
        fields = ['first_name', 'last_name', 'email','gender', 'phone', 'location']