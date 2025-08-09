from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from decimal import Decimal

class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    ROAST_CHOICES = [
        ("light", "Light Roast"),
        ("medium", "Medium Roast"),
        ("dark", "Dark Roast"),
    ]
    GRIND_CHOICES = [
        ("whole", "Whole Beans"),
        ("espresso", "Espresso Grind"),
        ("filter", "Filter Grind"),
        ("french_press", "French Press"),
    ]

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    sku = models.CharField(max_length=30, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")

    # Coffee specifics
    origin = models.CharField(max_length=120, default="Rwanda")
    farm = models.CharField(max_length=120, blank=True)
    variety = models.CharField(max_length=120, blank=True)     # e.g., Bourbon, Jackson
    altitude_masl = models.PositiveIntegerField(null=True, blank=True)  # meters above sea level
    process = models.CharField(max_length=120, blank=True)      # e.g., Washed, Natural, Honey
    roast_type = models.CharField(max_length=20, choices=ROAST_CHOICES, default="medium")
    tasting_notes = models.CharField(max_length=200, blank=True)

    # Commercial
    price = models.DecimalField(max_digits=8, decimal_places=2)  # EUR
    weight_grams = models.PositiveIntegerField(default=250)      # 250g, 500g, 1000g, etc.
    available_grinds = models.CharField(max_length=120, default="whole")  # comma list of GRIND_CHOICES keys

    # Inventory & media
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["sku"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.weight_grams}g)"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.weight_grams}")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("products:detail", kwargs={"slug": self.slug})

    @property
    def weight_kg(self) -> Decimal:
        return Decimal(self.weight_grams) / Decimal(1000)

