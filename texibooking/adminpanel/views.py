from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.core.mail import send_mail
from django.conf import settings

from .forms import AdminLoginForm, UserForm
from .forms import DriverForm
from driver.models import Driver, Vehicle
from .forms import VehicleForm

from user.models import User, Booking ,Payment
from django.db.models import Sum
from django.utils import timezone

from user.forms import ReviewForm


# -------------------- Admin Login --------------------

def admin_login(request):
    return redirect("login")


# -------------------- Dashboard --------------------

@login_required(login_url="admin_login")
def admin_dashboard(request):

    total_users = User.objects.filter(
            role="user",
            is_staff=False,
            is_superuser=False
        ).count()
    total_drivers = Driver.objects.count()

    total_vehicles = Vehicle.objects.count()

    total_bookings = Booking.objects.count()

    pending_bookings = Booking.objects.filter(
        status="Pending"
    ).count()

    completed_bookings = Booking.objects.filter(
        status="Completed"
    ).count()

    total_revenue = Booking.objects.filter(
        status="Completed"
    ).aggregate(
        total=Sum("total_fare")
    )["total"] or 0

    recent_bookings = Booking.objects.order_by(
        "-booking_datetime"
    )[:5]

    context = {
        "total_users": total_users,
        "total_drivers": total_drivers,
        "total_vehicles": total_vehicles,
        "total_bookings": total_bookings,
        "pending_bookings": pending_bookings,
        "completed_bookings": completed_bookings,
        "total_revenue": total_revenue,
        "recent_bookings": recent_bookings,
    }

    return render(
        request,
        "adminpanel/home.html",
        context,
    )

# -------------------- Logout --------------------

@login_required(login_url='admin_login')
def admin_logout(request):
    logout(request)
    return redirect("admin_login")


# -------------------- User List --------------------

@login_required(login_url='admin_login')
def user_list(request):

    if not request.user.is_staff:
        return redirect("admin_login")

    users = User.objects.filter(
        role="user",
        is_staff=False,
        is_superuser=False
    ).order_by("-date_joined")

    print("Total Users:", users.count())

    for u in users:
        print(
            u.id,
            u.username,
            u.role,
            u.is_staff,
            u.is_superuser
        )

    return render(request, "adminpanel/user_list.html", {
        "users": users
    })

# -------------------- Add User --------------------

