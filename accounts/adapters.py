from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured

from allauth.account.adapter import DefaultAccountAdapter


# Connect allauth phone authentication with our custom User model
class AccountAdapter(DefaultAccountAdapter):

    # Read the phone number and verification status from the user
    def get_phone(self, user):
        if not user.phone_number:
            return None

        return user.phone_number, user.phone_verified

    # Save the phone number and its verification status
    def set_phone(self, user, phone, verified):
        user.phone_number = phone
        user.phone_verified = verified
        user.save(update_fields=["phone_number", "phone_verified"])

    # Mark the phone as verified after a correct SMS code
    def set_phone_verified(self, user, phone):
        if user.phone_number != phone:
            raise ValueError("Phone number does not match")

        user.phone_verified = True
        user.save(update_fields=["phone_verified"])

    # Find an existing user by their phone number
    def get_user_by_phone(self, phone):
        User = get_user_model()
        return User.objects.filter(phone_number=phone).first()

    # Print SMS verification codes in terminal during local development only
    # since we do not have a real SMS provider yet
    def send_verification_code_sms(self, user, phone, code, **kwargs):
        if not settings.DEBUG:
            raise ImproperlyConfigured(
                "Configure an SMS provider before production"
            )

        print(f"[DEV SMS] Phone: {phone} | Code: {code}")
