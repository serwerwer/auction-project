from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models

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

    @property
    def public_bidder_name(self):
        # show the accepted pseudonym when available
        pseudonym = getattr(self, "auction_pseudonym", None)

        if pseudonym and pseudonym.accepted_at:
            return pseudonym.name

        # otherwise, show the real name of the user
        full_name = f"{self.first_name} {self.last_name}".strip()

        return full_name or "Uczestnik"

# Store predefined pseudonyms that users can randomly draw
class Pseudonym(models.Model):
    # Store unique names, so the same pseudonym cannot exist twice
    name = models.CharField(max_length=50, unique=True)

    # Connect an accepted pseudonym to one user only
    # Keep the pseudonym reserved even if the user account is deleted
    assigned_to = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="auction_pseudonym",
    )

    # Store when the user permanently accepted the pseudonym
    # Empty value means the pseudonym has not been accepted yet
    accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
    )

    # Display the pseudonym instead of the deafault ID
    def __str__(self):
        return self.name