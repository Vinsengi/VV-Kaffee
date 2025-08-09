from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "is_public", "created_at")
    list_filter = ("rating", "is_public", "created_at")
    search_fields = ("product__name", "user__username", "comment")
