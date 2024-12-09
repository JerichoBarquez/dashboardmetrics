from django import template
import json

register = template.Library()

@register.filter(name='replace_single_quotes')
def replace_single_quotes(value):
    value = json.dumps(value)
    return value.replace("'", '"')

@register.filter
def divide(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0.0
    

@register.filter
def multiply(value, arg):
    try:
        return value * arg
    except (ValueError, ZeroDivisionError):
        return 0
    
@register.filter
def has_utilization(highest_util):
    return any(utilization > 0 for utilization in highest_util.values())

@register.filter
def low_utilization(lowest_util):
    return any(utilization > 0 for utilization in lowest_util.values())

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)