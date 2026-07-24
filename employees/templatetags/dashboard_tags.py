from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key. Usage: {{ dict|get_item:key }}"""
    if dictionary is None:
        return 0
    return dictionary.get(key, 0)


@register.filter
def get_range(value):
    """Generate a range of numbers for pagination. Usage: {{ total_pages|get_range }}"""
    try:
        return range(1, int(value) + 1)
    except (ValueError, TypeError):
        return range(0)

