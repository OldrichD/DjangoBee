# custom_filters.py

from django import template

register = template.Library()

@register.filter(name='get_name')
def get_name(dictionary, key):
    return dictionary.get(key, None)
