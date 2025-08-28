from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # show real fields that exist on Profile
    list_display = (
        "user",
        "full_name",
        "phone",
        "city",
        "postcode",
        "country",
        "updated_at",
    )
    list_filter = ("country", "city", "updated_at")
    search_fields = (
        "user__username",
        "user__email",
        "full_name",
        "phone",
        "city",
        "postcode",
    )

