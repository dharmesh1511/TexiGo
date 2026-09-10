from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .models import Booking , Review

class CustomUserCreationForm(UserCreationForm):

    email = forms.EmailField(required=True)

    profile_image = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'profile_image',
            'password1',
            'password2',
        ]

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )



class BookingForm(forms.ModelForm):

    class Meta:
        model = Booking

        fields = [
            'pickup_location',
            'drop_location',
            'distance',
        ]

        widgets = {
            'pickup_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Pickup Location'
            }),

            'drop_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Drop Location'
            }),

            'distance': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Distance in KM'
            }),
        }


from django import forms
from .models import User

class UserEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            "username",
        ]

        widgets = {
            "username": forms.TextInput(attrs={
                "class":"form-control"
            }),
        }


from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):

    class Meta:
        model = Contact
        fields = "__all__"

        widgets = {
            "full_name": forms.TextInput(attrs={
                "class":"form-control mb-3",
                "placeholder":"Full Name"
            }),

            "email": forms.EmailInput(attrs={
                "class":"form-control mb-3",
                "placeholder":"Email Address"
            }),

            "subject": forms.TextInput(attrs={
                "class":"form-control mb-3",
                "placeholder":"Subject"
            }),

            "message": forms.Textarea(attrs={
                "class":"form-control mb-3",
                "rows":5,
                "placeholder":"Message"
            }),
        }

class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review

        fields = ["rating", "comment"]

        widgets = {
            "rating": forms.Select(
                choices=[
                    (1, "⭐ 1 Star"),
                    (2, "⭐⭐ 2 Stars"),
                    (3, "⭐⭐⭐ 3 Stars"),
                    (4, "⭐⭐⭐⭐ 4 Stars"),
                    (5, "⭐⭐⭐⭐⭐ 5 Stars"),
                ],
                attrs={
                    "class": "form-select"
                }
            ),

            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Write your experience..."
                }
            ),
        }