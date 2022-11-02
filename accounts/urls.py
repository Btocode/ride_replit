from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView
)
from .import views
from .views import (RegisterUserAPIView, IndividualUserDetailAPI, MyTokenObtainPairView,
                    LoginAPIView, LogOutAPIView, UserDetailAPI, DriverDetailAPI,
                    VehicleAPIView, DriversVehicle, ValidateToken, ResendToken, ResetPasswordAPIView,
                    ValidateResetPasswordOTP, ResendOTP, ChangePassword, CheckEmailIfExists, CreateDriver,
                    CreateTripRequestAPIView,FevoriteDriverApiView, FindRiderApiView, CreateStaticTripRequestAPIView)

urlpatterns = [

    # User/Driver Registration + blocking
    path('v1/signup/', RegisterUserAPIView.as_view(), name='signup'),
    path('v1/driver/signup/', CreateDriver.as_view(), name='create_driver'),
    path('v1/login/', LoginAPIView.as_view(), name='login'),
    path('v1/logout/', LogOutAPIView.as_view(), name='logout'),
    path("v1/validate-token/", ValidateToken.as_view(), name="validate_token"),
    path("v1/resend-token/", ResendToken.as_view(), name="validate_token"),
    path('v1/toggle-block-status/<uuid:id>/', views.ToggleBlockedStatus.as_view(), name="toggle_block_status"),
    
    # Registering vehicle for Drivers
    path("v1/register-vehicle/", VehicleAPIView.as_view(), name="register_vehicle"),

    # General Queries to Database for users and drivers
    path('v1/all-users/', UserDetailAPI.as_view(), name="all_users"),
    path("v1/all-drivers/", DriverDetailAPI.as_view(), name="all_drivers"),
    path('v1/drivers-vehicle/<uuid:id>/', DriversVehicle.as_view(), name="drivers_vehicle"),
    path("v1/check-email/", CheckEmailIfExists.as_view(), name="check_email"),


    # Login JWT token ie. access, refresh token and verify token
    path('v1/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('v1/token/getuser/', IndividualUserDetailAPI.as_view(), name = 'get_user'),
    
    # Password Reset / Forget Password
    path('v1/password-reset/', ResetPasswordAPIView.as_view(), name='password_reset'),
    path('v1/password-reset/resend/', ResendOTP.as_view(), name='password_resend'),
    path('v1/password-reset/validate/', ValidateResetPasswordOTP.as_view(), name='password_reset_validation'),
    path("v1/password-reset/confirm/", ChangePassword.as_view(), name="password_reset_confirm"),
    
    # Trip Request releted APIs
    path("v1/user/trip-request/", CreateTripRequestAPIView.as_view(), name="trip_request"),
    path("v1/user/trip-request/static", CreateStaticTripRequestAPIView.as_view(), name="static_trip_request"),
    
    path("v1/update-trip/<uuid:id>/", views.EditTrips.as_view(), name='edit_trips'),
    path("v1/update-trip-view/<uuid:id>/", views.UpdateTripAPIView.as_view(), name='update_trips'),
    path("v1/update-child/<int:pk>/", views.EditChildData.as_view(), name='edit_child_info'),
    path("v1/edit-stops/<int:pk>/", views.EditStops.as_view(), name='edit_stops'),
    path("v1/cancel-trip/<uuid:trip_id>/", views.CancelTrip.as_view(), name='cancel_trip'),
    # ratings
    path('v1/user-rates-driver/<uuid:trip_id>/', views.UserRatesDriver.as_view(), name='user_rates_driver'),
    path('v1/driver-rates-user/<uuid:trip_id>/', views.DriverRatesUser.as_view(), name='driver_rates_user'),
    path('v1/getfevorites/', FevoriteDriverApiView.as_view(), name='get_fevorites'),
    path('v1/find-rider/', FindRiderApiView.as_view(), name='find_rider'),
]
