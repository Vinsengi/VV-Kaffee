# orders/views.py
import stripe
from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from django.contrib import messages

from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from products.models import Product
from cart.utils import cart_from_session, compute_summary
from .forms import CheckoutForm
from .models import Order, OrderItem
from django.contrib.admin.views.decorators import staff_member_required

stripe.api_key = settings.STRIPE_SECRET_KEY

def _to_cents(amount_decimal: Decimal) -> int:
    # Quantize first to avoid float rounding issues
    amt = amount_decimal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int((amt * 100).to_integral_value(rounding=ROUND_HALF_UP))

@transaction.atomic
def checkout(request):
    cart = cart_from_session(request.session)
    if not cart:
        messages.info(request, "Your cart is empty.")
        return redirect("cart:detail")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # 1) Create Order (pending)
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                full_name=form.cleaned_data["full_name"],
                email=form.cleaned_data["email"],
                phone_number=form.cleaned_data.get("phone_number", ""),
                address_line1=form.cleaned_data["address_line1"],
                address_line2=form.cleaned_data.get("address_line2", ""),
                city=form.cleaned_data["city"],
                postal_code=form.cleaned_data["postal_code"],
                country=form.cleaned_data.get("country", "Germany"),
                status="new",
            )

            # 2) Copy items from session cart into OrderItems + compute totals
            items, subtotal, shipping, total = compute_summary(cart)
            for item in items:
                try:
                    product = Product.objects.get(slug=item["slug"], is_active=True)
                except Product.DoesNotExist:
                    messages.warning(request, f"Item '{item['name']}' is no longer available and was skipped.")
                    continue

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name_snapshot=product.name,
                    unit_price=item["price"],
                    quantity=item["quantity"],
                    grind=item["grind"],
                    weight_grams=item["weight_grams"] or product.weight_grams,
                )

            order.subtotal = subtotal
            order.shipping = shipping
            order.total = total
            order.save(update_fields=["subtotal", "shipping", "total"])

            # 3) Create PaymentIntent

            first_name = items[0]["name"] if items else "order"
            extra = f" +{len(items) - 1} more" if len(items) > 1 else ""
            pi_description = f"VV Kaffee -  {first_name}{extra}"
             
            intent = stripe.PaymentIntent.create(
                amount=_to_cents(order.total),
                currency="eur",
                metadata={
                    "order_id": str(order.id),
                    "email": order.email,
                },
                receipt_email=order.email,
                description=pi_description,
                # automatic_payment_methods is easiest for test
                automatic_payment_methods={"enabled": True},
            )
            order.payment_intent_id = intent.id
            order.save(update_fields=["payment_intent_id"])

            # 4) Clear session cart now (or keep until paid; choose your preference)
            request.session["cart"] = {}
            request.session.modified = True

            # 5) Go to pay page to render Payment Element
            return redirect("orders:pay", order_id=order.id)
    else:
        form = CheckoutForm()

    items, subtotal, shipping, total = compute_summary(cart)
    return render(request, "orders/checkout.html", {
        "form": form, "items": items, "subtotal": subtotal, "shipping": shipping, "total": total,
    })


def pay(request, order_id: int):
    order = get_object_or_404(Order, pk=order_id)
    if not order.payment_intent_id:
        messages.error(request, "Payment not initialized for this order.")
        return redirect("orders:checkout")

    # Build a clean list of items for display
    order_items = []
    subtotal = Decimal("0.00")
    for oi in order.items.select_related("product").all():  # uses related_name="items"
        line_total = (oi.unit_price * oi.quantity).quantize(Decimal("0.01"))
        subtotal += line_total
        order_items.append({
            "name": oi.product_name_snapshot,
            "quantity": oi.quantity,
            "unit_price": oi.unit_price,
            "grind": oi.grind,
            "weight_grams": oi.weight_grams,
            "line_total": line_total,
        })

    # fetch PI client secret
    intent = stripe.PaymentIntent.retrieve(order.payment_intent_id)
    client_secret = intent.client_secret

    return render(request, "orders/pay.html", {
        "order": order,
        "order_items": order_items,
        "subtotal": order.subtotal,   # already stored on order
        "shipping": order.shipping,
        "total": order.total,
        "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
        "client_secret": client_secret,
    })


def thank_you(request, order_id: int):
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product"),
        pk=order_id
    )
    return render(request, "orders/thank_you.html", {"order": order})


# --- Webhook to confirm payment server-side (recommended) ---

# orders/views.py


stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt  # Stripe posts from outside; skip CSRF
@transaction.atomic
def stripe_webhook(request):
    # 1) Read raw payload and signature header
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    if not webhook_secret:
        # Misconfiguration: you forgot to set whsec in .env
        return HttpResponseBadRequest("Missing webhook secret")

    # 2) Verify signature and construct the event
    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=webhook_secret,
        )
    except ValueError:
        # Invalid JSON
        return HttpResponseBadRequest("Invalid payload")
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return HttpResponseBadRequest("Invalid signature")

    # 3) Handle the event types you care about
    etype = event["type"]

    if etype == "payment_intent.succeeded":
        intent = event["data"]["object"]
        order_id = (intent.get("metadata") or {}).get("order_id")
        if order_id:
            try:
                order = Order.objects.select_for_update().get(pk=order_id)
            except Order.DoesNotExist:
                return HttpResponse(status=200)  # Nothing to do; acknowledge

            # Mark order as paid if not already
            if order.status != "paid":
                # 1) Decrement stock for each item
                items = order.items.select_related("product").all()  # adjust related_name if different
                for oi in items:
                    product = oi.product
                    if product and product.stock is not None:
                        new_stock = max(0, product.stock - oi.quantity)
                        if new_stock != product.stock:
                            product.stock = new_stock
                            product.save(update_fields=["stock"])

                # 2) Mark order as paid
                order.status = "paid"
                order.save(update_fields=["status"])
        return HttpResponse(status=200)

    elif etype == "payment_intent.payment_failed":
        intent = event["data"]["object"]
        order_id = (intent.get("metadata") or {}).get("order_id")
        if order_id:
            try:
                order = Order.objects.select_for_update().get(pk=order_id)
            except Order.DoesNotExist:
                return HttpResponse(status=200)
            if order.status not in ("paid", "refunded"):
                order.status = "failed"
                order.save(update_fields=["status"])
        return HttpResponse(status=200)

    elif etype == "charge.refunded":
        charge = event["data"]["object"]
        # If you stored charge_id on the order, you could look it up here.
        # For now, no-op; add logic later if you support refunds sync.
        return HttpResponse(status=200)

    # 4) For all other events, just acknowledge
    return HttpResponse(status=200)


@staff_member_required
def order_picklist(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related("items__product"), pk=order_id)
    return render(request, "orders/picklist.html", {"order": order})