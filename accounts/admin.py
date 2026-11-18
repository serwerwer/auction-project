from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


# Register the custom User model in Django Admin
# Reuse Django's built-in user management interface
@admin.register(User)
class CustomUserAdmin(UserAdmin):

    # Define the fields displayed when editing an existing user
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal information",
            {"fields": ("first_name", "last_name")},
        ),
        (
            "Verification",
            {"fields": ("email_verified",)},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            "Important dates",
            {"fields": ("last_login", "date_joined")},
        ),
    )

    # Prevent admin to manualy change the verification status of user's email
    readonly_fields = ("email_verified",)

    # Define the fields displayed when creating a new user
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "usable_password",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    # Choose which columns appear in the user list
    list_display = (
        "email",
        "first_name",
        "last_name",
        "email_verified",
        "is_staff",
        "is_active",
    )

    # Allow filtering and searching user accounts
    list_filter = ("is_staff", "is_active", "email_verified")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("last_name",)
