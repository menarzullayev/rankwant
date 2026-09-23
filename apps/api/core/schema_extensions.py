"""drf-spectacular kengaytmalari — autentifikator nomlarini sxemaga yozish.

Nega kerak: `ApiTokenAuthentication` — o'zimizning klass, drf-spectacular
esa uni standart `TokenAuthentication`/`JWTAuthentication` kabi tanimaydi.
Natijada har bir view uchun «could not resolve authenticator ... There was
no OpenApiAuthenticationExtension registered for that class» degan
ogohlantirish chiqardi (o'lchandi 2026-09-24: 138 tadan 114 tasi shu).

Yechim: `OpenApiAuthenticationExtension` — klassni sxemadagi xavfsizlik
sxemasiga bog'laydigan bitta kichik sinf. U import qilinishi bilan
(`config.settings` orqali) drf-spectacular uni avtomatik topadi.
"""

from __future__ import annotations

from typing import Any

from drf_spectacular.extensions import OpenApiAuthenticationExtension


class ApiTokenAuthenticationScheme(OpenApiAuthenticationExtension):
    """`ApiTokenAuthentication` → `bearerAuth` xavfsizlik sxemasi.

    Nom `bearerAuth` — OpenAPI 3 standart nomi, ya'ni generatsiya qilingan
    mijozlar (`openapi-typescript`, Swagger UI, Postman) uni tanishi oson.
    """

    target_class = "core.auth.ApiTokenAuthentication"
    name = "bearerAuth"

    def get_security_definition(self, auto_schema: Any) -> dict[str, str]:
        return {
            "type": "http",
            "scheme": "bearer",
            # Token prefiksi — hujjatda ko'rinib turadi, chunki nusxa
            # ko'chirishda odam ko'pincha "Bearer" ni tushirib qoldiradi.
            "bearerFormat": "rw_<token>",
            "description": (
                "`Authorization: Bearer rw_...` — Shaxsiy API token (PAT, ADR-0008). "
                "Tokenni profildan yaratasiz; bazada faqat xeshi saqlanadi."
            ),
        }
