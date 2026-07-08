from django import template

register = template.Library()

@register.filter
def sum_attr(items, attr):
    """Sum a list of dictionaries by attribute name."""
    try:
        total = 0
        for item in items:
            if isinstance(item, dict):
                total += item.get(attr, 0)
            else:
                total += getattr(item, attr, 0)
        return total
    except (AttributeError, TypeError, ValueError):
        return 0


@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key."""
    try:
        return dictionary.get(key, 0)
    except (AttributeError, TypeError):
        return 0