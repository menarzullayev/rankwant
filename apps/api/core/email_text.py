"""Xat matnlari — o'nta til (ADR-0015).

Nega `gettext` emas: sozlamalarda `USE_I18N` yoqilgan, lekin `locale/`
papkasi bo'sh — hech kim uni ishlatmagan. Uni endi ochish `.po`/`.mo`,
Docker image ga `gettext` va build qadamini olib keladi. Bu yerda esa
bir nechta xat va o'ttizga yaqin satr bor. Lug'at ancha kichik va
shablonlarni matndan butunlay tozalab turadi: tarjima BITTA faylda
yashaydi.

Satrlar ko'payib ketsa `gettext` ga o'tish oson — tuzilma allaqachon
«kalit → til → matn».

⚠️ **There is no fallback locale.** A missing language is the English
property name (`subject`, `cta`), not a silent copy of Uzbek. Coverage
gaps stay visible. `tools/check_email_locales.py` still requires every
string in all ten locales.

Ohang ADR-0015 da tanlangan: xolis va qisqa, salomlashuvsiz. Fishing
xatlari aynan ismi bilan iliq boshlanadi, ya'ni salomlashuv
foydalanuvchini shubhaga o'rgatmaydi.
"""

from __future__ import annotations

import logging

from core.i18n import translate

logger = logging.getLogger(__name__)

#: Locale used when a user record has none. This picks *which dictionary
#: to load*, not a string fallback — `strings()` never copies another
#: language's text.
DEFAULT_LOCALE = "uz"

#: Lug'atlar qaysi tillarda TO'LIQ yozilgan. Ro'yxat ATAYLAB shu yerda —
#: `strings()` shunga qarab zaxira haqida ogohlantiradi, tekshiruv esa
#: (`tools/check_email_locales.py`) shu ro'yxatni kod bilan solishtiradi.
#:
#: `kaa`, `kk`, `ky`, `tg`, `tr`, `zh`, `es` — qo'shildi (qaror 5).
LOCALES = ("uz", "ru", "en", "kaa", "kk", "ky", "tg", "tr", "zh", "es")

#: Xat sarlavhasidagi va footerdagi umumiy satrlar.
SHARED: dict[str, dict[str, str]] = {
    "brand": {
        "uz": "RankWant",
        "ru": "RankWant",
        "en": "RankWant",
        "kaa": "RankWant",
        "kk": "RankWant",
        "ky": "RankWant",
        "tg": "RankWant",
        "tr": "RankWant",
        "zh": "RankWant",
        "es": "RankWant",
    },
    "code_hint": {
        "uz": "Tugma ishlamasa, saytdagi maydonga shu kodni kiriting:",
        "ru": "Если кнопка не работает, введите этот код на сайте:",
        "en": "If the button does not work, enter this code on the site:",
        "kaa": "Tugme islemese, sayttaǵı maydanǵa usı kodtı kiritiń:",
        "kk": "Түйме жұмыс істемесе, сайттағы өріске осы кодты енгізіңіз:",
        "ky": "Баскыч иштебесе, сайттагы талаага ушул кодду киргизиңиз:",
        "tg": "Агар тугма кор накунад, ин кодро дар майдони сайт ворид кунед:",
        "tr": "Düğme çalışmazsa, bu kodu sitedeki alana girin:",
        "zh": "如果按钮无法使用，请在网站上的输入框中输入此代码：",
        "es": "Si el botón no funciona, introduce este código en el sitio:",
    },
    "meta_request": {
        "uz": "So'rov",
        "ru": "Запрос",
        "en": "Request",
        "kaa": "Soraw",
        "kk": "Сұраныс",
        "ky": "Сурамжылоо",
        "tg": "Дархост",
        "tr": "İstek",
        "zh": "请求",
        "es": "Solicitud",
    },
    "meta_ip": {
        "uz": "IP",
        "ru": "IP",
        "en": "IP",
        "kaa": "IP",
        "kk": "IP",
        "ky": "IP",
        "tg": "IP",
        "tr": "IP",
        "zh": "IP",
        "es": "IP",
    },
    "meta_ua": {
        "uz": "Brauzer",
        "ru": "Браузер",
        "en": "Browser",
        "kaa": "Brauzer",
        "kk": "Браузер",
        "ky": "Браузер",
        "tg": "Браузер",
        "tr": "Tarayıcı",
        "zh": "浏览器",
        "es": "Navegador",
    },
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
        "kaa": (
            "Bul xat RankWant esabıńız ushın jiberildi. "
            "Siz soramaǵan bolsańız, itibar bermeń — hesh nárse ózgerpeydi."
        ),
        "kk": (
            "Бұл хат RankWant тіркелгіңіз үшін жіберілді. "
            "Егер сіз сұрамаған болсаңыз, елемеңіз — ештеңе өзгермейді."
        ),
        "ky": (
            "Бул кат RankWant аккаунтуңуз үчүн жөнөтүлдү. "
            "Эгер сиз сурабаган болсоңуз, этибар албаңыз — эч нерсе өзгөрбөйт."
        ),
        "tg": (
            "Ин паём барои ҳисоби RankWant-и шумо фиристода шуд. "
            "Агар шумо онро дархост накарда бошед, нодида гиред — ҳеҷ чиз тағйир намеёбад."
        ),
        "tr": (
            "Bu mesaj RankWant hesabınız için gönderildi. "
            "Talep etmediyseniz yok sayın — hiçbir şey değişmez."
        ),
        "zh": ("此邮件是为您的 RankWant 账户发送的。如果您并未请求，请忽略——不会有任何更改。"),
        "es": (
            "Este mensaje se envió para tu cuenta de RankWant. "
            "Si no lo solicitaste, ignóralo — nada cambiará."
        ),
    },
}

