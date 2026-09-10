from django import forms
from django.contrib.auth.forms import UserCreationForm
from user.models import User
from .models import Vehicle
from .models import Driver

class DriverRegistrationForm(UserCreationForm):

    full_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )

    mobile = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    address = forms.CharField(
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 3
        })
    )

    license_number = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    # 👇 Profile Image
    profile_image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            "class": "form-control"
        })
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "full_name",
            "mobile",
            "address",
            "license_number",
            "profile_image",
            "password1",
            "password2",
        )

    def clean_password2(self):
        password = self.cleaned_data.get("password2")
        username = self.cleaned_data.get("username")

        if username and password and username.lower() in password.lower():
            raise forms.ValidationError(
                "Username aur Password same ya similar nahi hone chahiye."
            )

        return password

class DriverLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())


class VehicleForm(forms.ModelForm):

    class Meta:
        model = Vehicle

        fields = [
            "company_name",
            "car_model",
            "vehicle_number",
            "vehicle_color",
            "seating_capacity",
            "registration_number",
            "insurance_number",
            "price_per_km",      # 👈 New Field
            "car_image",
        ]

        widgets = {

            "company_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Company Name"
            }),

            "car_model": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Car Model"
            }),

            "vehicle_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Vehicle Number"
            }),

            "vehicle_color": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Vehicle Color"
            }),

            "seating_capacity": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Seating Capacity"
            }),

            "registration_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Registration Number"
            }),

            "insurance_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Insurance Number"
            }),

            "price_per_km": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Price Per KM",
                "step": "0.01",
                "min": "0"
            }),

            "car_image": forms.FileInput(attrs={
                "class": "form-control"
            }),

        }

class DriverEditForm(forms.ModelForm):

    class Meta:
        model = Driver
        fields = [
            "full_name",
            "address",
            "license_number",
        ]

        widgets = {

            "full_name": forms.TextInput(attrs={
                "class":"form-control"
            }),

            "address": forms.Textarea(attrs={
                "class":"form-control",
                "rows":3
            }),

            "license_number": forms.TextInput(attrs={
                "class":"form-control"
            }),

        }