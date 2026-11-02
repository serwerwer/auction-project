from django.contrib.auth.base_user import BaseUserManager


# Define how regular users and superusers are created
# Replace the default manager that expects a username
class UserManager(BaseUserManager):

    # Create a regular user identified by their email
    def create_user(self, email, password=None, **extra_fields):

        # Require an email address for every new account
        if not email:
            raise ValueError("An email address is required.")

        # Normalize the email before saving it
        email = self.normalize_email(email.strip()).lower()

        # Create a user object with the provided information
        user = self.model(email=email, **extra_fields)

        # Hash the password before storing it
        user.set_password(password)

        # Save the user in database
        user.save(using=self._db)

        return user

    # Create an administrator with full permissions
    # Used by the createsuperuser management command
    def create_superuser(self, email, password=None, **extra_fields):

        # Enable staff access and superuser permissions
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        # Reject accounts without the required permissions
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        # Reuse the regular user creation method
        return self.create_user(email, password, **extra_fields)
