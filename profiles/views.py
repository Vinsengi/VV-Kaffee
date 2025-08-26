from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import HttpResponseRedirect


@login_required
def post_login_redirect(request):
    # # Fulfillment staff go to the paid orders screen
    # if request.user.groups.filter(name="Fulfillment Department").exists():
    #     return redirect("/staff/fulfillment/")

    # # Everyone else – adjust as you like
    # return redirect("/")
    return HttpResponseRedirect("/staff/fulfillment/")

