/** Huquqiy sahifalar matni — ADR-0015.
 *
 * ⚠️ Ilgari bu yerda ADR-0016 yozilgan edi — u ro'yxatdan o'tish va kirish
 * haqida, huquqiy matn tillari haqida emas. Uch tilli qoida (uz/ru/en)
 * ADR-0015 dan keladi: o'sha yerda xat tillari ham aynan shu uchtasi.
 * Havola mavjud faylga ishora qilardi, shuning uchun uni na til, na tip,
 * na havola tekshiruvi ushlay olmaydi — faqat qo'lda o'qish.
 *
 * Tarjima lug'atida EMAS: bular uzun matnlar va `messages.ts` dagi qisqa
 * satrlar bilan bir joyda turishi ikkalasini ham o'qib bo'lmas qilardi.
 *
 * Uch tilda: uz, ru, en — `User.locale` da aynan shu uchtasi bor
 * (ADR-0015 dagi xat tillari bilan bir xil). Qolgan tillar o'zbekchaga
 * tushadi.
 *
 * Matn ATAYLAB aniq: har bir band biz haqiqatan qiladigan ishni yozadi.
 * Umumiy shablon matn foydasiz — u nima yig'ilishini ham, nima
 * qilinmasligini ham aytmaydi.
 */

export type LegalDoc = {
  title: string;
  updated: string;
  intro: string;
  sections: { h: string; p: string[] }[];
};

export type LegalLocale = "uz" | "ru" | "en";

const UPDATED = "2026-09-10";

/** Maxfiylik matni sanasi — shartlardan alohida: 2026-11-10 da faqat shu
 *  matn yangilandi (audit Q-06). ⚠️ Yurist hali ko'rmagan — legal brief § 5. */
const PRIVACY_UPDATED = "2026-11-10";

