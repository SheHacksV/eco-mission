from django import forms


class RouteForm(forms.Form):
    departure_postcode = forms.CharField(
        label='From',
        max_length=50,
        required=True,
        widget=forms.TextInput(
            attrs={'placeholder': 'Valid postcode required.'})
    )
    destination_postcode = forms.CharField(
        label='To',
        max_length=50,
        required=True,
        widget=forms.TextInput(
            attrs={'placeholder': 'Valid postcode required.'})
    )

