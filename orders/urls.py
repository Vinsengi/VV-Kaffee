from django.urls import path
from . import views
from .views import order_picklist_pdf

app_name = "orders"

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("pay/<int:order_id>/", views.pay, name="pay"),
    path("thank-you/<int:order_id>/", views.thank_you, name="thank_you"),
    path("webhook/stripe/", views.stripe_webhook, name="stripe_webhook"),
    path(
        "staff/orders/<int:order_id>/picklist/",
        views.order_picklist,
        name="order_picklist"
    ),
    path(
        "staff/orders/<int:order_id>/picklist/pdf/",
        order_picklist_pdf,
        name="order_picklist_pdf"
    ),
    path("staff/fulfillment/", views.fulfillment_paid_orders, name="fulfillment_paid_orders"),
    path("staff/orders/<int:order_id>/fulfill/", views.mark_order_fulfilled, name="mark_order_fulfilled"),
    path("staff/fulfillment/recent/", views.fulfillment_recently_fulfilled, name="fulfillment_recent"),
    path("account/orders/", views.my_orders, name="my_orders"),
    path("account/orders/<int:order_id>/", views.my_order_detail, name="my_order_detail"),
    path("continue-payment/<int:order_id>/", views.continue_payment, name="continue_payment"),





]
