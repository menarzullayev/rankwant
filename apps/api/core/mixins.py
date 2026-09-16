"""Model mixinlari — maydon qo'shmaydigan umumiy xususiyatlar.

Nega alohida fayl: `core/models.py` Django modellarini saqlaydi, mixin esa
model emas. Aralashtirilsa `mypy_django_plugin` va `Meta` merosi chalkashadi.
"""

from __future__ import annotations

from datetime import datetime

from django.utils import timezone


class TimeWindowMixin:
    """`start_at` … `end_at` oralig'idagi holat xususiyatlari.

    `ArenaRound`, `Contest`, `Tournament` va `Hackathon` da `is_running` /
    `is_finished` so'zma-so'z bir xil yozilgan edi — to'rt nusxa. Mantiq
    shu yerga chiqarildi, modelda faqat o'ziga xos qismi qoladi.

    `end_at` ikki xil bo'lishi mumkin, mixin farqini bilmaydi:
      * maydon — `Contest.end_at`, `Tournament.end_at`;
      * hisoblangan property — `ArenaRound.end_at` (savollar soniga bog'liq).

    ⚠️ `is_running` vaqt oynasini tekshiradi, holatni EMAS. `Duel` shu sabab
    bu mixin'ga ulanmagan: u yerda `status == ACCEPTED` sharti ham bor va
    «tugadi» xususiyati `is_due` deb nomlangan — aralashtirilsa ma'no
    o'zgarardi.
    """

    #: Modelda maydon yoki hisoblangan property sifatida bo'ladi — bu yerda
    #: faqat e'lon (read-only), qiymat bermaydi. `ArenaRound.end_at`
    #: property bo'lgani uchun yoziladigan atribut e'lon qilish mypy'da
    #: «Cannot override writeable attribute with read-only property»
    #: xatosini berardi.
    @property
    def start_at(self) -> datetime:
        raise NotImplementedError

    @property
    def end_at(self) -> datetime:
        raise NotImplementedError

    @property
    def is_running(self) -> bool:
        return self.start_at <= timezone.now() < self.end_at

    @property
    def is_finished(self) -> bool:
        return timezone.now() >= self.end_at
