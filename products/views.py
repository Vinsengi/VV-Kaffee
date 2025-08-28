# products/views.py
from django.views.generic import ListView, DetailView
from .models import Product


class ProductListView(ListView):
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        return Product.objects.filter(is_active=True).order_by("-created_at")


class ProductDetailView(DetailView):
    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        product = self.object
        # Use product.available_grinds if set, else sensible default
        raw = (product.available_grinds or "whole,espresso,filter,french_press")
        values = [g.strip() for g in raw.split(",") if g.strip()]
        choices = [(g, g.replace("_", " ").title()) for g in values]
        ctx["grind_choices"] = choices
        return ctx
