from django import forms


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
