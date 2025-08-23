from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse


@login_required
def post_login_redirect(request):
    user = request.user

    # If fulfiller: go to paid orders list
    if user.has_perm("orders.view_fulfillment"):
        return redirect(reverse("orders:fulfillment_paid_orders"))

    # Otherwise: send regular users to their profile (or homepage)
    return redirect(reverse("profiles:dashboard"))  # or: return redirect("/")
