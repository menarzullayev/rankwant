"""Xat matnlari — uz / ru / en (ADR-0015).

Nega `gettext` emas: sozlamalarda `USE_I18N` yoqilgan, lekin `locale/`
papkasi bo'sh — hech kim uni ishlatmagan. Uni endi ochish `.po`/`.mo`,
Docker image ga `gettext` va build qadamini olib keladi. Bu yerda esa
ikkita xat va o'ttizga yaqin satr bor. Lug'at ancha kichik va shablonlarni
matndan butunlay tozalab turadi: tarjima BITTA faylda yashaydi.

Satrlar ko'payib ketsa `gettext` ga o'tish oson — tuzilma allaqachon
«kalit → til → matn».

Ohang ADR-0015 da tanlangan: xolis va qisqa, salomlashuvsiz. Fishing
xatlari aynan ismi bilan iliq boshlanadi, ya'ni salomlashuv foydalanuvchini
shubhaga o'rgatmaydi.
"""

from __future__ import annotations

DEFAULT_LOCALE = "uz"

#: Xat sarlavhasidagi va footerdagi umumiy satrlar.
SHARED: dict[str, dict[str, str]] = {
    "brand": {"uz": "RankWant", "ru": "RankWant", "en": "RankWant"},
    "code_hint": {
        "uz": "Tugma ishlamasa, saytdagi maydonga shu kodni kiriting:",
        "ru": "Если кнопка не работает, введите этот код на сайте:",
        "en": "If the button does not work, enter this code on the site:",
    },
    "meta_request": {"uz": "So'rov", "ru": "Запрос", "en": "Request"},
    "meta_ip": {"uz": "IP", "ru": "IP", "en": "IP"},
    "meta_ua": {"uz": "Brauzer", "ru": "Браузер", "en": "Browser"},
    "footer": {
        "uz": (
            "Bu xat RankWant hisobingiz uchun yuborildi. "
            "Siz so'ramagan bo'lsangiz, e'tibor bermang — hech narsa o'zgarmaydi."
        ),
        "ru": (
            "Это письмо отправлено для вашего аккаунта RankWant. "
            "Если вы его не запрашивали, просто проигнорируйте — ничего не изменится."
        ),
        "en": (
            "This message was sent for your RankWant account. "
            "If you did not request it, ignore it — nothing will change."
        ),
    },
}

RESET: dict[str, dict[str, str]] = {
    "subject": {
        "uz": "RankWant — parolni tiklash",
        "ru": "RankWant — восстановление пароля",
        "en": "RankWant — password reset",
    },
    "heading": {
        "uz": "Parolni tiklash",
        "ru": "Восстановление пароля",
        "en": "Password reset",
    },
    "body": {
        "uz": (
            "Parolni tiklash so'rovi keldi. Quyidagi tugma orqali yangi parol o'rnating. "
            "Havola bir soat amal qiladi va bir marta ishlaydi."
        ),
        "ru": (
            "Поступил запрос на восстановление пароля. Установите новый пароль по кнопке ниже. "
            "Ссылка действует один час и срабатывает один раз."
        ),
        "en": (
            "A password reset was requested. Set a new password with the button below. "
            "The link is valid for one hour and works once."
        ),
    },
    "cta": {
        "uz": "Yangi parol o'rnatish",
        "ru": "Установить новый пароль",
        "en": "Set a new password",
    },
}

VERIFY: dict[str, dict[str, str]] = {
    "subject": {
        "uz": "RankWant — emailni tasdiqlang",
        "ru": "RankWant — подтвердите email",
        "en": "RankWant — confirm your email",
    },
    "heading": {
        "uz": "Emailni tasdiqlash",
        "ru": "Подтверждение email",
        "en": "Confirm your email",
    },
    "body": {
        "uz": (
            "Bu manzil RankWant hisobiga bog'landi. Tasdiqlash uchun quyidagi tugmani bosing. "
            "Havola bir soat amal qiladi va bir marta ishlaydi."
        ),
        "ru": (
            "Этот адрес привязан к аккаунту RankWant. Нажмите кнопку ниже, чтобы подтвердить. "
            "Ссылка действует один час и срабатывает один раз."
        ),
        "en": (
            "This address was attached to a RankWant account. Confirm it with the button below. "
            "The link is valid for one hour and works once."
        ),
    },
    "cta": {
        "uz": "Emailni tasdiqlash",
        "ru": "Подтвердить email",
        "en": "Confirm email",
    },
}


#: Eski manzilga — pochta almashtirilgach. Parolni tiklash tavsiya
#: QILINMAYDI: hisobni egallagan odam pochtani o'zinikiga almashtirgan
#: bo'lsa, tiklash havolasi endi aynan unga boradi.
CHANGED: dict[str, dict[str, str]] = {
    "subject": {
        "uz": "RankWant: pochta manzilingiz almashtirildi",
        "ru": "RankWant: адрес почты изменён",
        "en": "RankWant: your email address was changed",
    },
    "heading": {
        "uz": "Pochta manzili almashtirildi",
        "ru": "Адрес почты изменён",
        "en": "Email address changed",
    },
    "body": {
        "uz": (
            "Hisobingizning pochta manzili boshqa manzilga almashtirildi va bu "
            "manzilga endi xat kelmaydi. Buni siz qilmagan bo'lsangiz, hisobingizga "
            "darhol kiring, parolni almashtiring va barcha sessiyalarni yoping."
        ),
        "ru": (
            "Адрес почты вашего аккаунта изменён, и на этот адрес письма больше "
            "приходить не будут. Если это были не вы, сразу войдите в аккаунт, "
            "смените пароль и завершите все сеансы."
        ),
        "en": (
            "The email address on your account was changed, and this address will "
            "no longer receive messages. If this was not you, sign in right away, "
            "change your password and end all sessions."
        ),
    },
    "cta": {"uz": "Hisobga kirish", "ru": "Войти в аккаунт", "en": "Sign in"},
}


def strings(table: dict[str, dict[str, str]], locale: str) -> dict[str, str]:
    """Bitta til uchun satrlarni tekislaydi. Noma'lum til — o'zbekcha."""
    if locale not in ("uz", "ru", "en"):
        locale = DEFAULT_LOCALE
    return {key: values.get(locale, values[DEFAULT_LOCALE]) for key, values in table.items()}
