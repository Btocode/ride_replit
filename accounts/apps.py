from django.apps import AppConfig
from django.db.models.signals import post_save


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        from .models import UserData, Rating
        from .signals import send_email_verification_token, update_rating_info
        post_save.connect(send_email_verification_token, sender=UserData, dispatch_uid='email_verification')
        post_save.connect(update_rating_info, sender=Rating, dispatch_uid='update rating')

