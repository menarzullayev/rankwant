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

export const PRIVACY: Record<LegalLocale, LegalDoc> = {
  uz: {
    title: "Maxfiylik siyosati",
    updated: UPDATED,
    intro:
      "Bu sahifa RankWant qanday ma'lumot yig'ishini, nima uchun va qancha vaqt saqlashini aytadi. Har bir band platformada haqiqatan bajariladigan ishni tasvirlaydi.",
    sections: [
      {
        h: "Nima yig'iladi",
        p: [
          "Hisob: taxallus, email manzil va parolning kriptografik xesh qiymati. Parolning o'zi hech qachon saqlanmaydi va uni tiklab bo'lmaydi.",
          "Ixtiyoriy: ko'rsatiladigan ism, qisqa ma'lumot, avatar havolasi, til, Telegram identifikatori.",
          "Faoliyat: yuborilgan yechimlar va ularning kodi, verdiktlar, reytinglar, musobaqa natijalari, Qvant tranzaksiyalari.",
          "Texnik: parolni tiklash so'rovi yuborilganda IP manzil va brauzer nomi. Ular xatda ko'rsatiladi — foydalanuvchi so'rovni o'zi yubormaganini bilishi uchun.",
        ],
      },
      {
        h: "Nima uchun",
        p: [
          "Platformani ishlatish: hisobingizni tanish, yechimlarni tekshirish, reyting hisoblash, musobaqa jadvalini qurish.",
          "Suiiste'moldan himoya: so'rovlar sonini cheklash, ko'p hisob va taqlidning oldini olish.",
          "Hisobni tiklash: parolni unutganda pochtaga havola yuborish.",
        ],
      },
      {
        h: "Kim bilan ulashiladi",
        p: [
          "Xat yuborish provayderlari — Brevo, Mailjet, Resend, MailerSend. Ularga faqat qabul qiluvchi manzil va xat matni beriladi.",
          "Cloudflare — sayt trafigi shu tarmoq orqali o'tadi.",
          "Ijtimoiy kirishdan foydalansangiz, tanlagan provayderingiz (Google, GitHub, Telegram) bizga sizning identifikatoringiz va email manzilingizni beradi.",
          "Boshqa hech kimga berilmaydi va hech qachon sotilmaydi.",
        ],
      },
      {
        h: "Qancha saqlanadi",
        p: [
          "Hisob va faoliyat — hisob mavjud ekan.",
          "Parolni tiklash havolasi va kodi — bir soat, keyin ular ishlamaydi.",
          "Yuborilgan xatlarning TANASI umuman saqlanmaydi: tiklash havolasi tokendir, uni bazaga ko'chirish uni ikkinchi joyda qoldirish bo'lardi. Faqat qachon, kimga va qaysi provayder orqali yuborilgani yoziladi.",
        ],
      },
      {
        h: "Sizning huquqingiz",
        p: [
          "Ma'lumotingizni istalgan vaqt yuklab olishingiz mumkin — sozlamalar sahifasida eksport tugmasi bor.",
          "Hisobni o'chirishingiz mumkin. O'chirilganda shaxsiy ma'lumot (taxallus, email, ism, avatar, Telegram) olib tashlanadi va hisob anonim nom oladi. Yechimlar va musobaqa natijalari saqlanib qoladi, chunki ular boshqa ishtirokchilarning jadvaliga ham tegishli.",
          "Savol bo'lsa yozing — aloqa manzili sayt pastida.",
        ],
      },
      {
        h: "Bolalar",
        p: [
          "Platforma maktab o'quvchilari uchun ham mo'ljallangan. Biz yosh haqida ma'lumot so'ramaymiz va uni saqlamaymiz.",
        ],
      },
    ],
  },
  ru: {
    title: "Политика конфиденциальности",
    updated: UPDATED,
    intro:
      "Эта страница описывает, какие данные собирает RankWant, зачем и как долго их хранит. Каждый пункт описывает то, что действительно происходит на платформе.",
    sections: [
      {
        h: "Что собирается",
        p: [
          "Аккаунт: имя пользователя, адрес электронной почты и криптографический хеш пароля. Сам пароль не хранится и не может быть восстановлен.",
          "По желанию: отображаемое имя, краткое описание, ссылка на аватар, язык, идентификатор Telegram.",
          "Активность: отправленные решения и их код, вердикты, рейтинги, результаты соревнований, транзакции Qvant.",
          "Технические данные: IP-адрес и название браузера в момент запроса на восстановление пароля. Они показываются в письме, чтобы вы могли понять, что запрос сделали не вы.",
        ],
      },
      {
        h: "Зачем",
        p: [
          "Работа платформы: распознавание аккаунта, проверка решений, расчёт рейтинга, построение таблицы результатов.",
          "Защита от злоупотреблений: ограничение частоты запросов, предотвращение множественных аккаунтов и подражания.",
          "Восстановление доступа: отправка ссылки на почту, если пароль забыт.",
        ],
      },
      {
        h: "Кому передаётся",
        p: [
          "Почтовым провайдерам — Brevo, Mailjet, Resend, MailerSend. Им передаются только адрес получателя и текст письма.",
          "Cloudflare — через эту сеть проходит трафик сайта.",
          "Если вы используете вход через соцсети, выбранный провайдер (Google, GitHub, Telegram) передаёт нам ваш идентификатор и адрес почты.",
          "Больше никому не передаётся и никогда не продаётся.",
        ],
      },
      {
        h: "Сколько хранится",
        p: [
          "Аккаунт и активность — пока существует аккаунт.",
          "Ссылка и код восстановления — один час, после чего перестают работать.",
          "ТЕЛО отправленных писем не сохраняется вовсе: ссылка восстановления — это токен, и запись её в базу оставила бы вторую копию. Сохраняется только когда, кому и через какого провайдера письмо ушло.",
        ],
      },
      {
        h: "Ваши права",
        p: [
          "Вы можете выгрузить свои данные в любой момент — кнопка экспорта на странице настроек.",
          "Вы можете удалить аккаунт. При удалении личные данные (имя пользователя, почта, имя, аватар, Telegram) удаляются, а аккаунт получает анонимное имя. Решения и результаты соревнований сохраняются, так как они относятся и к таблицам других участников.",
          "Если есть вопросы — напишите нам, контакт указан внизу сайта.",
        ],
      },
      {
        h: "Дети",
        p: [
          "Платформа рассчитана в том числе на школьников. Мы не спрашиваем возраст и не храним его.",
        ],
      },
    ],
  },
  en: {
    title: "Privacy policy",
    updated: UPDATED,
    intro:
      "This page describes what RankWant collects, why, and for how long. Each item describes something the platform actually does.",
    sections: [
      {
        h: "What is collected",
        p: [
          "Account: username, email address, and a cryptographic hash of the password. The password itself is never stored and cannot be recovered.",
          "Optional: display name, short bio, avatar link, language, Telegram identifier.",
          "Activity: submitted solutions and their source code, verdicts, ratings, contest results, Qvant transactions.",
          "Technical: the IP address and browser name at the moment a password reset is requested. They appear in the message so you can tell that the request was not yours.",
        ],
      },
      {
        h: "Why",
        p: [
          "Running the platform: recognising your account, judging solutions, computing ratings, building standings.",
          "Preventing abuse: rate limiting, and blocking duplicate accounts and impersonation.",
          "Account recovery: sending a link to your mailbox when a password is forgotten.",
        ],
      },
      {
        h: "Who it is shared with",
        p: [
          "Email providers — Brevo, Mailjet, Resend, MailerSend. They receive only the recipient address and the message body.",
          "Cloudflare — the site's traffic passes through this network.",
          "If you use social sign-in, the provider you choose (Google, GitHub, Telegram) gives us your identifier and email address.",
          "It is shared with nobody else and never sold.",
        ],
      },
      {
        h: "How long it is kept",
        p: [
          "Account and activity — for as long as the account exists.",
          "Reset links and codes — one hour, after which they stop working.",
          "The BODY of sent messages is not stored at all: a reset link is a token, and writing it to the database would leave a second copy. Only the time, the recipient and the provider used are recorded.",
        ],
      },
      {
        h: "Your rights",
        p: [
          "You can download your data at any time — there is an export button on the settings page.",
          "You can delete your account. Deletion removes personal data (username, email, name, avatar, Telegram) and the account is given an anonymous name. Solutions and contest results remain, because they also belong to other participants' standings.",
          "If you have questions, write to us — the contact is at the bottom of the site.",
        ],
      },
      {
        h: "Children",
        p: [
          "The platform is intended for school students among others. We do not ask for an age and do not store one.",
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
