from django.urls import path
from .views import order_review, create_or_update_review, experience_review
app_name = "reviews"

urlpatterns = [
    path("order/<int:order_id>/review/", order_review, name="order_review"),
    path("product/<int:product_id>/review/", create_or_update_review, name="product_review"),
    path("experience/<int:order_id>/", experience_review, name="experience_review"),
]
