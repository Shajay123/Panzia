# people/templatetags/people_filters.py
from django import template

register = template.Library()

@register.filter
def percentage(value, total=100):
    """Calculate percentage with proper rounding."""
    try:
        value = float(value)
        total = float(total)
        if total == 0:
            return 0
        result = round((value / total) * 100)
        if result > 100:
            return 100
        return result
    except (ValueError, TypeError):
        return 0

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key."""
    try:
        return dictionary.get(key, '')
    except (AttributeError, TypeError):
        return ''

@register.filter
def format_currency(value):
    """Format currency with proper Indian Rupee format."""
    try:
        value = float(value)
        if value >= 10000000:
            return f"₹{value/10000000:.2f}Cr"
        elif value >= 100000:
            return f"₹{value/100000:.2f}L"
        else:
            return f"₹{value:,.2f}"
    except (ValueError, TypeError):
        return '₹0'

@register.filter
def subtract(value, arg):
    """Subtract arg from value."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def add_plural(value, word):
    """Add plural s if value is not 1."""
    try:
        if int(value) != 1:
            return f"{value} {word}s"
        return f"{value} {word}"
    except (ValueError, TypeError):
        return f"{value} {word}"