from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse
from products.models import Product
from cart.utils import cart_from_session, compute_summary
from .forms import CheckoutForm
from .models import Order, OrderItem

@transaction.atomic
def checkout(request):
    cart = cart_from_session(request.session)
    if not cart:
        messages.info(request, "Your cart is empty.")
        return redirect("cart:detail")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create order shell
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

            # Build items & totals once
            items, subtotal, shipping, total = compute_summary(cart)

            # Create order items and (optionally) decrement stock
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

                if product.stock is not None:
                    product.stock = max(0, product.stock - item["quantity"])
                    product.save(update_fields=["stock"])

            order.subtotal = subtotal
            order.shipping = shipping
            order.total = total
            order.save(update_fields=["subtotal", "shipping", "total"])

            # Clear session cart
            request.session["cart"] = {}
            request.session.modified = True

            messages.success(request, f"Order #{order.id} created! (Status: {order.status})")
            return redirect(reverse("orders:thank_you", kwargs={"order_id": order.id}))
    else:
        form = CheckoutForm()

    items, subtotal, shipping, total = compute_summary(cart)
    return render(request, "orders/checkout.html", {
        "form": form,
        "items": items,
        "subtotal": subtotal,
        "shipping": shipping,
        "total": total,
    })


def thank_you(request, order_id: int):
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect("home")
    return render(request, "orders/thank_you.html", {"order": order})
