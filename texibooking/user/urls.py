from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path("signup/", views.signup_view, name="signup"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("edit-profiles/", views.edit_profiles, name="user_edit_profile"),
    path('available-cars/', views.available_cars, name='available_cars'),
    path("ride/<int:id>/", views.ride_detail, name="ride_detail"),
    
    path("book-cab/<int:id>/",views.book_cab,name="book_cab"),
    path("search-location/", views.search_location, name="search_location"),
    path("my-bookings/",views.my_bookings,name="my_bookings"),
    path("active-ride/", views.active_ride, name="active_ride"),
    path("check-booking-status/<int:id>/", views.check_booking_status, name="check_booking_status"),
    path("ride-history/", views.ride_history, name="user_ride_history"),
    path("cancel-booking/<int:id>/",views.cancel_booking,name="cancel_booking"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),

    path("payment/<int:id>/",views.payment,name="payment"),
    path("pay-cash/<int:id>/",views.pay_cash,name="pay_cash"),
    path("payment-success/",views.payment_success,name="payment_success"),
    path("download-invoice/<int:id>/",views.download_invoice,name="download_invoice"),
    path("add-review/<int:booking_id>/",views.add_review,name="add_review"),

    path("forgot-password/",views.forgot_password,name="forgot_password"),
    path("forgot-password/otp/",views.forgot_password_otp,name="forgot_password_otp"),
    path("reset-password/",views.reset_password,name="reset_password"),

]