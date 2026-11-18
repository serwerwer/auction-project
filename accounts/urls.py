
from django.urls import path

from .views import pseudonym_settings

urlpatterns = [
    path(
        "pseudonym/",
        pseudonym_settings,
        name="pseudonym_settings",
    ),
]