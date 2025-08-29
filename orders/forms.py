from django import forms


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=100, label="Full name",
                                widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(label="Email",
                             widget=forms.EmailInput(attrs={"class": "form-control"}))
    phone_number = forms.CharField(max_length=20, required=False, label="Phone",
                                   widget=forms.TextInput(attrs={"class": "form-control"}))
    street = forms.CharField(max_length=120, label="Street",
                                    widget=forms.TextInput(attrs={"class": "form-control"}))
    house_number = forms.CharField(max_length=10, required=False, label="House Number",
                                    widget=forms.TextInput(attrs={"class": "form-control"}))
    city = forms.CharField(max_length=80, label="City",
                           widget=forms.TextInput(attrs={"class": "form-control"}))
    postal_code = forms.CharField(max_length=20, label="Postal code / PLZ",
                                  widget=forms.TextInput(attrs={"class": "form-control"}))
    country = forms.CharField(max_length=60, initial="Germany", label="Country",
                              widget=forms.TextInput(attrs={"class": "form-control"}))
