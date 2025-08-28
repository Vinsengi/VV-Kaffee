from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ProfileForm
from django.http import HttpResponseRedirect


@login_required
def account_dashboard(request):
    # recent orders for this user
    orders = request.user.orders.all().prefetch_related("items").order_by("-created_at")[:10]
    return render(request, "profiles/account_dashboard.html", {"orders": orders})


@login_required
def profile_edit(request):
    profile = request.user.profile  # created by signal
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("profiles:account_dashboard")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "profiles/profile_edit.html", {"form": form})


@login_required
def order_list(request):
    orders = request.user.orders.all().prefetch_related("items").order_by("-created_at")
    return render(request, "profiles/order_list.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    order = request.user.orders.prefetch_related("items__product").get(id=order_id)
    return render(request, "profiles/order_detail.html", {"order": order})


@login_required
def post_login_redirect(request):
    # # Fulfillment staff go to the paid orders screen
    # if request.user.groups.filter(name="Fulfillment Department").exists():
    #     return redirect("/staff/fulfillment/")

    # # Everyone else – adjust as you like
    # return redirect("/")
    return HttpResponseRedirect("/staff/fulfillment/")