from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    # Basic contact
    full_name = models.CharField(max_length=140, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField("Email address", max_length=254, blank=True)  # added email field

    # Default shipping address
    street = models.CharField("Street", max_length=120, blank=True)
    house_number = models.CharField("House number", max_length=20, blank=True)
    postcode = models.CharField("Postcode/PLZ", max_length=20, blank=True)
    city = models.CharField(max_length=80, blank=True)
    country = models.CharField(max_length=60, blank=True, default="Germany")

    # Profile image
    image = models.ImageField(upload_to="profile_images/", blank=True, null=True)  # added image field

    updated_at = models.DateTimeField(auto_now=True)
