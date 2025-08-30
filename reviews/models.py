from django.conf import settings
from django.db import models
from products.models import Product


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="product_reviews")
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1,6)])
    title = models.CharField(max_length=120, blank=True)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("product", "user")  # one review per product per user
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product} · {self.user} · {self.rating}★"


class ExperienceFeedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.OneToOneField("orders.Order", on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1,6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        who = self.user or "Anonymous"
        oid = self.order_id or "—"
        return f"Experience {self.rating}★ by {who} (order #{oid})"
