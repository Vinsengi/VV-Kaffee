from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    # Basic contact
    full_name = models.CharField(max_length=140, blank=True)
    phone = models.CharField(max_length=30, blank=True)

    # Default shipping address
    street = models.CharField("Street", max_length=120)
    house_number = models.PositiveIntegerField(verbose_name="House number")
    postcode = models.CharField("Postcode/PLZ", max_length=20, blank=True)
    city = models.CharField(max_length=80, blank=True)
    country = models.CharField(max_length=60, blank=True, default="Germany")

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile({self.user.username})"
