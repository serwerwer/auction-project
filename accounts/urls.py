from django.urls import path

from .views import account_profile, pseudonym_settings

urlpatterns = [
    path(
        "profile/",
        account_profile,
        name="account_profile",
    ),
    path(
        "pseudonym/",
        pseudonym_settings,
        name="pseudonym_settings",
    ),
]