export const PRIVACY: Record<LegalLocale, LegalDoc> = {
  uz: {
    title: "Maxfiylik siyosati",
    updated: PRIVACY_UPDATED,
    intro:
      "Bu sahifa RankWant qanday ma'lumot yig'ishini, nima uchun va qancha vaqt saqlashini aytadi. Har bir band platformada haqiqatan bajariladigan ishni tasvirlaydi.",
    sections: [
      {
        h: "Nima yig'iladi",
        p: [
          "Hisob: taxallus, email manzil, ism va familiya hamda parolning kriptografik xesh qiymati. Parolning o'zi hech qachon saqlanmaydi va uni tiklab bo'lmaydi. Ism va familiyadan profilda ko'rinadigan ism yasaladi.",
          "Profil — ixtiyoriy, o'zingiz to'ldirasiz: qisqa ma'lumot, avatar havolasi, til, Telegram identifikatori, mamlakat, viloyat, tuman yoki shahar, ta'lim bosqichi, maktab yoki o'quv yurti, sinf yoki kurs, mutaxassislik, ta'lim va ish tarixi, ko'nikmalar, jamoalar, boshqa saytlardagi profillaringiz va veb-sayt havolalari, telefon raqami, tug'ilgan sana, jins va futbolka o'lchami.",
          "Sovrin yetkazish — faqat alohida rozilik bersangiz: qabul qiluvchining ismi va pochta manzili.",
          "Faoliyat: yuborilgan yechimlar va ularning kodi, verdiktlar, reytinglar, musobaqa natijalari, Qvant tranzaksiyalari va saytdagi faollik tarixi (yechilgan masalalar, yutuqlar).",
          "Texnik: har bir kirish sessiyasi uchun IP manzil va brauzer nomi — ularni sozlamalardagi «Qurilmalar» bo'limida ko'rasiz va istalgan sessiyani yopasiz. Parolni tiklash so'rovida IP manzil va brauzer nomi xatda ham ko'rsatiladi — so'rovni o'zingiz yubormaganingizni bilishingiz uchun. Noto'g'ri kirish urinishlari IP manzil va kiritilgan nomning xesh qiymati bo'yicha sanaladi (nomning o'zi emas). Musobaqa paytida yuborilgan har yechim bilan muharrirda nechta belgi joylangani, sahifadan necha marta chiqilgani va sahifa qancha ochiq turgani yoziladi — faqat shu musobaqa hakami ko'radi.",
          "Import qilingan profillar: platformada Codeforces'ning ochiq profillaridan olingan 974 mingga yaqin hisob bor — taxallus, egasi o'sha saytda ochiq ko'rsatgan ism, mamlakat, shahar va tashkilot hamda avatar havolasi. Ularda email va parol yo'q: bu hisoblar orqali kirib bo'lmaydi va ularning sahifalari qidiruv tizimlariga yopiq.",
        ],
      },
      {
        h: "Nima uchun",
        p: [
          "Platformani ishlatish: hisobingizni tanish, yechimlarni tekshirish, reyting hisoblash, musobaqa jadvalini qurish.",
          "Profil ma'lumotlari — profilingizda ko'rsatish uchun. Qaysi maydon ommaviy bo'lishini o'zingiz tanlaysiz (pastda «Kim ko'radi»).",
          "Suiiste'moldan himoya: so'rovlar sonini cheklash, ko'p hisob va taqlidning oldini olish, ro'yxatdan o'tishda bot tekshiruvi.",
          "Hisobni tiklash: parolni unutganda pochtaga havola yuborish.",
          "Email bildirishnomalari — faqat siz sozlamalarda yoqqan turlar uchun (standart holatda hammasi o'chiq), faqat tasdiqlangan manzilga va faqat sizga tegishli xabar: musobaqa natijasi, duel, hack va hokazo. Har xatda shu turni yoki barcha xatlarni bitta bosishda o'chiradigan havola bor.",
          "Sovrin yuborish — faqat rozilik berganingizda.",
        ],
      },
      {
        h: "Kim ko'radi",
        p: [
          "Profilning ommaviy qismi saytga kirgan har kimga ko'rinadi. Doim ommaviy: taxallus, ko'rsatiladigan ism, qisqa ma'lumot, avatar, reyting va yechilgan masalalar. Standart holatda ommaviy, lekin sozlamalardagi maxfiylik jadvalida yashirish mumkin: mamlakat va hudud, maktab, sinf, tug'ilgan sana, jins, veb-sayt, boshqa saytlardagi profillar, murabbiylar va onlayn holat. Email standart holatda yashirin.",
          "Telefon raqami, sovrin manzili, ta'lim bosqichi va mutaxassislik hech qachon ommaviy ko'rsatilmaydi — ularni faqat siz ko'rasiz.",
          "Yechimlaringiz kodini siz va platforma xodimlari ko'radi; hack bosqichi bor musobaqada shu bosqich davomida shu musobaqa ishtirokchilari ham ko'rishi mumkin. Verdikt va natijalar jadvallarda ko'rinadi.",
        ],
      },
      {
        h: "Kim bilan ulashiladi",
        p: [
          "Xat yuborish provayderlari — Brevo, Mailjet, Resend, MailerSend. Ularga faqat qabul qiluvchi manzil va xat matni beriladi.",
          "Cloudflare — sayt trafigi shu tarmoq orqali o'tadi; ro'yxatdan o'tishdagi bot tekshiruvi (Turnstile) ham Cloudflare'niki.",
          "Ijtimoiy kirishdan foydalansangiz, tanlagan provayderingiz (Google, GitHub, Telegram) bizga sizning identifikatoringiz va email manzilingizni beradi.",
          "Boshqa hech kimga berilmaydi va hech qachon sotilmaydi.",
        ],
      },
      {
        h: "Qancha saqlanadi",
        p: [
          "Hisob va faoliyat — hisob mavjud ekan.",
          "Kirish sessiyasining IP manzili va brauzer nomi — sessiya amal qilguncha («Meni eslab qol» bilan eng ko'pi 30 kun); muddati tugagan yozuvlar har kuni o'chiriladi.",
          "Noto'g'ri kirish urinishlari hisobi — bir soat.",
          "Parolni tiklash havolasi va kodi — bir soat, keyin ular ishlamaydi.",
          "Yuborilgan xatlarning TANASI umuman saqlanmaydi: tiklash havolasi tokendir, uni bazaga ko'chirish uni ikkinchi joyda qoldirish bo'lardi. Faqat qachon, kimga va qaysi provayder orqali yuborilgani yoziladi.",
          "Hisobni o'chirish so'rovi 14 kun kutadi — shu vaqt ichida bekor qilishingiz mumkin — keyin shaxsiy ma'lumot o'chiriladi.",
        ],
      },
      {
        h: "Sizning huquqingiz",
        p: [
          "Ma'lumotingizni istalgan vaqt yuklab olishingiz mumkin — sozlamalar sahifasida eksport tugmasi bor.",
          "Hisobni o'chirishingiz mumkin. So'rovdan 14 kun o'tgach shaxsiy ma'lumot — taxallus, email, ism va familiya, avatar, Telegram, manzil, ta'lim, telefon, tug'ilgan sana, jins, sovrin manzili va boshqa profil maydonlari — o'chiriladi va hisob anonim nom oladi. Yechimlar va musobaqa natijalari saqlanib qoladi, chunki ular boshqa ishtirokchilarning jadvaliga ham tegishli.",
          "Qaysi profil maydoni ommaviy bo'lishini maxfiylik jadvalida o'zgartirasiz.",
          "Import qilingan profil sizniki bo'lsa yoki savolingiz bo'lsa yozing — aloqa manzili sayt pastida.",
        ],
      },
      {
        h: "Bolalar",
        p: [
          "Platforma maktab o'quvchilari uchun ham mo'ljallangan. Tug'ilgan sana ixtiyoriy: onboarding uni so'raydi, lekin bo'sh qoldirish mumkin. Kiritilsa, u standart holatda ommaviy profilda ko'rinadi — maxfiylik jadvalida yashirish mumkin. Yosh tekshirilmaydi.",
        ],
      },
    ],
  },
  ru: {
    title: "Политика конфиденциальности",
    updated: PRIVACY_UPDATED,
    intro:
      "Эта страница рассказывает, какие данные собирает RankWant, зачем и как долго их хранит. Каждый пункт описывает то, что платформа действительно делает.",
    sections: [
      {
        h: "Что собирается",
        p: [
          "Аккаунт: имя пользователя, адрес email, имя и фамилия, а также криптографический хеш пароля. Сам пароль никогда не хранится, и восстановить его нельзя. Из имени и фамилии составляется имя, видимое в профиле.",
          "Профиль — по желанию, заполняете вы сами: краткая информация, ссылка на аватар, язык, идентификатор Telegram, страна, область, район или город, ступень образования, школа или учебное заведение, класс или курс, специальность, история учёбы и работы, навыки, команды, ваши профили на других сайтах и ссылки на сайты, номер телефона, дата рождения, пол и размер футболки.",
          "Доставка призов — только с отдельного согласия: имя получателя и почтовый адрес.",
          "Активность: отправленные решения и их код, вердикты, рейтинги, результаты соревнований, транзакции Qvant и история активности на сайте (решённые задачи, достижения).",
          "Технические данные: для каждого входа — IP-адрес и название браузера; их видно в настройках в разделе «Устройства», там же любую сессию можно завершить. При запросе сброса пароля IP-адрес и браузер указываются и в письме — чтобы вы знали, если запрос отправили не вы. Неудачные попытки входа считаются по IP-адресу и хешу введённого имени (не по самому имени). С каждым решением, отправленным во время соревнования, записывается, сколько символов вставлено в редактор, сколько раз вы уходили со страницы и сколько она была открыта, — это видит только жюри соревнования.",
          "Импортированные профили: на платформе около 974 тысяч аккаунтов из открытых профилей Codeforces — имя пользователя, имя, которое владелец открыто указал на том сайте, страна, город, организация и ссылка на аватар. У них нет email и пароля: через них нельзя войти, а их страницы закрыты для поисковых систем.",
        ],
      },
      {
        h: "Зачем",
        p: [
          "Работа платформы: узнать ваш аккаунт, проверить решения, посчитать рейтинг, построить таблицу соревнования.",
          "Данные профиля — чтобы показать их в вашем профиле. Какие поля публичны, выбираете вы сами (см. ниже «Кто видит»).",
          "Защита от злоупотреблений: ограничение числа запросов, предотвращение мультиаккаунтов и выдачи себя за других, проверка на ботов при регистрации.",
          "Восстановление аккаунта: отправить ссылку на почту, если вы забыли пароль.",
          "Уведомления по почте — только для типов, которые вы сами включили в настройках (по умолчанию все выключены), только на подтверждённый адрес и только о том, что касается вас: результат соревнования, дуэль, взлом и т. п. В каждом письме есть ссылка, которая одним нажатием отключает этот тип писем или все письма.",
          "Отправка призов — только если вы дали согласие.",
        ],
      },
      {
        h: "Кто видит",
        p: [
          "Публичная часть профиля видна любому посетителю сайта. Всегда публичны: имя пользователя, отображаемое имя, краткая информация, аватар, рейтинг и решённые задачи. По умолчанию публичны, но их можно скрыть в таблице приватности в настройках: страна и регион, школа, класс, дата рождения, пол, сайт, профили на других сайтах, тренеры и статус «в сети». Email по умолчанию скрыт.",
          "Номер телефона, адрес для призов, ступень образования и специальность никогда не показываются публично — их видите только вы.",
          "Код ваших решений видите вы и сотрудники платформы; в соревновании с фазой взломов его в эту фазу могут видеть и участники этого соревнования. Вердикты и результаты видны в таблицах.",
        ],
      },
      {
        h: "Кому передаётся",
        p: [
          "Сервисам отправки писем — Brevo, Mailjet, Resend, MailerSend. Им передаются только адрес получателя и текст письма.",
          "Cloudflare — трафик сайта проходит через эту сеть; проверка на ботов при регистрации (Turnstile) тоже принадлежит Cloudflare.",
          "Если вы входите через соцсеть, выбранный провайдер (Google, GitHub, Telegram) передаёт нам ваш идентификатор и адрес email.",
          "Больше никому не передаётся и никогда не продаётся.",
        ],
      },
      {
        h: "Сколько хранится",
        p: [
          "Аккаунт и активность — пока существует аккаунт.",
          "IP-адрес и браузер сессии входа — пока сессия действует (с «Запомнить меня» не более 30 дней); записи истёкших сессий удаляются ежедневно.",
          "Счётчик неудачных попыток входа — один час.",
          "Ссылка и код сброса пароля — один час, после этого они не работают.",
          "ТЕЛО отправленных писем не хранится вовсе: ссылка сброса — это токен, и копия в базе оставила бы его во втором месте. Записывается только когда, кому и через какого провайдера отправлено.",
          "Запрос на удаление аккаунта ждёт 14 дней — за это время его можно отменить, — затем личные данные удаляются.",
        ],
      },
      {
        h: "Ваши права",
        p: [
          "Вы можете в любой момент скачать свои данные — в настройках есть кнопка экспорта.",
          "Вы можете удалить аккаунт. Через 14 дней после запроса личные данные — имя пользователя, email, имя и фамилия, аватар, Telegram, адрес, образование, телефон, дата рождения, пол, адрес для призов и остальные поля профиля — удаляются, а аккаунт получает анонимное имя. Решения и результаты соревнований сохраняются, потому что они относятся и к таблицам других участников.",
          "Какие поля профиля публичны, вы меняете в таблице приватности.",
          "Если импортированный профиль ваш или у вас есть вопрос, напишите нам — адрес для связи внизу сайта.",
        ],
      },
      {
        h: "Дети",
        p: [
          "Платформа рассчитана в том числе на школьников. Дата рождения необязательна: онбординг её спрашивает, но поле можно оставить пустым. Если её указать, по умолчанию она видна в публичном профиле — её можно скрыть в таблице приватности. Возраст не проверяется.",
        ],
      },
    ],
  },
  en: {
    title: "Privacy policy",
    updated: PRIVACY_UPDATED,
    intro:
      "This page says what data RankWant collects, why, and how long it keeps it. Every item describes something the platform actually does.",
    sections: [
      {
        h: "What is collected",
        p: [
          "Account: username, email address, first and last name, and a cryptographic hash of your password. The password itself is never stored and cannot be recovered. Your first and last name make up the name shown on your profile.",
          "Profile — optional, filled in by you: a short bio, avatar link, language, Telegram id, country, region, district or city, education stage, school or institution, grade or year, specialty, education and work history, skills, teams, your profiles on other sites and website links, phone number, date of birth, gender and T-shirt size.",
          "Prize delivery — only with separate consent: the recipient's name and postal address.",
          "Activity: submitted solutions and their code, verdicts, ratings, contest results, Qvant transactions and your activity history on the site (solved problems, achievements).",
          "Technical: for every sign-in session, the IP address and browser name — you see them under Devices in your settings and can end any session there. A password reset request also shows the IP address and browser in the email, so you know if someone else sent it. Failed sign-in attempts are counted by IP address and by a hash of the name typed (not the name itself). With each solution sent during a contest, the number of characters pasted into the editor, how often you left the page and how long it was open are recorded — only that contest's jury sees them.",
          "Imported profiles: the platform holds about 974 thousand accounts taken from public Codeforces profiles — the username, the name the owner made public there, country, city, organisation and avatar link. They have no email or password: no one can sign in through them, and their pages are closed to search engines.",
        ],
      },
      {
        h: "Why",
        p: [
          "Running the platform: recognising your account, judging solutions, computing ratings, building contest standings.",
          "Profile details — to show them on your profile. You choose which fields are public (see Who can see it, below).",
          "Abuse protection: rate limits, preventing multiple accounts and impersonation, a bot check at sign-up.",
          "Account recovery: emailing you a link when you forget your password.",
          "Notification emails — only for the kinds you switch on in your settings (all are off by default), only to a confirmed address and only about you: a contest result, a duel, a hack and so on. Every such email has a link that turns off that kind, or all of them, in one click.",
          "Sending prizes — only if you consented.",
        ],
      },
      {
        h: "Who can see it",
        p: [
          "The public part of your profile is visible to any visitor. Always public: username, display name, bio, avatar, ratings and solved problems. Public by default, but you can hide them in the privacy table in your settings: country and region, school, grade, date of birth, gender, website, profiles on other sites, coaches and online status. Email is hidden by default.",
          "Your phone number, prize address, education stage and specialty are never shown publicly — only you see them.",
          "Your solution code is seen by you and platform staff; in a contest with a hacking phase, that contest's participants may see it during the phase. Verdicts and results appear in standings.",
        ],
      },
      {
        h: "Who it is shared with",
        p: [
          "Email providers — Brevo, Mailjet, Resend, MailerSend. They receive only the recipient address and the message body.",
          "Cloudflare — site traffic passes through its network; the bot check at sign-up (Turnstile) is Cloudflare's too.",
          "If you sign in with a social account, the provider you choose (Google, GitHub, Telegram) gives us your identifier and email address.",
          "Nobody else receives it, and it is never sold.",
        ],
      },
      {
        h: "How long it is kept",
        p: [
          "Account and activity — as long as the account exists.",
          "A sign-in session's IP address and browser — while the session is valid (at most 30 days with Remember me); rows of expired sessions are deleted daily.",
          "The count of failed sign-in attempts — one hour.",
          "Password reset link and code — one hour, after which they stop working.",
          "The BODY of sent emails is not stored at all: a reset link is a token, and copying it into the database would leave it in a second place. Only when, to whom and through which provider an email went is recorded.",
          "An account deletion request waits 14 days — you can cancel it in that time — and then personal data is removed.",
        ],
      },
      {
        h: "Your rights",
        p: [
          "You can download your data at any time — the settings page has an export button.",
          "You can delete your account. Fourteen days after the request, personal data — username, email, first and last name, avatar, Telegram, address, education, phone, date of birth, gender, prize address and the other profile fields — is removed and the account gets an anonymous name. Solutions and contest results are kept, because they also belong to other participants' standings.",
          "You change which profile fields are public in the privacy table.",
          "If an imported profile is yours, or you have a question, write to us — the contact address is at the bottom of the site.",
        ],
      },
      {
        h: "Children",
        p: [
          "The platform is meant for school students too. Date of birth is optional: onboarding asks for it, but you can leave it empty. If you enter it, it is shown on your public profile by default — you can hide it in the privacy table. Age is not verified.",
        ],
      },
    ],
  },
};

