from django.shortcuts import render, redirect ,get_object_or_404
from .forms import ContactForm, ReviewForm

from django.contrib import messages
from django.contrib.auth import authenticate,login,logout, get_user_model
from .forms import CustomUserCreationForm,LoginForm
from django.contrib.auth.decorators import login_required
from driver.models import Vehicle
from .forms import BookingForm
from .models import Booking ,Review
import requests
from django.conf import settings
from django.core.mail import send_mail
import random

from django.contrib.auth import update_session_auth_hash
from .forms import UserEditForm

import razorpay
from .models import Payment

import requests
from django.http import JsonResponse, HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io

def signup_view(request):

    if request.method == "POST":

        form = CustomUserCreationForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            # ==============================
            # 1. Create User
            # ==============================

            user = form.save()

            # ==============================
            # 2. Generate OTP
            # ==============================

            otp = random.randint(100000, 999999)

            # Store OTP in session
            request.session["signup_otp"] = str(otp)
            request.session["signup_user_id"] = user.id

            # ==============================
            # 3. Send ONE Email
            # ==============================

            send_mail(
                subject="Welcome to Taxi Booking System - Verify Your Account",

                message=f"""
Hello {user.username},

Congratulations!

Your Taxi Booking System account has been created successfully.

Account Details:
-------------------------
Username : {user.username}
Email    : {user.email}
-------------------------

To activate and verify your account, please use the OTP below:

Your Verification OTP:
{otp}

This OTP is valid for 5 minutes.

Please do not share this OTP with anyone.

After successful verification, you can login and book your cab.

Thank you for choosing Taxi Booking System.

Regards,
Taxi Booking Team
""",

                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            # ==============================
            # 4. Success Message
            # ==============================

            messages.success(
                request,
                "Registration successful! Verification OTP has been sent to your email."
            )

            # ==============================
            # 5. Redirect to OTP Verification
            # ==============================

            return redirect("verify_otp")

    else:

        form = CustomUserCreationForm()

    return render(
        request,
        "user/signup.html",
        {"form": form}
    )


User = get_user_model()
def verify_otp(request):

    if request.method == "POST":

        entered_otp = request.POST.get("otp")

        saved_otp = request.session.get("signup_otp")
        user_id = request.session.get("signup_user_id")

        if saved_otp and user_id:

            if entered_otp == saved_otp:

                # Get user from database
                user = User.objects.get(id=user_id)

                # Login user after OTP verification
                login(request, user)

                # Remove OTP from session
                del request.session["signup_otp"]
                del request.session["signup_user_id"]

                messages.success(
                    request,
                    "Account verified successfully!"
                )

                return redirect("profile")

            else:
                messages.error(
                    request,
                    "Invalid OTP. Please try again."
                )

        else:
            messages.error(
                request,
                "OTP expired or invalid. Please register again."
            )

    return render(
        request,
        "user/verify_otp.html"
    )


def login_view(request):

    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect("admin_dashboard")
        elif getattr(request.user, "role", "") == "driver" or hasattr(request.user, "driver"):
            return redirect("driver_dashboard")
        else:
            return redirect("home")

    if request.method == "POST":

        form = LoginForm(request.POST)

        if form.is_valid():

            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is not None:

                login(request, user)

                messages.success(
                    request,
                    "Login successful."
                )

                if user.is_staff or user.is_superuser:
                    return redirect("admin_dashboard")
                elif getattr(user, "role", "") == "driver" or hasattr(user, "driver"):
                    return redirect("driver_dashboard")
                else:
                    return redirect("home")

            else:
                messages.error(
                    request,
                    "Invalid Username or Password"
                )

    else:
        form = LoginForm()

    return render(
        request,
        "user/login.html",
        {"form": form}
    )

def logout_view(request):
    logout(request)
    messages.success(request, "Logout Successful")
    return redirect("login")

@login_required(login_url='login')
def profile(request):

    if request.user.role == "driver":
        return redirect("driver_profile")

    bookings = Booking.objects.filter(user=request.user)

    total_bookings = bookings.count()

    pending_bookings = bookings.filter(status="Pending").count()

    confirmed_bookings = bookings.filter(status="Confirmed").count()

    completed_bookings = bookings.filter(status="Completed").count()

    cancelled_bookings = bookings.filter(status="Cancelled").count()

    return render(request, "user/profile.html", {
        "total_bookings": total_bookings,
        "pending_bookings": pending_bookings,
        "confirmed_bookings": confirmed_bookings,
        "completed_bookings": completed_bookings,
        "cancelled_bookings": cancelled_bookings,
    })

@login_required
def edit_profiles(request):

    if request.method == "POST":

        form = UserEditForm(request.POST, instance=request.user)

        if form.is_valid():

            user = form.save(commit=False)

            if request.FILES.get("profile_image"):
                user.profile_image = request.FILES["profile_image"]

            password = request.POST.get("password")

            if password:
                user.set_password(password)

            user.save()

            if password:
                update_session_auth_hash(request, user)

            messages.success(request, "Profile Updated Successfully")

            return redirect("profile")

    else:

        form = UserEditForm(instance=request.user)

    return render(request, "user/edit_profile.html", {
        "form": form
    })

def home(request):

    vehicles = Vehicle.objects.all().order_by("-id")

    return render(request, "user/home.html", {
        "vehicles": vehicles
    })

def about(request):
    return render(request, "user/about.html")

def contact(request):
    return render(request, "user/contact.html")

@login_required(login_url='login')
def available_cars(request):

    vehicles = Vehicle.objects.all().order_by('-id')

    return render(request, 'user/available_cars.html', {
        'vehicles': vehicles
    })

def ride_detail(request, id):

    vehicle = get_object_or_404(Vehicle, id=id)

    return render(request, "user/ride_detail.html", {
        "vehicle": vehicle
    })


from django.core.mail import send_mail
from django.conf import settings

@login_required(login_url="login")
def book_cab(request, id):

    vehicle = get_object_or_404(Vehicle, id=id)

    if request.method == "POST":

        form = BookingForm(request.POST)

        if form.is_valid():

            booking = form.save(commit=False)

            booking.user = request.user
            booking.vehicle = vehicle

            distance = request.POST.get("distance", 0)

            booking.distance = distance
            booking.price_per_km = vehicle.price_per_km

            booking.total_fare = (
                float(distance) *
                float(vehicle.price_per_km)
            )

            booking.status = "Pending"

            booking.save()

            # ================= EMAIL =================

            send_mail(
                subject="🚖 TaxiGo Booking Confirmation",
                message=f"""
Dear {request.user.username},

Your cab booking has been received successfully.

----------------------------------------
Booking Details
----------------------------------------

Vehicle : {vehicle.company_name} {vehicle.car_model}
Vehicle Number : {vehicle.vehicle_number}

Pickup Location :
{booking.pickup_location}

Drop Location :
{booking.drop_location}

Distance : {booking.distance} KM

Fare : ₹{booking.total_fare}

Status : {booking.status}

Thank you for choosing TaxiGo.

Have a Safe Journey!

TaxiGo Team
                """,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[request.user.email],
                fail_silently=False,
            )

            # ==========================================

            messages.success(
                request,
                "Cab booked successfully! Your request is pending driver acceptance."
            )
            return redirect("my_bookings")

        else:
            print(form.errors)

    else:
        form = BookingForm()

    return render(
        request,
        "user/book_cab.html",
        {
            "form": form,
            "vehicle": vehicle
        }
    )


def search_location(request):

    query = request.GET.get("q")

    if not query:
        return JsonResponse([], safe=False)

    url = "https://nominatim.openstreetmap.org/search"

    headers = {
        "User-Agent": "TaxiGo/1.0"
    }

    params = {
        "q": query,
        "format": "json",
        "limit": 5,
        "countrycodes": "in"
    }

    response = requests.get(
        url,
        headers=headers,
        params=params
    )

    return JsonResponse(
        response.json(),
        safe=False
    )

@login_required(login_url="login")
def active_ride(request):

    # 1. Check for ongoing ride (Pending, Confirmed, Arrived, Started)
    active_booking = Booking.objects.filter(
        user=request.user,
        status__in=["Pending", "Confirmed", "Arrived", "Started"]
    ).order_by("-id").first()

    # 2. If no ongoing ride, check for latest Completed ride so user can Pay & Review on Active Ride page
    if not active_booking:
        active_booking = Booking.objects.filter(
            user=request.user,
            status="Completed"
        ).order_by("-id").first()

    order = None
    razorpay_key = None

    if active_booking and active_booking.status == "Completed":
        is_paid = hasattr(active_booking, 'payment') and active_booking.payment.status == "Paid"
        if not is_paid:
            try:
                client = razorpay.Client(
                    auth=(
                        settings.RAZORPAY_KEY_ID,
                        settings.RAZORPAY_KEY_SECRET
                    )
                )
                fare_amount = active_booking.final_fare or active_booking.total_fare
                amount = int(float(fare_amount) * 100)

                order = client.order.create({
                    "amount": amount,
                    "currency": "INR",
                    "payment_capture": 1
                })
                razorpay_key = settings.RAZORPAY_KEY_ID

                payment_obj, created = Payment.objects.get_or_create(
                    booking=active_booking,
                    defaults={
                        "razorpay_order_id": order["id"],
                        "amount": fare_amount,
                        "payment_method": "Razorpay",
                        "status": "Pending"
                    }
                )
                if not created:
                    payment_obj.razorpay_order_id = order["id"]
                    payment_obj.amount = fare_amount
                    payment_obj.payment_method = "Razorpay"
                    payment_obj.save()
            except Exception as e:
                print("Razorpay order creation error in active_ride:", e)

    return render(request, "user/active_ride.html", {
        "booking": active_booking,
        "order": order,
        "key": razorpay_key,
    })


@login_required(login_url="login")
def check_booking_status(request, id):
    booking = get_object_or_404(Booking, id=id, user=request.user)
    return JsonResponse({
        "id": booking.id,
        "status": booking.status,
        "is_paid": hasattr(booking, 'payment') and booking.payment.status == "Paid"
    })



@login_required(login_url="login")
def ride_history(request):

    bookings = Booking.objects.filter(
        user=request.user,
        status__in=["Completed", "Cancelled", "Rejected"]
    ).order_by("-id")

    return render(request, "user/ride_history.html", {
        "bookings": bookings
    })


@login_required(login_url="login")
def my_bookings(request):

    active_exists = Booking.objects.filter(
        user=request.user,
        status__in=["Pending", "Confirmed", "Arrived", "Started"]
    ).exists()

    if active_exists:
        return redirect("active_ride")
    return redirect("user_ride_history")



def get_real_distance(
    pickup_lng,
    pickup_lat,
    drop_lng,
    drop_lat
):

    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {

        "Authorization": settings.OPENROUTE_API_KEY

    }
    params = {

        "start": f"{pickup_lng},{pickup_lat}",

        "end": f"{drop_lng},{drop_lat}"

    }

    response = requests.get(
        url,
        headers=headers,
        params=params
    )

    data = response.json()

    meters = (
        data["features"][0]
        ["properties"]
        ["segments"][0]
        ["distance"]
    )

    return round(
        meters / 1000,
        2
    )

@login_required(login_url="login")
def cancel_booking(request, id):

    booking = get_object_or_404(
        Booking,
        id=id,
        user=request.user
    )

    if booking.status == "Pending" or booking.status == "Accepted" or booking.status == "Confirmed":

        booking.status = "Cancelled"
        booking.save()

        messages.success(
            request,
            "Ride cancelled successfully."
        )

    else:

        messages.error(
            request,
            "This ride cannot be cancelled."
        )

    return redirect("my_bookings")




@login_required
def payment(request, id):

    booking = get_object_or_404(
        Booking,
        id=id,
        user=request.user
    )

    if booking.status != "Completed":
        messages.error(
            request,
            "Payment can only be processed after the ride is completed."
        )
        return redirect("my_bookings")

    # Check if already paid
    if hasattr(booking, 'payment') and booking.payment.status == "Paid":
        messages.info(request, "Payment has already been completed for this ride.")
        return redirect("my_bookings")

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )

    fare_amount = booking.final_fare or booking.total_fare
    amount = int(float(fare_amount) * 100)

    order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    payment_obj, created = Payment.objects.get_or_create(
        booking=booking,
        defaults={
            "razorpay_order_id": order["id"],
            "amount": fare_amount,
            "payment_method": "Razorpay",
            "status": "Pending"
        }
    )
    if not created:
        payment_obj.razorpay_order_id = order["id"]
        payment_obj.amount = fare_amount
        payment_obj.payment_method = "Razorpay"
        payment_obj.save()

    return render(request,
                  "user/payment.html",
                  {
                      "booking": booking,
                      "order": order,
                      "key": settings.RAZORPAY_KEY_ID
                  })


