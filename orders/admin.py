from django.contrib import admin
from .models import Order, OrderItem
from django.utils.html import format_html
from django.urls import reverse

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("line_total",)
    fields = ("product", "product_name_snapshot", "unit_price", "quantity", "grind", "weight_grams", "line_total")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "reference", "full_name", "status", "total", "picklist_link")
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "email", "payment_intent_id")
    readonly_fields = ("subtotal", "shipping", "total", "created_at", "updated_at")
    inlines = [OrderItemInline]
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    actions = ["recalculate_totals"]

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
