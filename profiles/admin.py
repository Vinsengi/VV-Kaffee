from django.contrib import admin
from django.utils.html import format_html
from .models import Profile
from django.contrib.auth import get_user_model


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    def profile_image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:48px;height:48px;object-fit:cover;border-radius:50%;">', obj.image.url)
        return "-"
    profile_image_tag.short_description = "Profile Image"

    list_display = (
        "user",
        "profile_image_tag",  # <-- add this line
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


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    fields = ("full_name", "phone", "email", "street", "house_number", "city", "postcode", "country", "image")


User = get_user_model()


class CustomUserAdmin(admin.ModelAdmin):
    inlines = (ProfileInline,)
    list_display = ("username", "email", "is_staff", "is_active", "date_joined")


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)