@login_required(login_url="login")
def pay_cash(request, id):

    booking = get_object_or_404(
        Booking,
        id=id,
        user=request.user
    )

    if booking.status != "Completed":
        messages.error(request, "Payment can only be selected after ride completion.")
        return redirect("active_ride")

    fare_amount = booking.final_fare or booking.total_fare

    payment_obj, created = Payment.objects.get_or_create(
        booking=booking,
        defaults={
            "amount": fare_amount,
            "payment_method": "Cash",
            "status": "Pending"
        }
    )
    payment_obj.payment_method = "Cash"
    payment_obj.amount = fare_amount
    payment_obj.save()

    messages.success(
        request,
        "Cash payment method selected. Please pay cash to your driver upon arrival/completion."
    )
    return redirect("active_ride")


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
def payment_success(request):

    if request.method == "POST":

        order_id = request.POST.get("razorpay_order_id")
        payment_id = request.POST.get("razorpay_payment_id")
        signature = request.POST.get("razorpay_signature")

        payment = Payment.objects.get(
            razorpay_order_id=order_id
        )

        payment.razorpay_payment_id = payment_id
        payment.razorpay_signature = signature
        payment.payment_method = "Razorpay"
        payment.status = "Paid"
        payment.save()

        booking = payment.booking
        if booking.status != "Completed":
            booking.status = "Completed"
        booking.save()

        return JsonResponse({
            "status":"success"
        })

    return JsonResponse({
        "status":"failed"
    })


