# orders/templatetags/user_extras.py
from django import template

register = template.Library()


@register.filter
def has_group(user, group_name):
    """
    Usage: {% if user|has_group:"Fulfillment Department" %}
    Returns True if the user is in the given group.
    """
    if not getattr(user, "is_authenticated", False):
        return False
    return user.groups.filter(name=group_name).exists()
