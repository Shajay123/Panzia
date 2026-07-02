# people/templatetags/math_filters.py

from django import template

register = template.Library()

@register.filter
def percentage(value, total):
    """
    Calculate percentage safely.
    Usage: {{ value|percentage:total }}
    """
    try:
        if total and int(total) > 0:
            result = (int(value) / int(total)) * 100
            return min(100, result)
        return 0
    except (TypeError, ValueError, ZeroDivisionError):
        return 0