@login_required(login_url="login")
def download_invoice(request, id):

    booking = get_object_or_404(Booking, id=id)

    # Check permission
    is_owner = (booking.user == request.user)
    is_driver = hasattr(request.user, 'driver') and (booking.vehicle.driver == request.user.driver)

    if not is_owner and not is_driver:
        messages.error(request, "Unauthorized access to invoice.")
        return redirect("my_bookings")

    payment = getattr(booking, 'payment', None)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#16A34A'),
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'InvoiceSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#4B5563')
    )

    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#111827'),
        fontName='Helvetica-Bold',
        spaceAfter=6
    )

    normal_style = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1F2937')
    )

    bold_style = ParagraphStyle(
        'BoldText',
        parent=normal_style,
        fontName='Helvetica-Bold'
    )

    elements = []

    # Header section
    header_data = [
        [
            Paragraph("TaxiGo Invoice", title_style),
            Paragraph(f"<b>INVOICE #TB-{booking.id:05d}</b><br/>Date: {booking.booking_datetime.strftime('%d %b %Y')}", ParagraphStyle('HeaderRight', parent=normal_style, alignment=2))
        ],
        [
            Paragraph("Official Taxi Booking Receipt", subtitle_style),
            Paragraph(f"Ride Status: <b>{booking.status}</b>", ParagraphStyle('StatusRight', parent=normal_style, alignment=2))
        ]
    ]

    header_table = Table(header_data, colWidths=[270, 270])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 15))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E5E7EB'), spaceBefore=5, spaceAfter=15))

    # Details table (Customer & Driver info)
    driver_name = booking.vehicle.driver.full_name if hasattr(booking.vehicle, 'driver') else "Assigned Driver"
    driver_mobile = booking.vehicle.driver.mobile if hasattr(booking.vehicle, 'driver') else "N/A"

    details_data = [
        [
            Paragraph("CUSTOMER DETAILS", heading_style),
            Paragraph("DRIVER & VEHICLE", heading_style)
        ],
        [
            Paragraph(f"<b>Name:</b> {booking.user.username}<br/><b>Email:</b> {booking.user.email}", normal_style),
            Paragraph(f"<b>Driver:</b> {driver_name}<br/><b>Mobile:</b> {driver_mobile}<br/><b>Vehicle:</b> {booking.vehicle.company_name} {booking.vehicle.car_model}<br/><b>Number:</b> {booking.vehicle.vehicle_number}", normal_style)
        ]
    ]

    details_table = Table(details_data, colWidths=[270, 270])
    details_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F9FAFB')),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
    ]))
    elements.append(details_table)
    elements.append(Spacer(1, 15))

    # Route Journey details
    elements.append(Paragraph("RIDE DETAILS", heading_style))
    route_data = [
        [Paragraph("<b>Pickup Location:</b>", bold_style), Paragraph(booking.pickup_location, normal_style)],
        [Paragraph("<b>Drop Location:</b>", bold_style), Paragraph(booking.drop_location, normal_style)],
        [Paragraph("<b>Total Distance:</b>", bold_style), Paragraph(f"{booking.distance} KM", normal_style)],
        [Paragraph("<b>Rate Per KM:</b>", bold_style), Paragraph(f"₹{booking.price_per_km}", normal_style)],
    ]
    route_table = Table(route_data, colWidths=[130, 410])
    route_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#F3F4F6')),
    ]))
    elements.append(route_table)
    elements.append(Spacer(1, 15))

    # Payment Summary
    elements.append(Paragraph("PAYMENT SUMMARY", heading_style))

    pay_method = payment.payment_method if payment else "N/A"
    pay_status = payment.status if payment else "Pending"
    final_amt = booking.final_fare if booking.final_fare else booking.total_fare

    summary_data = [
        [Paragraph("<b>Description</b>", bold_style), Paragraph("<b>Amount</b>", ParagraphStyle('RightBold', parent=bold_style, alignment=2))],
        [Paragraph(f"Base Ride Fare ({booking.distance} KM @ ₹{booking.price_per_km}/KM)", normal_style), Paragraph(f"₹{final_amt}", ParagraphStyle('RightNorm', parent=normal_style, alignment=2))],
        [Paragraph("<b>Total Amount</b>", bold_style), Paragraph(f"<b>₹{final_amt}</b>", ParagraphStyle('RightBold', parent=bold_style, alignment=2))],
        [Paragraph(f"<b>Payment Method:</b> {pay_method}", normal_style), Paragraph(f"<b>Payment Status:</b> {pay_status}", ParagraphStyle('RightNorm', parent=normal_style, alignment=2))]
    ]

    summary_table = Table(summary_data, colWidths=[380, 160])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#111827')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 1), (-1, 2), 0.5, colors.HexColor('#E5E7EB')),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#F0FDF4')),
    ]))
    elements.append(summary_table)

    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Thank you for choosing TaxiGo!", ParagraphStyle('FooterText', parent=normal_style, alignment=1, textColor=colors.HexColor('#6B7280'))))

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="TaxiGo_Invoice_TB{booking.id:05d}.pdf"'
    return response



