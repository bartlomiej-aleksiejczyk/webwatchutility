from django import template

register = template.Library()


@register.simple_tag
def boolean_span(value):
    if value is True:
        return '<span class="true-value">True</span>'
    elif value is False:
        return '<span class="false-value">False</span>'
    else:
        return '<span class="null-value">Not Defined</span>'
