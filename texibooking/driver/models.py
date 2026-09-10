from django.db import models
from user.models import User


class Driver(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    address = models.TextField()
    license_number = models.CharField(max_length=100)
    
    profile_image = models.ImageField(
        upload_to='driver/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.full_name
    
class Vehicle(models.Model):

    driver = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        related_name="vehicles"
    )

    company_name = models.CharField(max_length=100)
    car_model = models.CharField(max_length=100)
    vehicle_number = models.CharField(max_length=30, unique=True)
    vehicle_color = models.CharField(max_length=30)
    seating_capacity = models.PositiveIntegerField()

    registration_number = models.CharField(max_length=100)
    insurance_number = models.CharField(max_length=100)

    price_per_km = models.DecimalField(
            max_digits=6,
            decimal_places=2,
            default=10.00
        )

    car_image = models.ImageField(
        upload_to='vehicle/',
        blank=True,
        null=True)

    def __str__(self):
        return self.vehicle_number