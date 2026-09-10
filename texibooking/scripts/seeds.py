import os
import sys
import random
from decimal import Decimal
from django.utils import timezone

# Configure stdout encoding for Windows compatibility
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Setup Django environment
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'texibooking.settings')

import django
django.setup()

from user.models import User, Booking, Payment, Contact, Review
from driver.models import Driver, Vehicle


def seed_database():
    print("[*] Starting database seeding for TaxiGo...\n")

    # 1. Seed Superuser / Admin
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@gmail.com',
            'first_name': 'Admin',
            'last_name': 'System',
            'is_staff': True,
            'is_superuser': True,
            'role': 'user'
        }
    )
    if created:
        admin_user.set_password('admin')
        admin_user.save()
        print("[+] Admin created: admin (Password: admin)")
    else:
        print("[-] Admin 'admin' already exists.")

    # 2. Seed Customers / Normal Users
    users_data = [
        {"username": "rahul_sharma", "email": "rahul@gmail.com", "first_name": "Rahul", "last_name": "Sharma"},
        {"username": "priya_patel", "email": "priya@gmail.com", "first_name": "Priya", "last_name": "Patel"},
        {"username": "amit_kumar", "email": "amit@gmail.com", "first_name": "Amit", "last_name": "Kumar"},
        {"username": "neha_singh", "email": "neha@gmail.com", "first_name": "Neha", "last_name": "Singh"},
        {"username": "vikram_verma", "email": "vikram@gmail.com", "first_name": "Vikram", "last_name": "Verma"},
    ]

    seeded_users = []
    for udata in users_data:
        user, created = User.objects.get_or_create(
            username=udata["username"],
            defaults={
                "email": udata["email"],
                "first_name": udata["first_name"],
                "last_name": udata["last_name"],
                "role": "user"
            }
        )
        if created:
            user.set_password("User@123")
            user.save()
            print(f"[+] User created: {user.username} (Password: User@123)")
        else:
            print(f"[-] User '{user.username}' already exists.")
        seeded_users.append(user)

    # 3. Seed Drivers & Driver Profiles
    drivers_data = [
        {
            "username": "driver_ramesh",
            "email": "ramesh@driver.com",
            "full_name": "Ramesh Kumar",
            "mobile": "9876543210",
            "address": "SG Highway, Ahmedabad, Gujarat",
            "license_number": "GJ0120201234567"
        },
        {
            "username": "driver_suresh",
            "email": "suresh@driver.com",
            "full_name": "Suresh Yadav",
            "mobile": "9876543211",
            "address": "Connaught Place, New Delhi",
            "license_number": "DL0220197654321"
        },
        {
            "username": "driver_rajesh",
            "email": "rajesh@driver.com",
            "full_name": "Rajesh Patel",
            "mobile": "9876543212",
            "address": "Andheri West, Mumbai, Maharashtra",
            "license_number": "MH0120181122334"
        },
        {
            "username": "driver_vijay",
            "email": "vijay@driver.com",
            "full_name": "Vijay Singh",
            "mobile": "9876543213",
            "address": "Indiranagar, Bengaluru, Karnataka",
            "license_number": "KA0320219988776"
        },
        {
            "username": "driver_anil",
            "email": "anil@driver.com",
            "full_name": "Anil Sharma",
            "mobile": "9876543214",
            "address": "Bani Park, Jaipur, Rajasthan",
            "license_number": "RJ1420224455667"
        },
    ]

    seeded_drivers = []
    for ddata in drivers_data:
        driver_user, created = User.objects.get_or_create(
            username=ddata["username"],
            defaults={
                "email": ddata["email"],
                "first_name": ddata["full_name"].split()[0],
                "last_name": ddata["full_name"].split()[-1],
                "role": "driver"
            }
        )
        if created:
            driver_user.set_password("Driver@123")
            driver_user.save()

        driver_profile, p_created = Driver.objects.get_or_create(
            user=driver_user,
            defaults={
                "full_name": ddata["full_name"],
                "mobile": ddata["mobile"],
                "address": ddata["address"],
                "license_number": ddata["license_number"]
            }
        )
        if p_created:
            print(f"[+] Driver created: {driver_profile.full_name} (Password: Driver@123)")
        else:
            print(f"[-] Driver '{driver_profile.full_name}' profile already exists.")
        seeded_drivers.append(driver_profile)

    # 4. Seed Vehicles
    vehicles_data = [
        {
            "driver": seeded_drivers[0],
            "company_name": "Maruti Suzuki",
            "car_model": "Swift Dzire",
            "vehicle_number": "GJ01AB1234",
            "vehicle_color": "White",
            "seating_capacity": 4,
            "registration_number": "REG-GJ-1001",
            "insurance_number": "INS-GJ-9001",
            "price_per_km": Decimal("15.00")
        },
        {
            "driver": seeded_drivers[1],
            "company_name": "Hyundai",
            "car_model": "Aura",
            "vehicle_number": "DL02CD5678",
            "vehicle_color": "Silver",
            "seating_capacity": 4,
            "registration_number": "REG-DL-1002",
            "insurance_number": "INS-DL-9002",
            "price_per_km": Decimal("16.00")
        },
        {
            "driver": seeded_drivers[2],
            "company_name": "Toyota",
            "car_model": "Innova Crysta",
            "vehicle_number": "MH01EF9012",
            "vehicle_color": "Black",
            "seating_capacity": 7,
            "registration_number": "REG-MH-1003",
            "insurance_number": "INS-MH-9003",
            "price_per_km": Decimal("25.00")
        },
        {
            "driver": seeded_drivers[3],
            "company_name": "Tata",
            "car_model": "Nexon EV",
            "vehicle_number": "KA03GH3456",
            "vehicle_color": "Blue",
            "seating_capacity": 5,
            "registration_number": "REG-KA-1004",
            "insurance_number": "INS-KA-9004",
            "price_per_km": Decimal("18.00")
        },
        {
            "driver": seeded_drivers[4],
            "company_name": "Honda",
            "car_model": "City",
            "vehicle_number": "RJ14JK7890",
            "vehicle_color": "Red",
            "seating_capacity": 4,
            "registration_number": "REG-RJ-1005",
            "insurance_number": "INS-RJ-9005",
            "price_per_km": Decimal("20.00")
        },
    ]

    seeded_vehicles = []
    for vdata in vehicles_data:
        vehicle, created = Vehicle.objects.get_or_create(
            vehicle_number=vdata["vehicle_number"],
            defaults=vdata
        )
        if created:
            print(f"[+] Vehicle registered: {vehicle.company_name} {vehicle.car_model} ({vehicle.vehicle_number})")
        else:
            print(f"[-] Vehicle '{vehicle.vehicle_number}' already exists.")
        seeded_vehicles.append(vehicle)

    # 5. Seed Bookings & Payments & Reviews
    sample_locations = [
        {
            "pickup": "Iscon Mega Mall, SG Highway, Ahmedabad",
            "drop": "Ahmedabad Railway Station, Kalupur",
            "pickup_lat": 23.0298, "pickup_lng": 72.5074,
            "drop_lat": 23.0300, "drop_lng": 72.6012,
            "distance": Decimal("12.50")
        },
        {
            "pickup": "Connaught Place, New Delhi",
            "drop": "Indira Gandhi International Airport, Delhi",
            "pickup_lat": 28.6315, "pickup_lng": 77.2167,
            "drop_lat": 28.5562, "drop_lng": 77.1000,
            "distance": Decimal("18.20")
        },
        {
            "pickup": "Bandra Kurla Complex (BKC), Mumbai",
            "drop": "Chhatrapati Shivaji Maharaj Terminus (CSMT), Mumbai",
            "pickup_lat": 19.0674, "pickup_lng": 72.8685,
            "drop_lat": 18.9401, "drop_lng": 72.8347,
            "distance": Decimal("16.80")
        },
        {
            "pickup": "MG Road, Bengaluru",
            "drop": "Electronic City Phase 1, Bengaluru",
            "pickup_lat": 12.9716, "pickup_lng": 77.5946,
            "drop_lat": 12.8399, "drop_lng": 77.6770,
            "distance": Decimal("21.00")
        },
        {
            "pickup": "Hawa Mahal, Jaipur",
            "drop": "Jaipur International Airport, Sanganer",
            "pickup_lat": 26.9239, "pickup_lng": 75.8267,
            "drop_lat": 26.8289, "drop_lng": 75.8056,
            "distance": Decimal("13.40")
        }
    ]

    statuses = ["Completed", "Completed", "Started", "Confirmed", "Pending"]

    for i in range(5):
        user = seeded_users[i % len(seeded_users)]
        vehicle = seeded_vehicles[i % len(seeded_vehicles)]
        loc = sample_locations[i % len(sample_locations)]
        status = statuses[i]

        price_per_km = vehicle.price_per_km
        total_fare = (loc["distance"] * price_per_km).quantize(Decimal("0.01"))
        ride_otp = str(random.randint(100000, 999999))

        booking, b_created = Booking.objects.get_or_create(
            user=user,
            vehicle=vehicle,
            pickup_location=loc["pickup"],
            drop_location=loc["drop"],
            defaults={
                "distance": loc["distance"],
                "price_per_km": price_per_km,
                "total_fare": total_fare,
                "final_fare": total_fare if status == "Completed" else None,
                "pickup_lat": loc["pickup_lat"],
                "pickup_lng": loc["pickup_lng"],
                "drop_lat": loc["drop_lat"],
                "drop_lng": loc["drop_lng"],
                "status": status,
                "ride_otp": ride_otp,
                "otp_verified": status in ["Started", "Completed"],
                "started_at": timezone.now() if status in ["Started", "Completed"] else None,
                "completed_at": timezone.now() if status == "Completed" else None,
            }
        )

        if b_created:
            print(f"[+] Booking created: ID #{booking.id} - {user.username} with {vehicle.company_name} ({status})")

            # Seed Payment for Booking
            payment_status = "Paid" if status == "Completed" else ("Pending" if status != "Cancelled" else "Failed")
            payment_method = "Razorpay" if i % 2 == 0 else "Cash"
            
            Payment.objects.create(
                booking=booking,
                payment_method=payment_method,
                amount=total_fare,
                status=payment_status,
                razorpay_order_id=f"order_{random.randint(100000,999999)}" if payment_method == "Razorpay" else None,
                razorpay_payment_id=f"pay_{random.randint(100000,999999)}" if payment_status == "Paid" and payment_method == "Razorpay" else None,
            )
            print(f"  └─ Payment added ({payment_method} - {payment_status})")

            # Seed Review if completed
            if status == "Completed":
                Review.objects.create(
                    booking=booking,
                    user=user,
                    driver=vehicle.driver,
                    rating=random.choice([4, 5]),
                    comment=f"Great ride experience with {vehicle.driver.full_name}! Very punctual and smooth driving."
                )
                print(f"  └─ Review added for driver {vehicle.driver.full_name}")

    # 6. Seed Contact Messages
    contacts = [
        {
            "full_name": "Rohan Shah",
            "email": "rohan@example.com",
            "subject": "Inquiry about outstation rides",
            "message": "Do you provide outstation cab services from Ahmedabad to Udaipur?"
        },
        {
            "full_name": "Meera Joshi",
            "email": "meera@example.com",
            "subject": "Lost & Found Query",
            "message": "I forgot my sunglasses in the vehicle yesterday. Can you connect me with the driver?"
        }
    ]

    for cdata in contacts:
        contact, c_created = Contact.objects.get_or_create(
            email=cdata["email"],
            subject=cdata["subject"],
            defaults=cdata
        )
        if c_created:
            print(f"[+] Contact message seeded from {contact.full_name}")

    print("\n[+] Database seeding completed successfully!")


if __name__ == "__main__":
    seed_database()
