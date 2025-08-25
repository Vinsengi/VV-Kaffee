from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse


@login_required
def post_login_redirect(request):
    u = request.user
    if u.groups.filter(name="Fulfillment Department").exists():
        return redirect(reverse("orders:fulfillment_paid_orders"))
    return redirect("/")  # or profiles:dashboard for regular users
