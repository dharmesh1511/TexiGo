from django.urls import path
from . import views

urlpatterns = [
path('', views.driver_home, name='driver_home'),
path("register/", views.driver_register, name="driver_register"),
path("login/", views.driver_login, name="driver_login"),
path("logout/", views.driver_logout, name="driver_logout"),
path("verify-otp/", views.driver_verify_otp, name="driver_verify_otp"),

path("dashboard/", views.driver_dashboard, name="driver_dashboard"),
path("profile/", views.driver_profile, name="driver_profile"),
path("edit-profile/",views.edit_profile,name="edit_profile"),
    
path("vehicle/", views.vehicle_list, name="driver_vehicle_list"),
path("vehicle/add/", views.vehicle_add, name="driver_vehicle_add"),
path("vehicle/edit/<int:id>/", views.vehicle_edit, name="driver_vehicle_edit"),
path("vehicle/delete/<int:id>/", views.vehicle_delete, name="driver_vehicle_delete"),

path("booking-requests/",views.booking_requests,name="booking_requests",),
path("active-ride/", views.driver_active_ride, name="driver_active_ride"),
path("booking/<int:id>/accept/",views.accept_booking,name="accept_booking",),
path("booking/<int:id>/reject/",views.reject_booking,name="reject_booking",),
path("booking/<int:id>/arrived/",views.driver_arrived,name="driver_arrived",),
path("booking/<int:id>/verify-otp/",views.verify_ride_otp,name="verify_ride_otp",),
path("booking/<int:id>/start/",views.start_ride,name="start_ride",),
path("booking/<int:id>/complete/",views.complete_booking,name="complete_booking",),
path("booking/<int:id>/confirm-cash/",views.confirm_cash_payment,name="confirm_cash_payment",),

path('ride-history/', views.ride_history, name='ride_history'),

path("earnings/",views.earnings,name="driver_earnings"),

path("my-reviews/", views.my_reviews, name="my_reviews"),

path("forgot-password/",views.driver_forgot_password,name="driver_forgot_password"),
path("forgot-password/otp/",views.driver_forgot_password_otp,name="driver_forgot_password_otp"),
path("reset-password/",views.driver_reset_password,name="driver_reset_password"),


]