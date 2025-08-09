from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("line_total",)
    fields = ("product", "product_name_snapshot", "unit_price", "quantity", "grind", "weight_grams", "line_total")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "status", "total", "created_at")
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