@login_required(login_url='admin_login')
def user_add(request):

    if not request.user.is_staff:
        return redirect("admin_login")

    form = UserForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():

            user = form.save(commit=False)

            user.is_staff = False
            user.is_superuser = False

            if form.cleaned_data["password"]:
                user.set_password(form.cleaned_data["password"])

            user.save()

            # Send Welcome Email
            send_mail(
                subject="Welcome to Taxi Booking System",
                message=f"""
Hello {user.username},

Your account has been created successfully by the Administrator.

Account Details
-------------------------
Username : {user.username}
Email    : {user.email}

You can now login using your username and password.

If you did not expect this account, please contact the administrator.

Regards,
Taxi Booking Team
""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            messages.success(request, "User Added Successfully")

            return redirect("user_list")

    return render(
        request,
        "adminpanel/user_form.html",
        {"form": form}
    )


# -------------------- Edit User --------------------

@login_required(login_url='admin_login')
def user_edit(request, id):

    if not request.user.is_staff:
        return redirect("admin_login")

    user = get_object_or_404(
        User,
        id=id,
        is_staff=False,
        is_superuser=False
    )

    form = UserForm(request.POST or None, instance=user)

    if request.method == "POST":

        if form.is_valid():

            obj = form.save(commit=False)

            if form.cleaned_data["password"]:
                obj.set_password(form.cleaned_data["password"])

            obj.save()

            messages.success(request, "User Updated Successfully")

            return redirect("user_list")

    return render(request,
                  "adminpanel/user_form.html",
                  {"form": form})


# -------------------- Delete User --------------------

@login_required(login_url='admin_login')
def user_delete(request, id):

    if not request.user.is_staff:
        return redirect("admin_login")

    user = get_object_or_404(
        User,
        id=id,
        is_staff=False,
        is_superuser=False
    )

    user.delete()

    messages.success(request, "User Deleted Successfully")

    return redirect("user_list")

@login_required(login_url="admin_login")
def admin_profile(request):

    if not request.user.is_staff:
        return redirect("admin_login")

    return render(request, "adminpanel/profile.html", {
        "admin": request.user
    })


@login_required(login_url="admin_login")
def driver_list(request):

    if not request.user.is_staff:
        return redirect("admin_login")

    drivers = Driver.objects.select_related("user").filter(
        user__role="driver"
    ).order_by("-id")

    return render(request, "adminpanel/driver_list.html", {
        "drivers": drivers
    })

@login_required(login_url="admin_login")
def driver_add(request):

    if not request.user.is_staff:
        return redirect("admin_login")

    form = DriverForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():

            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
                role="driver"
            )

            Driver.objects.create(
                user=user,
                full_name=form.cleaned_data["full_name"],
                mobile=form.cleaned_data["mobile"],
                address=form.cleaned_data["address"],
                license_number=form.cleaned_data["license_number"],
                vehicle_number=form.cleaned_data["vehicle_number"],
            )

            # Send Welcome Email
            send_mail(
                subject="Driver Account Created - Taxi Booking System",
                message=f"""
Hello {user.username},

Your Driver account has been created successfully by the Administrator.

Driver Account Details
--------------------------------
Username : {user.username}
Email    : {user.email}

You can now login to the Driver Panel using your username and password.

If you did not expect this account, please contact the administrator.

Regards,
Taxi Booking Team
""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            messages.success(request, "Driver Added Successfully")

            return redirect("driver_list")

    return render(request, "adminpanel/driver_add.html", {
        "form": form
    })

@login_required(login_url="admin_login")
def driver_edit(request, id):

    if not request.user.is_staff:
        return redirect("admin_login")

    driver = get_object_or_404(Driver, id=id)

    if request.method == "POST":

        driver.full_name = request.POST["full_name"]
        driver.mobile = request.POST["mobile"]
        driver.address = request.POST["address"]
        driver.license_number = request.POST["license_number"]
        driver.vehicle_number = request.POST["vehicle_number"]

        driver.user.username = request.POST["username"]
        driver.user.email = request.POST["email"]

        password = request.POST.get("password")

        if password:
            driver.user.set_password(password)

        driver.user.save()
        driver.save()

        messages.success(request, "Driver Updated Successfully")

        return redirect("driver_list")

    return render(request, "adminpanel/driver_edit.html", {
        "driver": driver
    })

@login_required(login_url="admin_login")
def driver_delete(request, id):

    if not request.user.is_staff:
        return redirect("admin_login")

    driver = get_object_or_404(Driver, id=id)

    driver.user.delete()

    messages.success(request, "Driver Deleted Successfully")

    return redirect("driver_list")

@login_required(login_url="admin_login")
def vehicle_list(request):

    vehicles = Vehicle.objects.select_related("driver").all()

    return render(request,"adminpanel/vehicle_list.html",{
        "vehicles":vehicles
    })

@login_required(login_url="admin_login")
def vehicle_add(request):

    drivers = Driver.objects.all()

    if request.method == "POST":

        form = VehicleForm(request.POST, request.FILES)

        if form.is_valid():

            vehicle = form.save(commit=False)

            vehicle.driver = Driver.objects.get(
                id=request.POST["driver"]
            )

            vehicle.save()

            messages.success(request, "Vehicle Added Successfully")

            return redirect("vehicle_list")

    else:

        form = VehicleForm()

    return render(request, "adminpanel/vehicle_form.html", {
        "form": form,
        "drivers": drivers
    })

@login_required(login_url="admin_login")
def vehicle_edit(request, id):

    vehicle = get_object_or_404(Vehicle, id=id)

    drivers = Driver.objects.all()

    if request.method == "POST":

        form = VehicleForm(
            request.POST,
            request.FILES,
            instance=vehicle
        )

        if form.is_valid():

            obj = form.save(commit=False)

            obj.driver = Driver.objects.get(
                id=request.POST["driver"]
            )

            obj.save()

            messages.success(request, "Vehicle Updated Successfully")

            return redirect("vehicle_list")

    else:

        form = VehicleForm(instance=vehicle)

    return render(request, "adminpanel/vehicle_form.html", {
        "form": form,
        "vehicle": vehicle,
        "drivers": drivers
    })

@login_required(login_url="admin_login")
def vehicle_delete(request,id):

    vehicle=get_object_or_404(Vehicle,id=id)

    vehicle.delete()

    messages.success(request,"Vehicle Deleted Successfully")

    return redirect("vehicle_list")

@login_required(login_url="admin_login")
def booking_list(request):

    bookings = Booking.objects.select_related(
        "user",
        "vehicle",
        "vehicle__driver"
    ).order_by("-booking_datetime")

    return render(
        request,
        "adminpanel/booking_list.html",
        {
            "bookings": bookings
        }
    )


def edit_booking(request, id):
    booking = get_object_or_404(Booking, id=id)

    if request.method == "POST":
        booking.pickup_location = request.POST.get("pickup_location")
        booking.drop_location = request.POST.get("drop_location")
        booking.pickup_date = request.POST.get("pickup_date")
        booking.pickup_time = request.POST.get("pickup_time")
        booking.status = request.POST.get("status")

        # Vehicle Update
        vehicle_id = request.POST.get("vehicle")
        if vehicle_id:
            booking.vehicle = get_object_or_404(Vehicle, id=vehicle_id)

        # Distance & Fare (optional)
        booking.distance = request.POST.get("distance") or booking.distance
        booking.price_per_km = request.POST.get("price_per_km") or booking.price_per_km
        booking.total_fare = request.POST.get("total_fare") or booking.total_fare

        booking.save()

        messages.success(request, "Booking Updated Successfully")
        return redirect("admin_bookings")

    vehicles = Vehicle.objects.all()

    return render(request, "adminpanel/edit_booking.html", {
        "booking": booking,
        "vehicles": vehicles,
    })

def delete_booking(request, id):

    booking = get_object_or_404(
        Booking,
        id=id
    )

    booking.delete()

    messages.success(
        request,
        "Booking Deleted Successfully"
    )

    return redirect("admin_bookings")

@login_required
def payment_dashboard(request):

    total_revenue = Payment.objects.filter(
        status="Paid"
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0

    total_payments = Payment.objects.filter(
        status="Paid"
    ).count()

    total_rides = Booking.objects.filter(
        status="Completed"
    ).count()

    today = timezone.now()

    monthly_revenue = Payment.objects.filter(
        status="Paid",
        created_at__month=today.month,
        created_at__year=today.year
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0

    recent_payments = Payment.objects.filter(
        status="Paid"
    ).order_by("-created_at")

    return render(
        request,
        "adminpanel/payment_dashboard.html",
        {
            "total_revenue": total_revenue,
            "total_payments": total_payments,
            "total_rides": total_rides,
            "monthly_revenue": monthly_revenue,
            "recent_payments": recent_payments,
        }
    )

@login_required(login_url="admin_login")
def payment_delete(request, id):
    if not request.user.is_staff:
        return redirect("admin_login")

    payment = get_object_or_404(Payment, id=id)
    payment.delete()

    messages.success(request, "Payment Deleted Successfully")
    return redirect("payment_dashboard")



from user.models import Contact

def contact_messages(request):

    contacts = Contact.objects.all().order_by("-created_at")

    return render(request, "adminpanel/contact_messages.html", {
        "contacts": contacts
    })


import json
from datetime import timedelta
from django.utils import timezone
from django.db.models.functions import TruncMonth, TruncDate
from django.db.models import Count, Sum, Avg, Case, When, Value, CharField
from user.models import Review

@login_required(login_url="admin_login")
def analytics_dashboard(request):
    now = timezone.now()
    filter_type = request.GET.get("filter", "all")
    start_date = None
    end_date = now

    if filter_type == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif filter_type == "last_7_days":
        start_date = now - timedelta(days=7)
    elif filter_type == "this_month":
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif filter_type == "this_year":
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    elif filter_type == "custom":
        start_date_str = request.GET.get("start_date")
        end_date_str = request.GET.get("end_date")
        if start_date_str:
            try:
                start_date = timezone.datetime.strptime(start_date_str, "%Y-%m-%d")
                start_date = timezone.make_aware(start_date)
            except ValueError:
                pass
        if end_date_str:
            try:
                end_date = timezone.datetime.strptime(end_date_str, "%Y-%m-%d")
                end_date = timezone.make_aware(end_date).replace(hour=23, minute=59, second=59)
            except ValueError:
                pass

    # Filtered Bookings
    bookings_filtered = Booking.objects.all()
    if start_date:
        bookings_filtered = bookings_filtered.filter(booking_datetime__gte=start_date)
    if end_date:
        bookings_filtered = bookings_filtered.filter(booking_datetime__lte=end_date)

    # Filtered Payments
    payments_filtered = Payment.objects.filter(status="Paid")
    if start_date:
        payments_filtered = payments_filtered.filter(created_at__gte=start_date)
    if end_date:
        payments_filtered = payments_filtered.filter(created_at__lte=end_date)

    # Filtered Reviews
    reviews_filtered = Review.objects.all()
    if start_date:
        reviews_filtered = reviews_filtered.filter(created_at__gte=start_date)
    if end_date:
        reviews_filtered = reviews_filtered.filter(created_at__lte=end_date)

    # KPI 1: Total Users
    total_users = User.objects.filter(role="user").count()
    new_users_week = User.objects.filter(role="user", date_joined__gte=now - timedelta(days=7)).count()

    # KPI 2: Total Drivers
    total_drivers = Driver.objects.count()
    new_drivers_week = User.objects.filter(role="driver", date_joined__gte=now - timedelta(days=7)).count()

    # KPI 3: Total Vehicles
    total_vehicles = Vehicle.objects.count()
    new_vehicles_week = Vehicle.objects.filter(driver__user__date_joined__gte=now - timedelta(days=7)).count()

    # KPI 4: Total Bookings (Filtered)
    total_bookings = bookings_filtered.count()
    new_bookings_week = Booking.objects.filter(booking_datetime__gte=now - timedelta(days=7)).count()

    # Status Bookings Count
    pending_bookings = bookings_filtered.filter(status="Pending").count()
    confirmed_bookings = bookings_filtered.filter(status="Confirmed").count()
    completed_bookings = bookings_filtered.filter(status="Completed").count()
    cancelled_bookings = bookings_filtered.filter(status="Cancelled").count()

    # Revenues
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_revenue = Payment.objects.filter(status="Paid", created_at__gte=today_start).aggregate(total=Sum("amount"))["total"] or 0

    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_revenue = Payment.objects.filter(status="Paid", created_at__gte=month_start).aggregate(total=Sum("amount"))["total"] or 0

    filtered_revenue = payments_filtered.aggregate(total=Sum("amount"))["total"] or 0

    # Weekly Revenue comparison for growth indicator
    prev_week_start = now - timedelta(days=14)
    prev_week_end = now - timedelta(days=7)
    this_week_revenue = Payment.objects.filter(status="Paid", created_at__gte=prev_week_end).aggregate(total=Sum("amount"))["total"] or 0
    prev_week_revenue = Payment.objects.filter(status="Paid", created_at__range=(prev_week_start, prev_week_end)).aggregate(total=Sum("amount"))["total"] or 0
    
    if prev_week_revenue > 0:
        revenue_growth = round(((this_week_revenue - prev_week_revenue) / prev_week_revenue) * 100, 1)
    else:
        revenue_growth = 0.0

    # Review Metrics
    total_reviews = reviews_filtered.count()
    avg_rating_val = reviews_filtered.aggregate(avg=Avg("rating"))["avg"] or 0
    avg_review_rating = round(avg_rating_val, 1)

    r5_count = reviews_filtered.filter(rating=5).count()
    r4_count = reviews_filtered.filter(rating=4).count()
    r3_count = reviews_filtered.filter(rating=3).count()
    r2_count = reviews_filtered.filter(rating=2).count()
    r1_count = reviews_filtered.filter(rating=1).count()

    if total_reviews > 0:
        positive_feedback_pct = round(((r5_count + r4_count) / total_reviews) * 100, 1)
        five_star_pct = round((r5_count / total_reviews) * 100, 1)
    else:
        positive_feedback_pct = 0.0
        five_star_pct = 0.0

    # Recent 5 Reviews for live table preview
    recent_reviews = reviews_filtered.select_related("user", "driver", "booking__vehicle").order_by("-created_at")[:5]

    # 1. Booking Status (Pie Chart)
    status_chart_data = {
        "labels": ["Pending", "Confirmed", "Completed", "Cancelled"],
        "data": [pending_bookings, confirmed_bookings, completed_bookings, cancelled_bookings]
    }

    # Helper function for last 12 months list
    months_list = []
    for i in range(11, -1, -1):
        temp_date = now - timedelta(days=i*30)
        months_list.append(temp_date.replace(day=1))
    
    twelve_months_ago = now - timedelta(days=365)

    # 2. Monthly Booking Trend (Line Chart)
    monthly_trend_qs = Booking.objects.filter(booking_datetime__gte=twelve_months_ago)\
        .annotate(month=TruncMonth('booking_datetime'))\
        .values('month')\
        .annotate(count=Count('id'))\
        .order_by('month')
    
    monthly_trend_map = {item['month'].strftime('%Y-%m'): item['count'] for item in monthly_trend_qs if item['month']}
    
    monthly_bookings_data = []
    monthly_labels = []
    for m in months_list:
        m_str = m.strftime('%Y-%m')
        monthly_labels.append(m.strftime('%b %Y'))
        monthly_bookings_data.append(monthly_trend_map.get(m_str, 0))

    # 3. Monthly Revenue (Bar Chart)
    monthly_rev_qs = Payment.objects.filter(status="Paid", created_at__gte=twelve_months_ago)\
        .annotate(month=TruncMonth('created_at'))\
        .values('month')\
        .annotate(total=Sum('amount'))\
        .order_by('month')
    
    monthly_rev_map = {item['month'].strftime('%Y-%m'): float(item['total'] or 0) for item in monthly_rev_qs if item['month']}
    monthly_revenue_data = [monthly_rev_map.get(m.strftime('%Y-%m'), 0.0) for m in months_list]

    # 4. User Registration Trend (Line Chart)
    user_reg_qs = User.objects.filter(role="user", date_joined__gte=twelve_months_ago)\
        .annotate(month=TruncMonth('date_joined'))\
        .values('month')\
        .annotate(count=Count('id'))\
        .order_by('month')
    user_reg_map = {item['month'].strftime('%Y-%m'): item['count'] for item in user_reg_qs if item['month']}
    user_reg_data = [user_reg_map.get(m.strftime('%Y-%m'), 0) for m in months_list]

    # 5. Driver Registration Trend (Line Chart)
    driver_reg_qs = User.objects.filter(role="driver", date_joined__gte=twelve_months_ago)\
        .annotate(month=TruncMonth('date_joined'))\
        .values('month')\
        .annotate(count=Count('id'))\
        .order_by('month')
    driver_reg_map = {item['month'].strftime('%Y-%m'): item['count'] for item in driver_reg_qs if item['month']}
    driver_reg_data = [driver_reg_map.get(m.strftime('%Y-%m'), 0) for m in months_list]

    # 6. Top Drivers (Horizontal Bar Chart)
    top_drivers_qs = Booking.objects.filter(status="Completed")
    if start_date:
        top_drivers_qs = top_drivers_qs.filter(booking_datetime__gte=start_date)
    if end_date:
        top_drivers_qs = top_drivers_qs.filter(booking_datetime__lte=end_date)
    
    top_drivers_qs = top_drivers_qs.values('vehicle__driver__full_name')\
        .annotate(rides=Count('id'))\
        .order_by('-rides')[:10]
    
    top_drivers_labels = [item['vehicle__driver__full_name'] or "Unknown Driver" for item in top_drivers_qs]
    top_drivers_data = [item['rides'] for item in top_drivers_qs]

    # 7. Most Booked Vehicles (Horizontal Bar Chart)
    top_vehicles_qs = Booking.objects.all()
    if start_date:
        top_vehicles_qs = top_vehicles_qs.filter(booking_datetime__gte=start_date)
    if end_date:
        top_vehicles_qs = top_vehicles_qs.filter(booking_datetime__lte=end_date)
        
    top_vehicles_qs = top_vehicles_qs.values('vehicle__company_name', 'vehicle__car_model', 'vehicle__vehicle_number')\
        .annotate(count=Count('id'))\
        .order_by('-count')[:10]
        
    top_vehicles_labels = [f"{item['vehicle__company_name']} {item['vehicle__car_model']} ({item['vehicle__vehicle_number']})" for item in top_vehicles_qs]
    top_vehicles_data = [item['count'] for item in top_vehicles_qs]

    # 8. Ride Distance Distribution (Bar Chart)
    dist_qs = bookings_filtered.annotate(
        range=Case(
            When(distance__lte=5, then=Value("0-5 KM")),
            When(distance__lte=10, then=Value("5-10 KM")),
            When(distance__lte=20, then=Value("10-20 KM")),
            When(distance__lte=50, then=Value("20-50 KM")),
            default=Value("50+ KM"),
            output_field=CharField()
        )
    ).values('range').annotate(count=Count('id'))
    
    dist_map = {item['range']: item['count'] for item in dist_qs}
    dist_labels = ["0-5 KM", "5-10 KM", "10-20 KM", "20-50 KM", "50+ KM"]
    dist_data = [dist_map.get(lbl, 0) for lbl in dist_labels]

    # 9. Daily Bookings (Line Chart)
    daily_bookings_qs = Booking.objects.all()
    if filter_type in ["today", "last_7_days"] or (start_date and (now - start_date).days <= 30):
        if start_date:
            daily_bookings_qs = daily_bookings_qs.filter(booking_datetime__gte=start_date)
        if end_date:
            daily_bookings_qs = daily_bookings_qs.filter(booking_datetime__lte=end_date)
        days_count = (now - start_date).days if start_date else 7
    else:
        thirty_days_ago = now - timedelta(days=30)
        daily_bookings_qs = daily_bookings_qs.filter(booking_datetime__gte=thirty_days_ago)
        start_date = thirty_days_ago
        days_count = 30
        
    daily_bookings_qs = daily_bookings_qs.annotate(date=TruncDate('booking_datetime'))\
        .values('date')\
        .annotate(count=Count('id'))\
        .order_by('date')
        
    daily_bookings_map = {item['date'].strftime('%Y-%m-%d'): item['count'] for item in daily_bookings_qs if item['date']}
    
    daily_labels = []
    daily_data = []
    for i in range(days_count + 1):
        d = (start_date or (now - timedelta(days=7))) + timedelta(days=i)
        d_str = d.strftime('%Y-%m-%d')
        daily_labels.append(d.strftime('%d %b'))
        daily_data.append(daily_bookings_map.get(d_str, 0))

    review_dist_data = {
        "labels": ["5 Stars", "4 Stars", "3 Stars", "2 Stars", "1 Star"],
        "data": [r5_count, r4_count, r3_count, r2_count, r1_count]
    }

    charts_json = json.dumps({
        "status_chart": status_chart_data,
        "monthly_trend": {
            "labels": monthly_labels,
            "bookings": monthly_bookings_data,
            "revenue": monthly_revenue_data
        },
        "user_reg": {
            "labels": monthly_labels,
            "data": user_reg_data
        },
        "driver_reg": {
            "labels": monthly_labels,
            "data": driver_reg_data
        },
        "top_drivers": {
            "labels": top_drivers_labels,
            "data": top_drivers_data
        },
        "top_vehicles": {
            "labels": top_vehicles_labels,
            "data": top_vehicles_data
        },
        "distance_dist": {
            "labels": dist_labels,
            "data": dist_data
        },
        "daily_bookings": {
            "labels": daily_labels,
            "data": daily_data
        },
        "review_dist": review_dist_data
    })

    return render(
        request,
        "adminpanel/analytics.html",
        {
            "filter_type": filter_type,
            "start_date": request.GET.get("start_date", ""),
            "end_date": request.GET.get("end_date", ""),
            "total_users": total_users,
            "new_users_week": new_users_week,
            "total_drivers": total_drivers,
            "new_drivers_week": new_drivers_week,
            "total_vehicles": total_vehicles,
            "new_vehicles_week": new_vehicles_week,
            "total_bookings": total_bookings,
            "new_bookings_week": new_bookings_week,
            "pending_bookings": pending_bookings,
            "confirmed_bookings": confirmed_bookings,
            "completed_bookings": completed_bookings,
            "cancelled_bookings": cancelled_bookings,
            "today_revenue": today_revenue,
            "monthly_revenue": monthly_revenue,
            "filtered_revenue": filtered_revenue,
            "revenue_growth": revenue_growth,
            "total_reviews": total_reviews,
            "avg_review_rating": avg_review_rating,
            "r5_count": r5_count,
            "r4_count": r4_count,
            "r3_count": r3_count,
            "r2_count": r2_count,
            "r1_count": r1_count,
            "positive_feedback_pct": positive_feedback_pct,
            "five_star_pct": five_star_pct,
            "recent_reviews": recent_reviews,
            "charts_data": charts_json,
        }
    )

from user.models import Review

@login_required(login_url="admin_login")
def review_list(request):

    reviews = Review.objects.select_related(
        "user",
        "driver",
        "booking",
        "booking__vehicle"
    ).order_by("-created_at")

    return render(
        request,
        "adminpanel/review_list.html",
        {
            "reviews": reviews
        }
    )

@login_required(login_url="admin_login")
def review_edit(request, id):

    review = get_object_or_404(Review, id=id)

    if request.method == "POST":

        form = ReviewForm(request.POST, instance=review)

        if form.is_valid():
            form.save()

            messages.success(request, "Review updated successfully.")

            return redirect("review_list")

    else:
        form = ReviewForm(instance=review)

    return render(
        request,
        "adminpanel/review_edit.html",
        {
            "form": form,
            "review": review
        }
    )

@login_required(login_url="admin_login")
def review_delete(request, id):

    review = get_object_or_404(Review, id=id)

    if request.method == "POST":
        review.delete()

        messages.success(request, "Review deleted successfully.")
        return redirect("review_list")

    return render(
        request,
        "adminpanel/review_delete.html",
        {
            "review": review
        }
    )