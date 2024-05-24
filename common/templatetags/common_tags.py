from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.simple_tag
def boolean_span(value):
    if value is True:
        return mark_safe('<span class="true-value">True</span>')
    elif value is False:
        return mark_safe('<span class="false-value">False</span>')
    else:
        return mark_safe('<span class="null-value">Not Defined</span>')