RESET: dict[str, dict[str, str]] = {
    "subject": {
        "uz": "RankWant — parolni tiklash",
        "ru": "RankWant — восстановление пароля",
        "en": "RankWant — password reset",
        "kaa": "RankWant — paroldi tiklew",
        "kk": "RankWant — құпия сөзді қалпына келтіру",
        "ky": "RankWant — сырсөздү калыбына келтирүү",
        "tg": "RankWant — барқарорсозии рамз",
        "tr": "RankWant — parola sıfırlama",
        "zh": "RankWant — 重置密码",
        "es": "RankWant — restablecer contraseña",
    },
    "heading": {
        "uz": "Parolni tiklash",
        "ru": "Восстановление пароля",
        "en": "Password reset",
        "kaa": "Paroldi tiklew",
        "kk": "Құпия сөзді қалпына келтіру",
        "ky": "Сырсөздү калыбына келтирүү",
        "tg": "Барқарорсозии рамз",
        "tr": "Parola sıfırlama",
        "zh": "重置密码",
        "es": "Restablecer contraseña",
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
        "kaa": (
            "Paroldi tiklew sorawı keldi. Tómendegi tugme arqalı jańa parol ornatıń. "
            "Silteme bir saat isleydi hám bir márte isleydi."
        ),
        "kk": (
            "Құпия сөзді қалпына келтіру сұранысы келді. Төмендегі түймемен "
            "жаңа құпия сөзді орнатыңыз. Сілтеме бір сағат жарамды және бір рет істейді."
        ),
        "ky": (
            "Сырсөздү калыбына келтирүү сурамы келди. Төмөнкү баскыч аркылуу жаңы сырсөздү коюңуз. "
            "Шилтеме бир саат жарактуу жана бир жолу иштейт."
        ),
        "tg": (
            "Дархости барқарорсозии рамз расид. Рамзи навро бо тугмаи зер ворид кунед. "
            "Пайванд як соат эътибор дорад ва як бор кор мекунад."
        ),
        "tr": (
            "Parola sıfırlama isteği alındı. Aşağıdaki düğmeyle yeni parolanızı belirleyin. "
            "Bağlantı bir saat geçerlidir ve bir kez çalışır."
        ),
        "zh": (
            "收到重置密码的请求。请通过下方按钮设置新密码。链接有效期为 1 小时，且仅可使用一次。"
        ),
        "es": (
            "Se solicitó un restablecimiento de contraseña. Establece una nueva "
            "con el botón de abajo. El enlace es válido durante una hora y funciona una sola vez."
        ),
    },
    "cta": {
        "uz": "Yangi parol o'rnatish",
        "ru": "Установить новый пароль",
        "en": "Set a new password",
        "kaa": "Jańa parol ornatıw",
        "kk": "Жаңа құпия сөзді орнату",
        "ky": "Жаңы сырсөздү коюу",
        "tg": "Рамзи нав ворид кардан",
        "tr": "Yeni parola belirle",
        "zh": "设置新密码",
        "es": "Establecer nueva contraseña",
    },
}

