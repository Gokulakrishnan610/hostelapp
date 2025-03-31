from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def divisibleby(value, arg):
    if arg == 0:
        return 0
    return float(value) / float(arg) 