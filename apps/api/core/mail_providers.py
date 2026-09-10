"""Email provayderlari — har biri bitta JSON POST.

Nega bittasi yetmaydi: bepul planlar KUNLIK kvota qo'yadi — Brevo 300/kun,
Mailjet 200/kun, Resend 100/kun, MailerSend esa 500/oy (≈16/kun) va uning
ustiga 100 API so'rov/kun. Parol tiklash so'rovlari kun davomida notekis
keladi, ya'ni kvota tugashi kundalik hodisa bo'ladi. Zanjir — `core.mailer`.

`requests`/`httpx` qo'shilmadi: to'rttasi ham oddiy JSON POST, stdlib
yetarli va Docker image ga yangi bog'liqlik kirmaydi.
"""

from __future__ import annotations

import base64
import json
import logging
import urllib.error
import urllib.request
from dataclasses import dataclass

from django.conf import settings

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Message:
    to: str
    subject: str
    text: str
    html: str = ""


class SendError(Exception):
    """Provayder yubora olmadi — zanjir keyingisiga o'tadi.

    Ataylab «bu xato tuzatib bo'lmaydi» degan tur yo'q: HTTP kodiga qarab
    zanjirni to'xtatish xavfli. MailerSend tasdiqlanmagan akkauntda 422,
    kaliti eskirgan provayder 401 qaytaradi — ikkalasi ham XABARDA emas,
    PROVAYDERDA muammo, ya'ni keyingisi yuborishi mumkin. Manzilning o'zi
    yaroqsiz bo'lsa, u zanjirga kirishdan oldin tekshiriladi.
    """

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


#: `urllib` ning standart `User-Agent` i — `Python-urllib/3.12`. Resend va
#: MailerSend API'lari Cloudflare ortida turadi va uni bot deb bloklaydi:
#: o'lchandi, ikkalasi ham `HTTP 403 … error_code 1010,
#: browser_signature_banned` qaytardi. Brevo va Mailjet o'tkazib yuborardi,
#: ya'ni bu nosozlik zanjirning yarmida jimgina yashiringan bo'lardi.
USER_AGENT = "RankWant/1.0 (+https://rankwant.bugvector.uz)"


def _post(url: str, payload: dict[str, object], headers: dict[str, str]) -> str:
    """POST qiladi va javob tanasini qaytaradi. Xato bo'lsa `SendError`."""
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
            **headers,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=settings.EMAIL_TIMEOUT) as response:
            return str(response.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as exc:
        detail = exc.read()[:500].decode("utf-8", "replace")
        raise SendError(f"HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise SendError(f"tarmoq: {exc}") from exc


def _sender(provider: str) -> tuple[str, str]:
    """Provayderning O'Z jo'natuvchi manzili.

    SPF `include:` mexanizmi 10 ta DNS lookup bilan cheklangan, ya'ni to'rt
    provayderni bitta domenning SPF yozuviga sig'dirib bo'lmaydi. Har biri
    o'z subdomenidan yuboradi (`BREVO_FROM=no-reply@mail1.rankwant.uz` …).
    Sozlanmagan bo'lsa umumiy `EMAIL_FROM` ga tushadi — bu faqat bitta
    provayder ishlatilayotganda to'g'ri.
    """
    return (
        getattr(settings, f"{provider.upper()}_FROM", "") or settings.EMAIL_FROM,
        settings.EMAIL_FROM_NAME,
    )


class Brevo:
    """https://api.brevo.com/v3/smtp/email — bepul 300/kun, kartasiz."""

    name = "brevo"

    @property
    def configured(self) -> bool:
        return bool(settings.BREVO_API_KEY)

    def send(self, msg: Message) -> None:
        email, name = _sender(self.name)
        _post(
            "https://api.brevo.com/v3/smtp/email",
            {
                "sender": {"email": email, "name": name},
                "to": [{"email": msg.to}],
                "subject": msg.subject,
                "textContent": msg.text,
                **({"htmlContent": msg.html} if msg.html else {}),
            },
            {"api-key": settings.BREVO_API_KEY},
        )


class Mailjet:
    """https://api.mailjet.com/v3.1/send — bepul 200/kun, kartasiz."""

    name = "mailjet"

    @property
    def configured(self) -> bool:
        return bool(settings.MAILJET_API_KEY and settings.MAILJET_SECRET_KEY)

    def send(self, msg: Message) -> None:
        email, name = _sender(self.name)
        credentials = f"{settings.MAILJET_API_KEY}:{settings.MAILJET_SECRET_KEY}".encode()
        body = _post(
            "https://api.mailjet.com/v3.1/send",
            {
                "Messages": [
                    {
                        "From": {"Email": email, "Name": name},
                        "To": [{"Email": msg.to}],
                        "Subject": msg.subject,
                        "TextPart": msg.text,
                        **({"HTMLPart": msg.html} if msg.html else {}),
                    }
                ]
            },
            {"Authorization": f"Basic {base64.b64encode(credentials).decode()}"},
        )
        # Mailjet v3.1 xato bo'lganda ham HTTP 200 qaytaradi — natija
        # javobning ICHIDA. Buni tekshirmasak zanjir «yuborildi» deb
        # yozadi-yu, xat hech qayerga bormaydi.
        try:
            status = json.loads(body)["Messages"][0]["Status"]
        except (ValueError, KeyError, IndexError, TypeError):
            raise SendError(f"kutilmagan javob: {body[:300]}") from None
        if status != "success":
            raise SendError(f"status={status}: {body[:300]}")


class Resend:
    """https://api.resend.com/emails — bepul 3 000/oy, 100/kun, kartasiz."""

    name = "resend"

    @property
    def configured(self) -> bool:
        return bool(settings.RESEND_API_KEY)

    def send(self, msg: Message) -> None:
        email, name = _sender(self.name)
        _post(
            "https://api.resend.com/emails",
            {
                "from": f"{name} <{email}>",
                "to": [msg.to],
                "subject": msg.subject,
                "text": msg.text,
                **({"html": msg.html} if msg.html else {}),
            },
            {"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
        )


class MailerSend:
    """https://api.mailersend.com/v1/email — bepul 500/oy, karta majburiy."""

    name = "mailersend"

    @property
    def configured(self) -> bool:
        return bool(settings.MAILERSEND_API_KEY)

    def send(self, msg: Message) -> None:
        email, name = _sender(self.name)
        _post(
            "https://api.mailersend.com/v1/email",
            {
                "from": {"email": email, "name": name},
                "to": [{"email": msg.to}],
                "subject": msg.subject,
                "text": msg.text,
                **({"html": msg.html} if msg.html else {}),
            },
            {"Authorization": f"Bearer {settings.MAILERSEND_API_KEY}"},
        )


class Console:
    """Hech qayerga yubormaydi — xabarni logga yozadi.

    Kalitlar hali yo'q, lekin parol tiklash oqimini havolani ko'rmasdan
    sinab bo'lmaydi. `DEBUG` da yoqiladi, ya'ni prodda o'zi tushib qoladi.
    """

    name = "console"

    @property
    def configured(self) -> bool:
        return bool(settings.DEBUG)

    def send(self, msg: Message) -> None:
        log.info("EMAIL → %s | %s\n%s", msg.to, msg.subject, msg.text)


PROVIDERS: dict[str, Brevo | Mailjet | Resend | MailerSend | Console] = {
    provider.name: provider for provider in (Brevo(), Mailjet(), Resend(), MailerSend(), Console())
}
