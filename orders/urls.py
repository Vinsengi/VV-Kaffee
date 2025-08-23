from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("pay/<int:order_id>/", views.pay, name="pay"),
    path("thank-you/<int:order_id>/", views.thank_you, name="thank_you"),
    path("stripe/webhook/", views.stripe_webhook, name="stripe_webhook"),
    path("staff/orders/<int:order_id>/picklist/", views.order_picklist, name="order_picklist"),

]