def contact(request):

    if request.method == "POST":

        form = ContactForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(request, "Your message has been sent successfully.")

            return redirect("contact")

    else:

        form = ContactForm()

    return render(request, "user/contact.html", {"form": form})


@login_required(login_url="login")
def add_review(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    # Sirf completed booking par review
    if booking.status != "Completed":
        messages.error(request, "You can review only completed rides.")
        return redirect("my_bookings")

    # Ek booking par sirf ek review
    if Review.objects.filter(booking=booking).exists():
        messages.warning(request, "You have already reviewed this ride.")
        return redirect("my_bookings")

    if request.method == "POST":
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)

            review.booking = booking
            review.user = request.user

            # Driver automatically vehicle se aayega
            review.driver = booking.vehicle.driver

            review.save()

            messages.success(request, "Review submitted successfully.")

            return redirect("my_bookings")

    else:
        form = ReviewForm()

    return render(request, "user/review_form.html", {
        "form": form,
        "booking": booking,
    })

User = get_user_model()
def forgot_password(request):

    if request.method == "POST":

        email = request.POST.get("email", "").strip()

        if not email:
            messages.error(
                request,
                "Please enter your email address."
            )
            return render(
                request,
                "user/forgot_password.html"
            )

        user = User.objects.filter(email__iexact=email).first()

        if not user:
            messages.error(
                request,
                "No account found with this email address."
            )
            return render(
                request,
                "user/forgot_password.html"
            )

        # Generate 6 digit OTP
        otp = random.randint(100000, 999999)

        # Store OTP in session
        request.session["forgot_password_otp"] = str(otp)
        request.session["forgot_password_user_id"] = user.id

        # Send OTP email
        send_mail(
            subject="Password Reset OTP - Taxi Booking System",

            message=f"""
Hello {user.username},

We received a request to reset your Taxi Booking System password.

Your Password Reset OTP is:

{otp}

This OTP is valid for 5 minutes.

Please do not share this OTP with anyone.

If you did not request a password reset, you can safely ignore this email.

Regards,
Taxi Booking Team
""",

            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        messages.success(
            request,
            "Password reset OTP has been sent to your email."
        )

        return redirect("forgot_password_otp")

    return render(
        request,
        "user/forgot_password.html"
    )

def forgot_password_otp(request):

    if request.method == "POST":

        entered_otp = request.POST.get(
            "otp",
            ""
        ).strip()

        saved_otp = request.session.get(
            "forgot_password_otp"
        )

        user_id = request.session.get(
            "forgot_password_user_id"
        )

        if not saved_otp or not user_id:

            messages.error(
                request,
                "OTP expired or invalid. Please request a new OTP."
            )

            return redirect("forgot_password")

        if entered_otp == str(saved_otp):

            # OTP verified
            request.session["forgot_password_verified"] = True

            # Remove OTP so it cannot be reused
            request.session.pop(
                "forgot_password_otp",
                None
            )

            messages.success(
                request,
                "OTP verified successfully. Please create your new password."
            )

            return redirect("reset_password")

        else:

            messages.error(
                request,
                "Invalid OTP. Please try again."
            )

    return render(
        request,
        "user/forgot_password_otp.html"
    )

def reset_password(request):

    verified = request.session.get(
        "forgot_password_verified"
    )

    user_id = request.session.get(
        "forgot_password_user_id"
    )

    if not verified or not user_id:

        messages.error(
            request,
            "Please verify the OTP first."
        )

        return redirect("forgot_password")

    try:

        user = User.objects.get(
            id=user_id
        )

    except User.DoesNotExist:

        messages.error(
            request,
            "User account not found."
        )

        return redirect("forgot_password")

    if request.method == "POST":

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        # Empty password check
        if not password or not confirm_password:

            messages.error(
                request,
                "Please enter both password fields."
            )

            return render(
                request,
                "user/reset_password.html"
            )

        # Password match
        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return render(
                request,
                "user/reset_password.html"
            )

        # Password validation
        if len(password) < 8:

            messages.error(
                request,
                "Password must be at least 8 characters long."
            )

            return render(
                request,
                "user/reset_password.html"
            )

        # Set new password securely
        user.set_password(password)
        user.save()

        # Clear reset session
        request.session.pop(
            "forgot_password_user_id",
            None
        )

        request.session.pop("forgot_password_verified",None)

        messages.success(request,
            "Password changed successfully. You can now login with your new password."
        )

        return redirect("login")

    return render(request,"user/reset_password.html")
