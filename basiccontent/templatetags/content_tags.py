from django import template
from django.contrib.contenttypes.models import ContentType

register = template.Library()

@register.filter
def get_content_object(content_id):
    if not content_id:
        return None
    from basiccontent.models import Content
    try:
        return Content.objects.get(id=content_id).item
    except Content.DoesNotExist:
        return None

@register.filter
def content_type(obj):
    if not obj:
        return ''
    return ContentType.objects.get_for_model(obj).model

@register.filter
def get_filename(path):
    return path.split('/')[-1]

@register.filter
def get_item(dictionary, key):
    """사전에서 키에 해당하는 값을 가져오는 템플릿 필터"""
    return dictionary.get(key)