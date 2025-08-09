{
  "kivu-bourbon-250g": {
    "name": "Kivu Bourbon 250g",
    "price": "10.90",
    "quantity": 2,
    "grind": "whole",
    "weight_grams": 250,
    "sku": "KV-250-BOR-MED",
    "image_url": "/media/products/kivu.jpg"
  }
}


# cart/views.py
from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from products.models import Product



CART_SESSION_KEY = "cart"
GRIND_OPTIONS = ["whole", "espresso", "filter", "french_press"]


def _get_cart(session):
    cart = session.get(CART_SESSION_KEY)
    if cart is None:
        cart = {}
        session[CART_SESSION_KEY] = cart
    return cart


def _cart_totals(cart_dict):
    subtotal = Decimal("0.00")
    for item in cart_dict.values():
        subtotal += Decimal(item["price"]) * int(item["quantity"])
    shipping = Decimal("0.00") if subtotal >= Decimal("39.00") else (Decimal("4.90") if subtotal > 0 else Decimal("0.00"))
    total = (subtotal + shipping).quantize(Decimal("0.01"))
    return subtotal.quantize(Decimal("0.01")), shipping, total


def cart_detail(request):
    cart = _get_cart(request.session)

    # Build a list of items with computed line totals for the template
    cart_items = []
    for slug, item in cart.items():
        qty = int(item.get("quantity", 0))
        price = Decimal(item.get("price", "0"))
        line_total = (price * qty).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        cart_items.append({
            "slug": slug,
            "name": item.get("name", ""),
            "sku": item.get("sku", ""),
            "image_url": item.get("image_url", ""),
            "grind": item.get("grind", "whole"),
            "quantity": qty,
            "price": price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "line_total": line_total,
        })

    # Totals
    subtotal = sum((i["line_total"] for i in cart_items), Decimal("0.00")).quantize(Decimal("0.01"))
    shipping = Decimal("0.00") if subtotal >= Decimal("39.00") else (Decimal("4.90") if subtotal > Decimal("0.00") else Decimal("0.00"))
    total = (subtotal + shipping).quantize(Decimal("0.01"))

    context = {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "shipping": shipping,
        "total": total,
    }
    return render(request, "cart/cart.html", context)


def cart_add(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    cart = _get_cart(request.session)
    qty = int(request.POST.get("quantity", 1))
    grind = (request.POST.get("grind") or "whole").strip()

    key = product.slug
    if key not in cart:
        cart[key] = {
            "name": product.name,
            "price": str(product.price),
            "quantity": 0,
            "grind": grind,
            "weight_grams": product.weight_grams,
            "sku": product.sku,
            "image_url": product.image.url if product.image else "",
        }
    cart[key]["quantity"] += qty
    cart[key]["grind"] = grind
    request.session.modified = True
    messages.success(request, f"Added {qty} × {product.name} to cart.")
    return redirect("cart:detail")


def cart_remove(request, slug):
    cart = _get_cart(request.session)
    if slug in cart:
        del cart[slug]
        request.session.modified = True
        messages.info(request, "Item removed from cart.")
    return redirect("cart:detail")


def cart_update(request, slug):
    cart = _get_cart(request.session)
    if slug in cart:
        qty = max(1, int(request.POST.get("quantity", 1)))
        grind = (request.POST.get("grind") or cart[slug]["grind"]).strip()
        cart[slug]["quantity"] = qty
        cart[slug]["grind"] = grind
        request.session.modified = True
        messages.success(request, "Cart updated.")
    return redirect("cart:detail")


def cart_clear(request):
    request.session[CART_SESSION_KEY] = {}
    request.session.modified = True
    messages.info(request, "Cart cleared.")
    return redirect("cart:detail")
