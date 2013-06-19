from django import template
register = template.Library()


@register.filter
def build_absolute_uri(uri, request):
    return request.build_absolute_uri(uri)


@register.filter(name='split')
def split(value, arg):
    return value.split(arg)
