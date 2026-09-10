from django import forms
from user.models import User
from driver.models import Driver


class AdminLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )



class UserForm(forms.ModelForm):

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Password"
        })
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]

        widgets = {
            "username": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Username"
            }),

            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Email Address"
            }),
        }

from driver.models import Driver

class DriverForm(forms.ModelForm):

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Username"
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Email"
        })
    )

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Password"
        })
    )

    class Meta:
        model = Driver
        fields = [
            "full_name",
            "mobile",
            "address",
            "license_number",
        ]

        widgets = {
            "full_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Full Name"
            }),

            "mobile": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Mobile Number"
            }),

            "address": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Address"
            }),

            "license_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "License Number"
            }),

            
        }

from driver.models import Vehicle

class VehicleForm(forms.ModelForm):

    class Meta:
        model = Vehicle

        exclude = ["driver"]

        widgets = {

            "vehicle_name": forms.TextInput(attrs={
                "class":"form-control"
            }),

            "vehicle_number": forms.TextInput(attrs={
                "class":"form-control"
            }),

            "vehicle_type": forms.TextInput(attrs={
                "class":"form-control"
            }),

            "vehicle_model": forms.TextInput(attrs={
                "class":"form-control"
            }),

            "vehicle_color": forms.TextInput(attrs={
                "class":"form-control"
            }),

            "seating_capacity": forms.NumberInput(attrs={
                "class":"form-control"
            }),

            "registration_number": forms.TextInput(attrs={
                "class":"form-control"
            }),

            "insurance_number": forms.TextInput(attrs={
                "class":"form-control"
            }),

             "car_image": forms.ClearableFileInput(attrs={
                "class":"form-control"
            }),
        }