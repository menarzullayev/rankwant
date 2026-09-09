"""Ko'chirilgan media fayllarni beradi.

Fayllar MinIO/S3 da turadi va tashqariga ochilmagan (10-operations:
saqlash faqat ichki tarmoqda). Tunnel `/api/*` ni API ga yo'naltiradi,
ya'ni bu yo'l qo'shimcha ingress sozlamasisiz ishlaydi.

Kalit MAZMUNGA bog'langan (SHA-256), shuning uchun javob abadiy
keshlanadi: bir xil manzil hech qachon boshqa faylni bermaydi.
"""

from __future__ import annotations

from django.http import Http404, HttpRequest, HttpResponse
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_safe

from problems.storage import MEDIA_PREFIX, get_media

CACHE_SECONDS = 31_536_000  # bir yil


@require_safe
@cache_control(public=True, max_age=CACHE_SECONDS, immutable=True)
def media(request: HttpRequest, path: str) -> HttpResponse:
    if ".." in path or path.startswith("/"):
        raise Http404
    try:
        body, content_type = get_media(MEDIA_PREFIX + path)
    except Exception as exc:
        raise Http404("fayl topilmadi") from exc
    response = HttpResponse(body, content_type=content_type)
    response["X-Content-Type-Options"] = "nosniff"
    return response
