from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin


from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import Driver, Vehicle, Paper, UserToken, UserData, DriverData, UserOTP, Trip, Child, Stops, \
    Rating, Admin, FevoriteDriverModel

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    model = User

    list_display = ('id', 'email','blacklisted', 'is_active',
                    'is_staff', 'is_superuser', 'last_login',)
    list_filter = ('is_active', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('email', 'password', 'first_name', 'last_name', 'phone', 'address')}),
        ('Permissions', {'fields': ('is_staff', 'is_active',
                                    'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'date_joined')})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
            'email', 'password1', 'password2', 'first_name', 'last_name', 'phone', 'address', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)


admin.site.register(User, CustomUserAdmin)


@admin.register(Driver)
class DriverInfoAdmin(admin.ModelAdmin):
    list_display = ("user","id","driving_license_front_image", "driving_license_back_image")


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("brand", "Class", "id")


admin.site.register(Paper)
admin.site.register(UserToken)
admin.site.register(UserData)
admin.site.register(DriverData)
admin.site.register(UserOTP)
admin.site.register(Trip)
admin.site.register(Child)
admin.site.register(Stops)
admin.site.register(Rating)
admin.site.register(Admin)
admin.site.register(FevoriteDriverModel)