export const TERMS: Record<LegalLocale, LegalDoc> = {
  uz: {
    title: "Foydalanish shartlari",
    updated: UPDATED,
    intro:
      "RankWant — sport dasturlash platformasi. Bu sahifa undan foydalanish qoidalarini aytadi.",
    sections: [
      {
        h: "Hisob",
        p: [
          "Bir odam — bitta hisob. Ko'p hisob reyting va musobaqa natijalarini buzadi.",
          "Taxallus boshqa ishtirokchiga taqlid qilmasligi kerak. Ko'zga o'xshash harflar bilan olingan nom tizim tomonidan rad etiladi.",
          "Hisobingiz xavfsizligi sizning zimmangizda: parolni boshqalarga bermang.",
        ],
      },
      {
        h: "Musobaqa halolligi",
        p: [
          "Musobaqa davomida yechimni boshqalar bilan ulashish yoki boshqadan olish taqiqlanadi.",
          "Boshqa ishtirokchining kodini o'zingiznikidek yuborish plagiat hisoblanadi.",
          "Buzilish aniqlansa natija bekor qilinadi; takrorlansa hisob cheklanadi.",
        ],
      },
      {
        h: "Kontent",
        p: [
          "Yuborgan kodingiz sizniki bo'lib qoladi. Biz uni faqat tekshirish, statistika va plagiat aniqlash uchun ishlatamiz.",
          "Masala matnlari mualliflarga tegishli. KEP.uz arxividan olingan masalalar egalarining ruxsati bilan ko'chirilgan.",
          "Platforma matnlarini ruxsatsiz ko'chirib boshqa joyda e'lon qilish mumkin emas.",
        ],
      },
      {
        h: "Qvant",
        p: [
          "Qvant — platforma ichidagi ball. Uning pul qiymati yo'q, sotib olinmaydi, sotilmaydi va naqd pulga almashtirilmaydi.",
          "Qvant faqat platforma ichida ishlatiladi va hisob o'chirilganda yo'qoladi.",
        ],
      },
      {
        h: "Xizmat",
        p: [
          "Platforma hozircha rivojlanish bosqichida: xususiyatlar o'zgarishi, vaqtincha ishlamay qolishi mumkin.",
          "Qoidalarni buzgan hisobni cheklash yoki o'chirish huquqini o'zimizda qoldiramiz.",
          "Shartlar o'zgarsa, sahifadagi sana yangilanadi.",
        ],
      },
    ],
  },
  ru: {
    title: "Условия использования",
    updated: UPDATED,
    intro:
      "RankWant — платформа спортивного программирования. Эта страница описывает правила её использования.",
    sections: [
      {
        h: "Аккаунт",
        p: [
          "Один человек — один аккаунт. Несколько аккаунтов искажают рейтинг и результаты соревнований.",
          "Имя пользователя не должно подражать другому участнику. Имя, взятое с помощью визуально похожих букв, отклоняется системой.",
          "Безопасность аккаунта — ваша ответственность: не передавайте пароль другим.",
        ],
      },
      {
        h: "Честность соревнований",
        p: [
          "Во время соревнования запрещено передавать решение другим или получать его от других.",
          "Отправка чужого кода как своего считается плагиатом.",
          "При обнаружении нарушения результат аннулируется; при повторе аккаунт ограничивается.",
        ],
      },
      {
        h: "Контент",
        p: [
          "Отправленный вами код остаётся вашим. Мы используем его только для проверки, статистики и выявления плагиата.",
          "Тексты задач принадлежат их авторам. Задачи из архива KEP.uz перенесены с разрешения владельцев.",
          "Копировать материалы платформы и публиковать их в другом месте без разрешения нельзя.",
        ],
      },
      {
        h: "Qvant",
        p: [
          "Qvant — внутренние баллы платформы. Они не имеют денежной стоимости, не покупаются, не продаются и не обмениваются на деньги.",
          "Qvant используется только внутри платформы и исчезает при удалении аккаунта.",
        ],
      },
      {
        h: "Сервис",
        p: [
          "Платформа находится в стадии развития: возможности могут меняться, возможны временные перерывы в работе.",
          "Мы оставляем за собой право ограничить или удалить аккаунт, нарушающий правила.",
          "При изменении условий обновляется дата на этой странице.",
        ],
      },
    ],
  },
  en: {
    title: "Terms of use",
    updated: UPDATED,
    intro:
      "RankWant is a competitive programming platform. This page describes the rules for using it.",
    sections: [
      {
        h: "Account",
        p: [
          "One person, one account. Multiple accounts distort ratings and contest results.",
          "A username must not imitate another participant. A name taken with visually similar letters is rejected by the system.",
          "Your account's security is yours to keep: do not give your password to anyone.",
        ],
      },
      {
        h: "Contest integrity",
        p: [
          "During a contest, sharing a solution with others or taking one from others is not allowed.",
          "Submitting someone else's code as your own is plagiarism.",
          "A confirmed breach voids the result; a repeat restricts the account.",
        ],
      },
      {
        h: "Content",
        p: [
          "The code you submit remains yours. We use it only for judging, statistics and plagiarism detection.",
          "Problem statements belong to their authors. Problems from the KEP.uz archive were transferred with the owners' permission.",
          "Copying the platform's material and publishing it elsewhere without permission is not allowed.",
        ],
      },
      {
        h: "Qvant",
        p: [
          "Qvant is an in-platform score. It has no monetary value, cannot be bought or sold, and is not exchangeable for money.",
          "Qvant is used only inside the platform and is lost when an account is deleted.",
        ],
      },
      {
        h: "The service",
        p: [
          "The platform is still being built: features may change and interruptions are possible.",
          "We reserve the right to restrict or remove an account that breaks these rules.",
          "If the terms change, the date on this page is updated.",
        ],
      },
    ],
  },
};

export function pickLegal(locale: string): LegalLocale {
  return locale === "ru" || locale === "en" ? locale : "uz";
}
