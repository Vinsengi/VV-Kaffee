from decimal import Decimal

CART_SESSION_KEY = "cart"

def cart_summary(request):
    cart = request.session.get(CART_SESSION_KEY, {})
    item_count = sum(int(item.get("quantity", 0)) for item in cart.values())
    subtotal = sum(
        Decimal(item["price"]) * int(item["quantity"]) for item in cart.values()
    ) if cart else Decimal("0.00")
    shipping = Decimal("0.00") if subtotal >= Decimal("39.00") else (Decimal("4.90") if subtotal > 0 else Decimal("0.00"))
    total = (subtotal + shipping).quantize(Decimal("0.01"))
    return {
        "cart_item_count": item_count,
        "cart_subtotal": subtotal.quantize(Decimal("0.01")),
        "cart_total": total,
    }
