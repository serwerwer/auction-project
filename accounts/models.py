from django.contrib.auth.models import AbstractUser
from django.db import models
from typing import ClassVar

from .managers import UserManager


# Represent both auction participants and administrators
# Reuse Django's built-in password and permission system
class User(AbstractUser):

    # Remove the default username field as users will authenticate using email, phone or Google
    # username is yet another variable to remember, and our app is supposed to be as easy to use for any user as possible
    username = None

    # Use email as the main identifier for Django authentication
    # Each email address can belong to only one account
    email = models.EmailField(unique=True)

    # Store the phone number for SMS authentication and notifications
    # Allow empty values during incomplete registration
    # Phone numbers should be normalized to E.164 format (example: +48512345678)
    phone_number = models.CharField(
        max_length=16,
        unique=True,
        null=True,
        blank=True,
    )

    # Track whether user's contact details have been verified
    # These fields must only change after successful verification
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)

    # Use email instead of username for Django authentication
    USERNAME_FIELD = "email"

    # Do not request additional fields when creating a superuser
    REQUIRED_FIELDS: ClassVar[list[str]] = []

    # Use our custom manager to create users without usernames
    # The manager defines how users and superusers are created
    objects = UserManager()

    # Display the email when representing a user as text
    def __str__(self):
        return self.email
