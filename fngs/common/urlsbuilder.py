from typing import Iterable

from django.utils.html import format_html


def _object_modification_url_nonformatted(app_name, model_name, obj_id, obj_display):
    if isinstance(obj_id, Iterable):
        htmls = [_object_modification_url_nonformatted(app_name, model_name, i, s) for i, s in zip(obj_id, obj_display)]
        return ', '.join(htmls)
    else:
        return f'<a href="/admin/{app_name}/{model_name}/{obj_id}/change/">{obj_display}</a>'


def object_modification_url(app_name, model_name, obj_id, obj_display):
    return format_html(_object_modification_url_nonformatted(app_name, model_name, obj_id, obj_display))
