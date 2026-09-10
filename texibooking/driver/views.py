from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings

from .forms import DriverEditForm
from django.contrib.auth import update_session_auth_hash


from .forms import DriverRegistrationForm, DriverLoginForm
from .models import Driver

from .models import Driver, Vehicle
from .forms import VehicleForm
from django.shortcuts import get_object_or_404
from user.models import Booking
import random
from django.contrib.auth import get_user_model

from django.db.models import Sum
from django.utils import timezone
from user.models import Payment
from .models import Driver


from django.db.models import Sum

def driver_register(request):

    if request.method == "POST":

        form = DriverRegistrationForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            # ==================================
            # 1. Create User
            # ==================================

            user = form.save(commit=False)

            user.email = form.cleaned_data["email"]
            user.role = "driver"

            if request.FILES.get("profile_image"):
                user.profile_image = request.FILES["profile_image"]

            user.save()

            # ==================================
            # 2. Create Driver Profile
            # ==================================

            Driver.objects.create(
                user=user,
                full_name=form.cleaned_data["full_name"],
                mobile=form.cleaned_data["mobile"],
                address=form.cleaned_data["address"],
                license_number=form.cleaned_data["license_number"],
            )

            # ==================================
            # 3. Generate OTP
            # ==================================

            otp = random.randint(100000, 999999)

            # Store OTP in session
            request.session["driver_signup_otp"] = str(otp)
            request.session["driver_signup_user_id"] = user.id

            # ==================================
            # 4. Send ONE Email
            # ==================================

            send_mail(
                subject="Welcome to Taxi Booking System - Verify Your Driver Account",

                message=f"""
Hello {user.username},

Congratulations!

Your Driver account has been created successfully.

Driver Details:
-------------------------
Username : {user.username}
Email    : {user.email}
Role     : Driver
-------------------------

To activate and verify your Driver account, please use the OTP below:

Your Verification OTP:
{otp}

This OTP is valid for 5 minutes.

Please do not share this OTP with anyone.

After successful verification, you will be able to access the Driver Panel.

Thank you for joining Taxi Booking System.

Regards,
Taxi Booking Team
""",

                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            # ==================================
            # 5. Success Message
            # ==================================

            messages.success(
                request,
                "Registration successful! Verification OTP has been sent to your email."
            )

            # ==================================
            # 6. Redirect to Driver OTP Page
            # ==================================

            return redirect("driver_verify_otp")

        else:
            print(form.errors)

    else:
        form = DriverRegistrationForm()

    return render(
        request,
        "driver/register.html",
        {"form": form}
    )

def driver_login(request):
    return redirect("login")


User = get_user_model()
def driver_verify_otp(request):
    if request.method == "POST":

        entered_otp = request.POST.get("otp", "").strip()

        saved_otp = request.session.get("driver_signup_otp")
        user_id = request.session.get("driver_signup_user_id")

        if not saved_otp or not user_id:
            messages.error(
                request,
                "OTP expired or session data not found. Please register again."
            )
            return redirect("driver_register")

        if entered_otp == str(saved_otp):

            try:
                user = User.objects.get(
                    id=user_id,
                    role="driver"
                )

                # Login driver
                login(request, user)

                # Clear OTP session
                request.session.pop("driver_signup_otp", None)
                request.session.pop("driver_signup_user_id", None)

                # Make sure session is saved
                request.session.modified = True

                messages.success(
                    request,
                    f"Welcome {user.username}! Driver account verified successfully."
                )

                return redirect("driver_dashboard")

            except User.DoesNotExist:

                messages.error(
                    request,
                    "Driver account not found."
                )

                return redirect("driver_register")

        else:

            messages.error(
                request,
                "Invalid OTP. Please enter the correct OTP."

            )

    return render(
        request,
        "driver/verify_otp.html"
    )

def driver_home(request):
    return render(request, "driver/home.html")


def driver_logout(request):
    logout(request)
    return redirect("driver_login")


@login_required(login_url="driver_login")
def driver_dashboard(request):

    driver = Driver.objects.get(user=request.user)

    total_vehicles = Vehicle.objects.filter(
        driver=driver
    ).count()

    pending_bookings = Booking.objects.filter(
        vehicle__driver=driver,
        status="Pending"
    ).count()

    completed_rides = Booking.objects.filter(
        vehicle__driver=driver,
        status="Completed"
    ).count()

    total_earnings = Booking.objects.filter(
        vehicle__driver=driver,
        status="Completed"
    ).aggregate(
        total=Sum("total_fare")
    )["total"] or 0

    recent_bookings = Booking.objects.filter(
        vehicle__driver=driver
    ).order_by("-booking_datetime")[:5]

    context = {
        "total_vehicles": total_vehicles,
        "pending_bookings": pending_bookings,
        "completed_rides": completed_rides,
        "total_earnings": total_earnings,
        "recent_bookings": recent_bookings,
    }

    return render(
        request,
        "driver/dashboard.html",
        context
    )


@login_required(login_url="driver_login")
def driver_profile(request):

    driver = Driver.objects.get(user=request.user)

    return render(request,"driver/profile.html",{
        "driver":driver
    })

@login_required
def edit_profile(request):

    driver = Driver.objects.get(user=request.user)

    if request.method == "POST":

        form = DriverEditForm(
            request.POST,
            instance=driver
        )

        if form.is_valid():

            # Username
            request.user.username = request.POST.get("username")

            # Profile Image
            if request.FILES.get("profile_image"):
                driver.profile_image = request.FILES.get("profile_image")

            # Password
            password = request.POST.get("password")

            if password != "":
                request.user.set_password(password)

            request.user.save()
            driver.save()
            form.save()

            if password != "":
                update_session_auth_hash(request, request.user)

            messages.success(request,"Profile Updated Successfully")

            return redirect("driver_profile")

    else:

        form = DriverEditForm(instance=driver)

    return render(request,"driver/edit_profile.html",{
        "form":form,
        "driver":driver
    })

@login_required(login_url="driver_login")
def vehicle_add(request):

    driver = Driver.objects.get(user=request.user)

    if request.method == "POST":

        form = VehicleForm(request.POST, request.FILES)

        if form.is_valid():

            vehicle = form.save(commit=False)

            vehicle.driver = driver

            vehicle.save()

            messages.success(request, "Vehicle Added Successfully")

            return redirect("driver_vehicle_list")

    else:

        form = VehicleForm()

    return render(request, "driver/vehicle_form.html", {
        "form": form
    })

@login_required(login_url="driver_login")
def vehicle_list(request):

    driver = Driver.objects.get(user=request.user)

    vehicles = Vehicle.objects.filter(driver=driver)

    return render(request, "driver/vehicle_list.html", {
        "vehicles": vehicles
    })

@login_required(login_url="driver_login")
def vehicle_edit(request, id):

    driver = Driver.objects.get(user=request.user)

    vehicle = get_object_or_404(
        Vehicle,
        id=id,
        driver=driver
    )

    if request.method == "POST":

        form = VehicleForm(
            request.POST,
            request.FILES,
            instance=vehicle
        )

        if form.is_valid():

            form.save()

            messages.success(request, "Vehicle Updated Successfully")

            return redirect("driver_vehicle_list")

    else:

        form = VehicleForm(instance=vehicle)

    return render(request, "driver/vehicle_form.html", {
        "form": form
    })

@login_required(login_url="driver_login")
def vehicle_delete(request, id):

    driver = Driver.objects.get(user=request.user)

    vehicle = get_object_or_404(
        Vehicle,
        id=id,
        driver=driver
    )

    vehicle.delete()

    messages.success(request, "Vehicle Deleted Successfully")

    return redirect("driver_vehicle_list")


@login_required(login_url="driver_login")
def booking_requests(request):

    driver = Driver.objects.get(user=request.user)

    bookings = Booking.objects.filter(
        vehicle__driver=driver
    ).order_by("-id")

    return render(
        request,
        "driver/booking_requests.html",
        {
            "bookings": bookings
        }
    )


@login_required(login_url="driver_login")
def driver_active_ride(request):

    driver = Driver.objects.get(user=request.user)

    # 1. Ongoing active ride for driver (Confirmed, Arrived, Started)
    active_booking = Booking.objects.filter(
        vehicle__driver=driver,
        status__in=["Confirmed", "Arrived", "Started"]
    ).order_by("-id").first()

    # 2. If no ongoing ride, check for latest Completed ride
    if not active_booking:
        active_booking = Booking.objects.filter(
            vehicle__driver=driver,
            status="Completed"
        ).order_by("-id").first()

    return render(
        request,
        "driver/active_ride.html",
        {
            "booking": active_booking
        }
    )


@login_required(login_url="driver_login")
def accept_booking(request, id):

    driver = Driver.objects.get(user=request.user)

    booking = get_object_or_404(
        Booking,
        id=id,
        vehicle__driver=driver
    )

    booking.status = "Confirmed"
    booking.save()

    messages.success(
        request,
        "Booking Accepted Successfully! Switched to Active Ride view."
    )

    return redirect("driver_active_ride")


@login_required(login_url="driver_login")
def reject_booking(request, id):

    driver = Driver.objects.get(user=request.user)

    booking = get_object_or_404(
        Booking,
        id=id,
        vehicle__driver=driver
    )

    booking.status = "Rejected"
    booking.save()

    messages.success(
        request,
        "Booking Rejected Successfully."
    )

    return redirect("booking_requests")


@login_required(login_url="driver_login")
def driver_arrived(request, id):

    driver = Driver.objects.get(user=request.user)

    booking = get_object_or_404(
        Booking,
        id=id,
        vehicle__driver=driver
    )

    if booking.status in ["Confirmed", "Pending"]:
        booking.status = "Arrived"
        booking.arrived_at = timezone.now()

        # Generate 4-digit Ride OTP
        otp = f"{random.randint(1000, 9999)}"
        booking.ride_otp = otp
        booking.otp_created_at = timezone.now()
        booking.otp_verified = False
        booking.save()

        # Send Ride OTP to customer email
        if booking.user and booking.user.email:
            send_mail(
                subject="🚖 TaxiGo Ride OTP - Driver Has Arrived",
                message=f"""
Dear {booking.user.username},

Your driver has arrived at your pickup location ({booking.pickup_location}).

Your TaxiGo Ride OTP is:

        {otp}

Please share this 4-digit OTP with your driver to start your ride.

Vehicle Details:
{booking.vehicle.company_name} {booking.vehicle.car_model} ({booking.vehicle.vehicle_number})

Have a safe journey!

TaxiGo Team
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.user.email],
                fail_silently=True,
            )

        messages.success(
            request,
            f"Marked as Arrived. 4-digit Ride OTP has been sent to customer ({booking.user.username})."
        )
    else:
        messages.warning(request, f"Cannot mark arrived for ride in status '{booking.status}'.")

    return redirect(request.META.get('HTTP_REFERER') or "driver_active_ride")


@login_required(login_url="driver_login")
def verify_ride_otp(request, id):

    driver = Driver.objects.get(user=request.user)

    booking = get_object_or_404(
        Booking,
        id=id,
        vehicle__driver=driver
    )

    if request.method == "POST":
        entered_otp = request.POST.get("ride_otp", "").strip()

        if booking.ride_otp and entered_otp == str(booking.ride_otp):
            booking.otp_verified = True
            booking.save()
            messages.success(request, "Ride OTP Verified Successfully! You can now start the ride.")
        else:
            booking.otp_verified = False
            booking.save()
            messages.error(request, "Invalid Ride OTP. Please ask customer for the correct OTP.")

    return redirect(request.META.get('HTTP_REFERER') or "driver_active_ride")


@login_required(login_url="driver_login")
def start_ride(request, id):

    driver = Driver.objects.get(user=request.user)

    booking = get_object_or_404(
        Booking,
        id=id,
        vehicle__driver=driver
    )

    if booking.status == "Arrived" and booking.otp_verified:
        booking.status = "Started"
        booking.started_at = timezone.now()
        booking.save()
        messages.success(request, "Ride Started! Have a safe journey.")
    elif not booking.otp_verified:
        messages.error(request, "Cannot start ride. Ride OTP must be verified first.")
    else:
        messages.warning(request, f"Cannot start ride in status '{booking.status}'.")

    return redirect(request.META.get('HTTP_REFERER') or "driver_active_ride")


@login_required(login_url="driver_login")
def complete_booking(request, id):

    driver = Driver.objects.get(user=request.user)

    booking = get_object_or_404(
        Booking,
        id=id,
        vehicle__driver=driver
    )

    if booking.status == "Started":
        booking.status = "Completed"
        booking.completed_at = timezone.now()

        # Calculate final fare server-side
        calculated_fare = float(booking.distance) * float(booking.price_per_km)
        booking.final_fare = round(calculated_fare, 2)
        booking.total_fare = booking.final_fare
        booking.save()

        messages.success(request, f"Ride Completed Successfully! Final Fare: ₹{booking.final_fare}")
    elif booking.status == "Completed":
        messages.info(request, "Ride is already marked as completed.")
    else:
        messages.error(request, f"Cannot complete ride from status '{booking.status}'.")

    return redirect(request.META.get('HTTP_REFERER') or "driver_active_ride")


@login_required(login_url="driver_login")
def confirm_cash_payment(request, id):

    driver = Driver.objects.get(user=request.user)

    booking = get_object_or_404(
        Booking,
        id=id,
        vehicle__driver=driver
    )

    if booking.status == "Completed":
        payment, created = Payment.objects.get_or_create(
            booking=booking,
            defaults={
                "amount": booking.final_fare or booking.total_fare,
                "payment_method": "Cash",
                "status": "Paid"
            }
        )
        payment.payment_method = "Cash"
        payment.status = "Paid"
        payment.save()
        messages.success(request, "Cash payment collected and confirmed.")
    else:
        messages.error(request, "Payment can only be confirmed for completed rides.")

    return redirect(request.META.get('HTTP_REFERER') or "driver_active_ride")


@login_required(login_url="driver_login")
def ride_history(request):

    driver = Driver.objects.get(user=request.user)

    completed_rides = Booking.objects.filter(
        vehicle__driver=driver,
        status="Completed"
    ).order_by("-booking_datetime")

    context = {
        "completed_rides": completed_rides,
        "total_completed": completed_rides.count(),
    }

    return render(request, "driver/ride_history.html", context)


@login_required(login_url="driver_login")
def earnings(request):

    driver = Driver.objects.get(user=request.user)

    payments = Payment.objects.filter(

        booking__vehicle__driver=driver,

        status="Paid"

    ).order_by("-created_at")

    total_earning = payments.aggregate(
        total=Sum("amount")
    )["total"] or 0

    today = timezone.now().date()

    today_earning = payments.filter(

        created_at__date=today

    ).aggregate(

        total=Sum("amount")

    )["total"] or 0

    month = timezone.now().month
    year = timezone.now().year

    month_earning = payments.filter(

        created_at__month=month,
        created_at__year=year

    ).aggregate(

        total=Sum("amount")

    )["total"] or 0

    return render(

        request,

        "driver/earnings.html",

        {

            "payments":payments,

            "total_earning":total_earning,

            "today_earning":today_earning,

            "month_earning":month_earning,

        }

    )

from user.models import Review

@login_required(login_url="driver_login")
def my_reviews(request):

    driver = request.user.driver

    reviews = Review.objects.filter(driver=driver)

    return render(request, "driver/my_reviews.html", {
        "reviews": reviews
    })

User = get_user_model()
def driver_forgot_password(request):

    if request.method == "POST":

        email = request.POST.get("email", "").strip()

        if not email:

            messages.error(
                request,
                "Please enter your email address."
            )

            return render(
                request,
                "driver/forgot_password.html"
            )

        try:

            # Find only Driver users
            user = User.objects.get(
                email__iexact=email,
                role="driver"
            )

        except User.DoesNotExist:

            messages.error(
                request,
                "No driver account found with this email address."
            )

            return render(
                request,
                "driver/forgot_password.html"
            )

        except User.MultipleObjectsReturned:

            messages.error(
                request,
                "Multiple driver accounts are using this email. Please contact admin."
            )

            return render(
                request,
                "driver/forgot_password.html"
            )

        # ==================================
        # Generate OTP
        # ==================================

        otp = random.randint(100000, 999999)

        # Store Driver Forgot Password OTP
        request.session["driver_forgot_password_otp"] = str(otp)

        request.session["driver_forgot_password_user_id"] = user.id

        # ==================================
        # Send OTP Email
        # ==================================

        send_mail(
            subject="Driver Password Reset OTP - TaxiGo",

            message=f"""
Hello {user.username},

We received a request to reset your TaxiGo Driver account password.

Driver Account:
-------------------------
Username : {user.username}
Email    : {user.email}
-------------------------

Your Password Reset OTP is:

{otp}

This OTP is valid for 5 minutes.

Please do not share this OTP with anyone.

If you did not request a password reset, you can safely ignore this email.

Regards,
TaxiGo Team
""",

            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        messages.success(
            request,
            "Password reset OTP has been sent to your email."
        )

        return redirect(
            "driver_forgot_password_otp"
        )

    return render(
        request,
        "driver/forgot_password.html"
    )

def driver_forgot_password_otp(request):

    if request.method == "POST":

        entered_otp = request.POST.get(
            "otp",
            ""
        ).strip()

        saved_otp = request.session.get(
            "driver_forgot_password_otp"
        )

        user_id = request.session.get(
            "driver_forgot_password_user_id"
        )

        print(
            "DRIVER FORGOT PASSWORD OTP:",
            entered_otp
        )

        print(
            "SAVED DRIVER OTP:",
            saved_otp
        )

        print(
            "DRIVER USER ID:",
            user_id
        )

        if not saved_otp or not user_id:

            messages.error(
                request,
                "OTP expired or invalid. Please request a new OTP."
            )

            return redirect(
                "driver_forgot_password"
            )

        if entered_otp == str(saved_otp):

            # OTP verified
            request.session[
                "driver_forgot_password_verified"
            ] = True

            # Remove OTP after successful verification
            request.session.pop(
                "driver_forgot_password_otp",
                None
            )

            messages.success(
                request,
                "OTP verified successfully. Please create your new password."
            )

            return redirect(
                "driver_reset_password"
            )

        else:

            messages.error(
                request,
                "Invalid OTP. Please try again."
            )

    return render(
        request,
        "driver/forgot_password_otp.html"
    )

def driver_reset_password(request):

    verified = request.session.get(
        "driver_forgot_password_verified"
    )

    user_id = request.session.get(
        "driver_forgot_password_user_id"
    )

    if not verified or not user_id:

        messages.error(
            request,
            "Please verify the OTP first."
        )

        return redirect(
            "driver_forgot_password"
        )

    try:

        user = User.objects.get(
            id=user_id,
            role="driver"
        )

    except User.DoesNotExist:

        messages.error(
            request,
            "Driver account not found."
        )

        return redirect(
            "driver_forgot_password"
        )

    if request.method == "POST":

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        # Empty fields
        if not password or not confirm_password:

            messages.error(
                request,
                "Please enter both password fields."
            )

            return render(
                request,
                "driver/reset_password.html"
            )

        # Password match
        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return render(
                request,
                "driver/reset_password.html"
            )

        # Minimum password length
        if len(password) < 8:

            messages.error(
                request,
                "Password must be at least 8 characters long."
            )

            return render(
                request,
                "driver/reset_password.html"
            )

        # Secure password update
        user.set_password(password)
        user.save()

        # Clear session
        request.session.pop(
            "driver_forgot_password_user_id",
            None
        )

        request.session.pop(
            "driver_forgot_password_verified",
            None
        )

        messages.success(
            request,
            "Password changed successfully. You can now login with your new password."
        )

        return redirect(
            "driver_login"
        )

    return render(
        request,
        "driver/reset_password.html"
    )