VERIFY: dict[str, dict[str, str]] = {
    "subject": {
        "uz": "RankWant — emailni tasdiqlang",
        "ru": "RankWant — подтвердите email",
        "en": "RankWant — confirm your email",
        "kaa": "RankWant — emaildı tastıyıqlań",
        "kk": "RankWant — emailді растаңыз",
        "ky": "RankWant — email ды ырастаңыз",
        "tg": "RankWant — emailро тасдиқ кунед",
        "tr": "RankWant — e-postanızı doğrulayın",
        "zh": "RankWant — 确认您的邮箱",
        "es": "RankWant — confirma tu correo",
    },
    "heading": {
        "uz": "Emailni tasdiqlash",
        "ru": "Подтверждение email",
        "en": "Confirm your email",
        "kaa": "Emaildı tastıyıqlaw",
        "kk": "Emailді растау",
        "ky": "Emailды ырастоо",
        "tg": "Тасдиқи email",
        "tr": "E-postayı doğrulama",
        "zh": "确认邮箱",
        "es": "Confirmar correo",
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
        "kaa": (
            "Bul mánzil RankWant esabına baylandı. Tastıyıqlaw ushın tómendegi tugmeni basıń. "
            "Silteme bir saat isleydi hám bir márte isleydi."
        ),
        "kk": (
            "Бұл мекенжай RankWant тіркелгісіне байланды. Растау үшін төмендегі түймені басыңыз. "
            "Сілтеме бір сағат жарамды және бір рет істейді."
        ),
        "ky": (
            "Бул дарек RankWant аккаунтуна байланды. Ырастоо үчүн төмөнкү баскычты басыңыз. "
            "Шилтеме бир саат жарактуу жана бир жолу иштейт."
        ),
        "tg": (
            "Ин суроға ба ҳисоби RankWant пайваст шуд. Барои тасдиқ тугмаи зерро пахш кунед. "
            "Пайванд як соат эътибор дорад ва як бор кор мекунад."
        ),
        "tr": (
            "Bu adres bir RankWant hesabına bağlandı. Doğrulamak için aşağıdaki düğmeye basın. "
            "Bağlantı bir saat geçerlidir ve bir kez çalışır."
        ),
        "zh": (
            "此地址已绑定到 RankWant 账户。请通过下方按钮进行确认。"
            "链接有效期为 1 小时，且仅可使用一次。"
        ),
        "es": (
            "Esta dirección se vinculó a una cuenta de RankWant. Confírmala con el botón de abajo. "
            "El enlace es válido durante una hora y funciona una sola vez."
        ),
    },
    "cta": {
        "uz": "Emailni tasdiqlash",
        "ru": "Подтвердить email",
        "en": "Confirm email",
        "kaa": "Emaildı tastıyıqlaw",
        "kk": "Emailді растау",
        "ky": "Emailды ырастоо",
        "tg": "Тасдиқи email",
        "tr": "E-postayı doğrula",
        "zh": "确认邮箱",
        "es": "Confirmar correo",
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
        "kaa": "RankWant: pochta mánzilińiz ózgertildi",
        "kk": "RankWant: пошта мекенжайыңыз өзгертілді",
        "ky": "RankWant: почта дарегиңиз өзгөртүлдү",
        "tg": "RankWant: суроғаи почтаи шумо тағйир ёфт",
        "tr": "RankWant: e-posta adresiniz değiştirildi",
        "zh": "RankWant：您的邮箱地址已更改",
        "es": "RankWant: tu dirección de correo cambió",
    },
    "heading": {
        "uz": "Pochta manzili almashtirildi",
        "ru": "Адрес почты изменён",
        "en": "Email address changed",
        "kaa": "Pochta mánzili ózgertildi",
        "kk": "Пошта мекенжайы өзгертілді",
        "ky": "Почта дареги өзгөртүлдү",
        "tg": "Суроғаи почта тағйир ёфт",
        "tr": "E-posta adresi değiştirildi",
        "zh": "邮箱地址已更改",
        "es": "Dirección de correo cambiada",
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
        "kaa": (
            "Esabıńızdıń pochta mánzili basqa mánzilge ózgertildi hám bul mánzilge "
            "endi xat kelmeydi. Bunı siz qılmaǵan bolsańız, esabıńızǵa derhal kiriń, "
            "paroldı ózgertіń hám barlıq sessiyalardı jappıń."
        ),
        "kk": (
            "Тіркелгіңіздің пошта мекенжайы өзгертілді, енді бұл мекенжайға хат "
            "келмейді. Егер бұл сіз болмасаңыз, дереу тіркелгіңізге кіріңіз, құпия "
            "сөзді ауыстырыңыз және барлық сеанстарды жабыңыз."
        ),
        "ky": (
            "Аккаунтуңуздун почта дареги өзгөртүлдү, эми бул дарекке кат келбейт. "
            "Эгер бул сиз болбосоңуз, дароо аккаунтуңузга кириңиз, сырсөздү "
            "алмаштырыңыз жана бардык сессияларды жабыңыз."
        ),
        "tg": (
            "Суроғаи почтаи ҳисоби шумо тағйир ёфт ва дигар ба ин суроға паём "
            "намеояд. Агар ин шумо набошед, фавран ба ҳисоби худ ворид шавед, "
            "рамзро иваз кунед ва ҳамаи сессияҳоро бандед."
        ),
        "tr": (
            "Hesabınızın e-posta adresi değiştirildi ve bu adrese artık mesaj "
            "gelmeyecek. Bunu siz yapmadıysanız hemen hesabınıza girin, parolanızı "
            "değiştirin ve tüm oturumları kapatın."
        ),
        "zh": (
            "您账户的邮箱地址已更改，此地址将不再收到邮件。"
            "如果并非您本人操作，请立即登录账户、更改密码并结束所有会话。"
        ),
        "es": (
            "La dirección de correo de tu cuenta cambió y esta dirección ya no "
            "recibirá mensajes. Si no fuiste tú, inicia sesión de inmediato, "
            "cambia tu contraseña y cierra todas las sesiones."
        ),
    },
    "cta": {
        "uz": "Hisobga kirish",
        "ru": "Войти в аккаунт",
        "en": "Sign in",
        "kaa": "Esabqa kiriw",
        "kk": "Тіркелгіге кіру",
        "ky": "Аккаунтка кирүү",
        "tg": "Ворид шудан ба ҳисоб",
        "tr": "Hesaba giriş yap",
        "zh": "登录账户",
        "es": "Iniciar sesión",
    },
}


def strings(table: dict[str, dict[str, str]], locale: str) -> dict[str, str]:
    """Flatten one locale. Missing text is the English property name.

    There is no fallback language. An unknown locale, or a row without
    that locale, returns the property (`subject`, `cta`) so the gap is
    visible instead of an Uzbek letter.
    """
    if locale not in LOCALES:
        logger.warning(
            "email_text: locale %r has no dictionary — property names will be used",
            locale,
        )
    properties = tuple(table)
    texts = translate(locale, *properties, catalog=table)
    if isinstance(texts, str):
        texts = (texts,)
    return dict(zip(properties, texts, strict=True))
