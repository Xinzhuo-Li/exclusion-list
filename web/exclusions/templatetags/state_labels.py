from django import template

from exclusions.queries import STATE_NAMES

register = template.Library()


@register.filter
def state_label(code: str) -> str:
    return STATE_NAMES.get(str(code).upper(), code)
