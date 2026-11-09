from django import forms


class BidForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=9,
        decimal_places=2,
    )
