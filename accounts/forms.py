from django import forms
from django.contrib.auth import get_user_model

# Add first and last name fields to user registration
class CustomSignupForm(forms.Form):
    first_name = forms.CharField(
        label="Imię",
        max_length=50,
        required=True,
        strip=True,
    )

    last_name = forms.CharField(
        label="Nazwisko",
        max_length=50,
        required=True,
        strip=True,
    )

    # Saving additional fields to our custom User model
    # allauth handles email, password and email verification
    def signup(self, request, user):
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save(update_fields=["first_name", "last_name"])

# Use our custom User model
User = get_user_model()


# Allow users to edit their first and last name
# Email and pseudonym are managed separately
class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]

        labels = {
            "first_name": "Imię",
            "last_name": "Nazwisko",
        }

    # Require both names when updating the profile
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True