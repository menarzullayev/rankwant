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

#: BRAUZERDA ochilishi mumkin bo'lgan yagona turlar.
#:
#: Fayllar tashqi arxivdan ko'chirilgan, ya'ni ularning turi bizniki
#: emas. `text/html` yoki `image/svg+xml` ni o'z originimizdan berish
#: saqlanadigan XSS bo'lardi — sessiya cookie'si aynan shu originda.
#: Ro'yxatdan tashqarisi yuklab olinadi, ko'rsatilmaydi.
INLINE_TYPES = frozenset(
    {"image/png", "image/jpeg", "image/gif", "image/webp", "image/avif", "application/pdf"}
)
FALLBACK_TYPE = "application/octet-stream"


@require_safe
@cache_control(public=True, max_age=CACHE_SECONDS, immutable=True)
def media(request: HttpRequest, path: str) -> HttpResponse:
    if ".." in path or path.startswith("/"):
        raise Http404
    try:
        body, stored_type = get_media(MEDIA_PREFIX + path)
    except Exception as exc:
        raise Http404("fayl topilmadi") from exc

    content_type = stored_type.split(";")[0].strip().lower()
    inline = content_type in INLINE_TYPES
    response = HttpResponse(body, content_type=content_type if inline else FALLBACK_TYPE)
    response["X-Content-Type-Options"] = "nosniff"
    if not inline:
        response["Content-Disposition"] = "attachment"
    return response


@require_safe
@cache_control(public=True, max_age=CACHE_SECONDS, immutable=True)
def speech_piece(request: HttpRequest, name: str) -> HttpResponse:
    """One audio piece of a statement read aloud (ADR-0064 § 5).

    The name is the piece's content key (`speech.cache_key`): the same name
    never gives other audio, so it is cached for a year, at the edge too.
    """
    from core.middleware import EDGE_CACHE_FLAG
    from problems import speech_audio

    key = name.removesuffix(speech_audio.EXT)
    data = speech_audio.get(key) if name.endswith(speech_audio.EXT) else None
    if data is None:
        raise Http404
    response = HttpResponse(data, content_type=speech_audio.CONTENT_TYPE)
    response["X-Content-Type-Options"] = "nosniff"
    setattr(response, EDGE_CACHE_FLAG, True)
    return response
