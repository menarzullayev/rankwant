"""Hodisa turlari va yuklari — bitta joy (ADR-0029 §4).

⚠️ **Nega alohida modul.** `event:` nomi va yuk sxemasi — server bilan
mijoz o'rtasidagi **shartnoma**. U nashr joyida ham, obuna joyida ham
yozilsa, biri o'zgarib ikkinchisi jimgina eskirib qolardi: oqim ochiladi,
hodisa keladi, lekin mijoz noto'g'ri maydonni o'qiydi — va buni faqat
brauzerda sezish mumkin. Shu sababli nomlar va yuklar shu yerda.

⚠️ **Yukka shaxsiy ma'lumot solinmaydi.** `verdict` yuki faqat raqamlar va
kodlar; manba kod, kompilyatsiya chiqishi va bildirishnoma matni **hech
qachon** oqimga tushmaydi. Sabab ikki xil: (a) ular log va proksi
buferlarida qolishi mumkin, (b) mijoz baribir to'liq yozuvni REST dan
oladi (ADR-0029 §9: oqim — optimallashtirish, haqiqat manbasi emas).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from realtime import bus

if TYPE_CHECKING:  # pragma: no cover — faqat tip uchun, import sikli yo'q
    from judging.models import Attempt

#: Urinish verdikti tayyor bo'ldi. Yuk: raqamlar va kodlar.
EVENT_VERDICT = "verdict"
#: Ommaviy jadval o'zgardi. Yuk: ⚠️ FAQAT versiya belgisi, jadval EMAS.
EVENT_STANDINGS = "standings"


def verdict_payload(attempt: Attempt) -> dict[str, Any]:
    """Verdikt hodisasining yuki — qatorning qisqa ko'rinishi."""
    return {
        "attempt_id": attempt.pk,
        "problem": attempt.problem.slug,
        "verdict": attempt.verdict,
        "score": attempt.score,
        "time_ms": attempt.time_ms,
        "memory_kb": attempt.memory_kb,
        "failed_test_index": attempt.failed_test_index,
    }


def standings_payload(contest_id: int, version: str) -> dict[str, Any]:
    """Jadval o'zgardi degan **belgi**.

    ⚠️ Jadvalning O'ZI bu yerga solinmaydi (ADR-0029 §3). Sabab
    `docs/10-operations` dagi o'lchov: 110 000 tomoshabin uchun 45 KB
    hujjatni oqim orqali tashish chekka kesh bergan narsani
    qimmatlashtiradi (7 300 so'rov/s, 330 MB/s origin'ga). Mijoz
    versiyani solishtiradi va **faqat farq bo'lsa** mavjud keshli
    endpointdan qayta oladi.
    """
    return {"contest_id": contest_id, "version": version}


def publish_verdict(attempt: Attempt) -> None:
    """Verdiktni egasiga yuboradi.

    ⚠️ Chaqiruvchi `apply_result` **qaytgandan keyin** chaqirishi shart:
    u `@transaction.atomic`, ya'ni shu paytda verdikt haqiqatan commit
    qilingan. Usiz obunachi hali ko'rinmaydigan qator haqida xabar olardi
    va REST dan qayta o'qisa eski holatni ko'rardi (ADR-0029 §6).
    """
    bus.publish(bus.user_channel(attempt.user_id), EVENT_VERDICT, verdict_payload(attempt))


def publish_standings(contest_id: int, version: str) -> None:
    bus.publish(
        bus.standings_channel(contest_id),
        EVENT_STANDINGS,
        standings_payload(contest_id, version),
    )
