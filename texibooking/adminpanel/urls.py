from django.urls import path
from . import views

urlpatterns = [
  path('', views.admin_dashboard, name='admin_dashboard'),
  path("login/", views.admin_login, name="admin_login"),
  path("admin_logout/",views.admin_logout,name='admin_logout'),
  path("contact-messages/",views.contact_messages,name="contact_messages"),

  path("users/", views.user_list, name="user_list"),
  path("users/add/", views.user_add, name="user_add"),
  path("users/edit/<int:id>/", views.user_edit, name="user_edit"),
  path("users/delete/<int:id>/", views.user_delete, name="user_delete"),

  path("profile/", views.admin_profile, name="admin_profile"),

  path("drivers/", views.driver_list, name="driver_list"),
  path("drivers/add/", views.driver_add, name="driver_add"),
  path("drivers/edit/<int:id>/", views.driver_edit, name="driver_edit"),
  path("drivers/delete/<int:id>/", views.driver_delete, name="driver_delete"),

  path("vehicles/",views.vehicle_list,name="vehicle_list"),
  path("vehicles/add/",views.vehicle_add,name="vehicle_add"),
  path("vehicles/edit/<int:id>/",views.vehicle_edit,name="vehicle_edit"),
  path("vehicles/delete/<int:id>/",views.vehicle_delete,name="vehicle_delete"),

  path("bookings/",views.booking_list,name="admin_bookings",),
  path("bookings/edit/<int:id>/",views.edit_booking,name="edit_booking",),
  path("bookings/delete/<int:id>/",views.delete_booking,name="delete_booking",),

  path("payment-dashboard/",views.payment_dashboard,name="payment_dashboard"),
  path("payment/delete/<int:id>/", views.payment_delete, name="delete_payment"),
  path("analytics/", views.analytics_dashboard, name="admin_analytics"),

  path("reviews/",views.review_list,name="review_list"),
  path("review/edit/<int:id>/",views.review_edit,name="review_edit",),
  path("review/delete/<int:id>/",views.review_delete,name="review_delete",),

  ]