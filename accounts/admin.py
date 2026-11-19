from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Pseudonym, User


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
        "is_staff",
        "is_active",
    )

    # Allow filtering and searching user accounts
    list_filter = ("is_staff", "is_active")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("last_name",)


@admin.register(Pseudonym)
class PseudonymAdmin(admin.ModelAdmin):
    list_display = ("name", "assigned_to", "accepted_at")
    search_fields = ("name",)
    readonly_fields = ("assigned_to", "accepted_at")
    actions = None

    def get_readonly_fields(self, request, obj=None):
        # Lock accepted pseudonyms in the admin form
        if obj and obj.accepted_at:
            return ("name", "assigned_to", "accepted_at")

        return ("assigned_to", "accepted_at")

    def has_delete_permission(self, request, obj=None):
        # Prevent deliting of accepted pseudonyms through admin
        if obj and obj.accepted_at:
            return False

        return super().has_delete_permission(request, obj)
