from django.dispatch import receiver
from allauth.account.signals import user_logged_in, user_signed_up
from .models import Order


def _attach_orders_to_user(user):
    if not user.email:
        return
    Order.objects.filter(user__isnull=True, email__iexact=user.email).update(user=user)


@receiver(user_signed_up)
def on_signup(sender, request, user, **kwargs):
    _attach_orders_to_user(user)


@receiver(user_logged_in)
def on_login(sender, request, user, **kwargs):
    _attach_orders_to_user(user)
