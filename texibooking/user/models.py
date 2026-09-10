from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):

    ROLE_CHOICES = (
        ('user', 'User'),
        ('driver', 'Driver'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user'
    )

    profile_image = models.ImageField(
        upload_to='profile/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.username


class Booking(models.Model):

    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Arrived", "Arrived"),
        ("Started", "Started"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
        ("Rejected", "Rejected"),
    )


    user = models.ForeignKey(
        "user.User",
        on_delete=models.CASCADE
    )


    vehicle = models.ForeignKey(
        "driver.Vehicle",
        on_delete=models.CASCADE
    )


    pickup_location = models.CharField(
        max_length=255
    )


    drop_location = models.CharField(
        max_length=255
    )


    distance = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )


    price_per_km = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=20
    )


    total_fare = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    pickup_lat = models.FloatField(null=True, blank=True)

    pickup_lng = models.FloatField(null=True, blank=True)


    drop_lat = models.FloatField(null=True, blank=True)

    drop_lng = models.FloatField(null=True, blank=True)

    booking_datetime = models.DateTimeField(
        auto_now_add=True
    )


    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    ride_otp = models.CharField(max_length=6, blank=True, null=True)
    otp_verified = models.BooleanField(default=False)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    arrived_at = models.DateTimeField(blank=True, null=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    final_fare = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)


    def __str__(self):
        return f"{self.user.username} - {self.vehicle.company_name}"
    

class Payment(models.Model):

    STATUS = (

    ("Pending","Pending"),

    ("Paid","Paid"),

    ("Failed","Failed"),

)

    PAYMENT_METHOD_CHOICES = (
        ("Razorpay", "Razorpay"),
        ("Cash", "Cash"),
    )

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default="Razorpay"
    )

    razorpay_order_id = models.CharField(max_length=200, blank=True, null=True)

    razorpay_payment_id = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    razorpay_signature = models.CharField(
        max_length=300,
        blank=True,
        null=True
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="Pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.booking.id} - {self.status}"


from django.db import models

class Contact(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

from driver.models import Driver

class Review(models.Model):
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="review"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    driver = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    rating = models.PositiveSmallIntegerField(
    validators=[
        MinValueValidator(1),
        MaxValueValidator(5)
    ]
)

    comment = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.rating}⭐"