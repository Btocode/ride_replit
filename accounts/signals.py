from django.core.mail import send_mail
from . import otp
from django.conf import settings
from .models import UserToken


def send_email_verification_token(sender, instance, created, **kwargs):
    """
    Sends verification email to user mail address everytime new user is created
    """
    if created:
        token = otp.generateOTP()
        UserToken.objects.create(user_data=instance, token=token)
        send_mail(
            # title:
            "You are one step behind of becoming a registered driver",
            # message:
            "Your Registration token is: " + token,
            # from:
            settings.EMAIL_HOST_USER,
            # to:
            [instance.email]
        )


def update_rating_info(sender, instance, created, **kwargs):
    """
    Updates rating information in user model everytime new rating is added.
    """
    if created:
        user = instance.rated_to
        user.sum_of_ratings += instance.rating
        user.number_of_ratings += 1
        user.save()
