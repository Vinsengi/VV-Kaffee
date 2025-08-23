from django.contrib import admin, messages
from django.conf import settings
import stripe
from .models import Order, OrderItem
from django.utils.html import format_html
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False

    # Show a computed column safely:
    readonly_fields = (
        "product_name_snapshot",
        "unit_price",
        "quantity",
        "grind",
        "weight_grams",
        "line_total_display",   # <-- use display method
    )
    fields = (
        "product_name_snapshot",
        "unit_price",
        "quantity",
        "grind",
        "weight_grams",
        "line_total_display",   # <-- not 'line_total'
    )

    @admin.display(description="Line total")
    def line_total_display(self, obj):
        # guard against None
        if obj is None:
            return "€0.00"
        return f"€{obj.line_total}"


@admin.action(description="Reconcile selected orders with Stripe")
def reconcile_with_stripe(modeladmin, request, queryset):
    updated = 0
    for order in queryset:
        if not order.payment_intent_id:
            continue
        try:
            pi = stripe.PaymentIntent.retrieve(order.payment_intent_id)
            if pi.status == "succeeded" and order.status != "paid":
                # apply same logic as webhook
                for oi in order.items.select_related("product").all():
                    p = oi.product
                    if p and p.stock is not None:
                        ns = max(0, p.stock - oi.quantity)
                        if ns != p.stock:
                            p.stock = ns
                            p.save(update_fields=["stock"])
                order.status = "paid"
                order.save(update_fields=["status"])
                updated += 1
        except Exception:
            pass
    messages.info(request, f"Reconciled {updated} order(s).")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "reference", "full_name", "status", "total", "picklist_link", "picklist_pdf_link")
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "email", "payment_intent_id")
    readonly_fields = ("subtotal", "shipping", "total", "created_at", "updated_at")
    inlines = [OrderItemInline]
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    actions = [reconcile_with_stripe, "recalculate_totals"]

    @admin.action(description="Recalculate totals for selected orders")
    def recalculate_totals(self, request, queryset):
        for order in queryset:
            order.recalc_totals()

    def reference_display(self, obj):
        return getattr(obj, "reference", obj.id)
    reference_display.short_description = "Reference"

    def picklist_link(self, obj):
        url = reverse("orders:order_picklist", kwargs={"order_id": obj.id})
        return format_html('<a class="button" target="_blank" href="{}">Picklist</a>', url)
    picklist_link.short_description = " "

    def picklist_pdf_link(self, obj):
        url = reverse("orders:order_picklist_pdf", args=[obj.id])
        return format_html('<a class="button" href="{}" target="_blank">📄 PDF Picklist</a>', url)
    picklist_pdf_link.short_description = "Picklist PDF"


# admin.site.register(Order, OrderAdmin)