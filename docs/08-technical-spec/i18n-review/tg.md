# Tajik (tg) — translation review

**Status:** unverified. These values were produced by a language
model, not by a speaker of the language. They are plausible, and
some are certainly wrong.

## How to review

Read the third column against the second. If the meaning is right,
tick the last column. If it is wrong, write the correct wording in
it and it will be copied into the dictionary.

- Column 2 is the **Uzbek source**, the text the app was written in.
- Column 3 is what a user of this language currently sees.
- Proper nouns and loanwords are expected to match the source; that
  is deliberate and `tools/check_i18n.py` exempts them explicitly.

Regenerate with `python tools/export_i18n_review.py --prefix ""` (every key).

**1573 strings.**

| Key | Uzbek (source) | Tajik | Review |
| --- | --- | --- | --- |
| `customizer.tab.appearance` | Ko'rinish | Намуд |  |
| `customizer.template.classic` | Klassik | Классикӣ |  |
| `customizer.template.day` | Kun | Рӯз |  |
| `customizer.template.night` | Tun | Шаб |  |
| `customizer.template.console` | Konsol | Консол |  |
| `customizer.template.journal` | Jurnal | Маҷалла |  |
| `customizer.template.focus` | Fokus | Фокус |  |
| `customizer.template.soft` | Yumshoq | Мулоим |  |
| `customizer.template.aurora` | Aurora | Аврора |  |
| `customizer.copyLink` | Havolani nusxalash | Пайвандро нусха бардоштан |  |
| `customizer.linkCopied` | Havola nusxalandi | Пайванд нусхабардорӣ шуд |  |
| `customizer.myTemplates` | Mening shablonlarim | Қолибҳои ман |  |
| `customizer.templateName` | Shablon nomi | Номи қолиб |  |
| `customizer.save` | Saqlash | Нигоҳ доштан |  |
| `customizer.delete` | O'chirish | Нест кардан |  |
| `customizer.templateLimit` | Shablon chegarasiga yetdingiz | Ба ҳадди қолибҳо расидед |  |
| `customizer.show` | Sozlagichni ko'rsatish | Нишон додани танзимгар |  |
| `customizer.title` | Ko'rinish sozlagichi | Танзими намуд |  |
| `customizer.short` | Ko'rinish | Намуд |  |
| `customizer.close` | Yopish | Пӯшидан |  |
| `customizer.tab.a11y` | Qulaylik | Дастрасӣ |  |
| `customizer.templates` | Tayyor shablonlar | Қолибҳои омода |  |
| `customizer.templateModified` | Shablon o'zgartirilgan | Қолиб тағйир ёфт |  |
| `customizer.theme` | Mavzu | Мавзӯъ |  |
| `customizer.themeFixed` | Bu uslub faqat bitta muhitga chizilgan — mavzu unga moslashadi. | Ин услуб танҳо барои як муҳит кашида шудааст — мавзӯъ ба он мутобиқ мешавад. |  |
| `customizer.style` | Uslub | Услуб |  |
| `customizer.accent` | Asosiy rang | Ранги асосӣ |  |
| `customizer.accentDefault` | Uslubning o'z rangi | Ранги худи услуб |  |
| `customizer.hue` | Tus | Ранг |  |
| `customizer.saturation` | To'yinganlik | Серӣ |  |
| `customizer.contrastButton` | Tugma matni | Матни тугма |  |
| `customizer.contrastText` | Matn (havola) | Матн (пайванд) |  |
| `customizer.contrastBlocked` | Bu rang o'qilmaydi — AA (4.5:1) dan o'tmadi, saqlanmaydi. | Ин ранг хонда намешавад — аз AA (4.5:1) намегузарад ва нигоҳ дошта намешавад. |  |
| `customizer.accentApply` | Rangni qo'llash | Рангро татбиқ кардан |  |
| `customizer.accentCurrent` | Joriy kontrast | Контрасти ҷорӣ |  |
| `customizer.font` | Shrift | Ҳарф |  |
| `customizer.font.default` | Uslubning o'zi | Худи услуб |  |
| `customizer.fontHint` | Lexend o'qish qiyinligi uchun ishlab chiqilgan. | Lexend барои душвории хондан сохта шудааст. |  |
| `customizer.fontHeading` | Sarlavha shrifti | Шрифти сарлавҳа |  |
| `customizer.fontHeadingHint` | Sarlavhalar uchun boshqa shrift — klassik juftlik. | Шрифти дигар барои сарлавҳаҳо — ҷуфти классикӣ. |  |
| `customizer.font.same` | Matn bilan bir xil | Мисли матн |  |
| `customizer.size` | Shrift o'lchami | Андозаи ҳарф |  |
| `customizer.density` | Zichlik | Зичӣ |  |
| `customizer.density.compact` | Zich | Зич |  |
| `customizer.density.comfortable` | Qulay | Қулай |  |
| `customizer.density.spacious` | Keng | Фарроҳ |  |
| `customizer.a11y.vision` | Rang ajratish | Фарқи рангҳо |  |
| `customizer.a11y.vision.normal` | Oddiy | Муқаррарӣ |  |
| `customizer.a11y.vision.protan` | Qizil-yashil | Сурх-сабз |  |
| `customizer.a11y.vision.tritan` | Ko'k-sariq | Кабуд-зард |  |
| `customizer.a11y.visionHint` | Palitra moslashadi: holat ranglari shakl va matn bilan ham ajralib turadi. | Палитра мутобиқ мешавад: рангҳои ҳолат бо шакл ва матн ҳам фарқ мекунанд. |  |
| `customizer.a11y.motion` | Harakat | Ҳаракат |  |
| `customizer.a11y.motion.system` | Tizim | Системавӣ |  |
| `customizer.a11y.motion.reduce` | Kamaytirish | Кам кардан |  |
| `customizer.a11y.more` | Qo'shimcha | Иловагӣ |  |
| `customizer.a11y.bigTargets` | Katta bosish maydonlari | Майдонҳои калони зер |  |
| `customizer.a11y.strongFocus` | Kuchli fokus halqasi | Ҳалқаи қавии фокус |  |
| `customizer.undo` | Bekor qilish | Бекор кардан |  |
| `customizer.reset` | Tiklash | Барқарор кардан |  |
| `customizer.resetConfirm` | Ha, hammasini tiklash | Бале, ҳамаро барқарор кун |  |
| `customizer.cancel` | Yopish | Бекор |  |
| `nav.platformRoadmap` | Yo'l xaritasi | Нақшаи рушд |  |
| `roadmap.title` | Platforma yo'l xaritasi | Нақшаи рушди платформа |  |
| `roadmap.lead` | Platformada nima rejalashtirilgani va nima ustida ishlanayotgani. Ovoz bering yoki o'z taklifingizni qoldiring — har bir taklif ochiq ko'rinadi. | Дар платформа чӣ нақша шудааст ва аз рӯи чӣ кор меравад. Овоз диҳед ё пешниҳоди худро гузоред — ҳар пешниҳод ошкоро дида мешавад. |  |
| `roadmap.suggest` | Taklif berish | Пешниҳод кардан |  |
| `roadmap.suggestTitle` | Sarlavha | Сарлавҳа |  |
| `roadmap.suggestBody` | Tavsif | Тавсиф |  |
| `roadmap.suggestHint` | Taklif darhol shu sahifada \"Ko'rib chiqilmoqda\" holatida ko'rinadi va boshqalar ovoz bera oladi. | Пешниҳод дарҳол ҳамин ҷо бо ҳолати «Дар баррасӣ» пайдо мешавад ва дигарон метавонанд овоз диҳанд. |  |
| `roadmap.suggestSend` | Yuborish | Фиристодан |  |
| `roadmap.suggestCancel` | Bekor qilish | Бекор кардан |  |
| `roadmap.sending` | Yuborilmoqda… | Фиристода мешавад… |  |
| `roadmap.vote` | Ovoz berish | Овоз додан |  |
| `roadmap.voted` | Ovoz berdingiz | Шумо овоз додед |  |
| `roadmap.voteLogin` | Ovoz berish uchun tizimga kiring | Барои овоз додан ворид шавед |  |
| `roadmap.empty` | Hozircha bo'sh | Ҳоло холӣ |  |
| `roadmap.truncated` | Ro'yxat cheklangan: yana {count} ta band bor. | Рӯйхат маҳдуд аст: боз {count} сабт ҳаст. |  |
| `roadmap.status.suggested` | Ko'rib chiqilmoqda | Дар баррасӣ |  |
| `roadmap.status.planned` | Rejalashtirilgan | Нақшашуда |  |
| `roadmap.status.in_progress` | Ishlanmoqda | Дар кор |  |
| `roadmap.status.released` | Chiqarildi | Нашр шуд |  |
| `roadmap.status.declined` | Rad etilgan | Рад шуд |  |
| `roadmap.quarter` | Muddat | Мӯҳлат |  |
| `roadmap.author` | Muallif | Муаллиф |  |
| `roadmap.timeline` | Holat tarixi | Таърихи ҳолат |  |
| `roadmap.plannedAt` | Rejalashtirildi | Нақша шуд |  |
| `roadmap.startedAt` | Boshlandi | Оғоз ёфт |  |
| `roadmap.releasedAt` | Chiqarildi | Нашр шуд |  |
| `roadmap.changelog` | Changelogda ko'rish | Дар рӯйхати тағйирот дидан |  |
| `roadmap.comments` | Izohlar | Шарҳҳо |  |
| `roadmap.commentCount` | Izohlar: {count} | Шарҳҳо: {count} |  |
| `roadmap.commentPlaceholder` | Fikringizni yozing… | Фикратонро нависед… |  |
| `roadmap.commentSend` | Izoh qoldirish | Шарҳ гузоштан |  |
| `roadmap.commentLogin` | Izoh qoldirish uchun tizimga kiring | Барои шарҳ гузоштан ворид шавед |  |
| `roadmap.noComments` | Hozircha izoh yo'q — birinchi bo'ling. | Ҳоло шарҳ нест — аввалин шавед. |  |
| `roadmap.deletedUser` | O'chirilgan hisob | Ҳисоби нестшуда |  |
| `roadmap.mine` | Mening takliflarim | Пешниҳодҳои ман |  |
| `roadmap.declinedTitle` | Rad etilganlar | Радшудаҳо |  |
| `roadmap.declinedHint` | Bu taklif rad etilgan. Sababi izohlarda bo'lishi mumkin. | Ин пешниҳод рад шуд. Сабаб дар шарҳҳо буда метавонад. |  |
| `roadmap.back` | Barcha rejalar | Ҳамаи нақшаҳо |  |
| `nav.updates` | O'zgarishlar | Навсозиҳо |  |
| `update.title` | Platforma o'zgarishlari | Тағйиротҳо дар платформа |  |
| `update.lead` | Platformada nima o'zgargani: yangi imkoniyatlar, tuzatishlar va muhim ogohlantirishlar. Har bir yozuv chiqqan sanasi bilan yozib boriladi. | Дар платформа чӣ тағйир ёфт: имкониятҳои нав, ислоҳҳо ва огоҳиҳои муҳим. Ҳар як сабт бо санаи нашр нашр мешавад. |  |
| `update.home` | So'nggi o'zgarishlar | Тағйиротҳои охирин |  |
| `update.filterAll` | Barcha turlar | Ҳамаи намудҳо |  |
| `update.filterLabel` | Tur bo'yicha filtr | Филтр аз рӯи намуд |  |
| `update.actionable` | Diqqat talab qiladi | Диққатро талаб мекунад |  |
| `update.actionableHint` | Bu o'zgarishlar sizdan biror amal talab qiladi — eski usul ishlamay qolishi mumkin. | Ин тағйиротҳо аз шумо амал талаб мекунанд — усули кӯҳна метавонад кор накунад. |  |
| `update.source` | Manbani ko'rish | Сарчашмаро кушодан |  |
| `update.withdrawn` | Bu yozuv nashrdan olingan. U arxivda qoladi, lekin mazmuni endi amal qilmaydi. | Ин сабт аз нашр гирифта шуд. Он дар бойгонӣ мемонад, аммо мундариҷааш дигар эътибор надорад. |  |
| `update.markAllRead` | Hammasi o'qildi | Ҳамаро хондашуда қайд кардан |  |
| `update.allRead` | Hammasi o'qilgan | Ҳама хонда шудааст |  |
| `update.originUz` | Bu yozuv hali tarjima qilinmagan — o'zbekcha ko'rsatilmoqda. | Ин сабт ҳанӯз тарҷума нашудааст — бо забони ӯзбекӣ нишон дода мешавад. |  |
| `update.back` | Barcha o'zgarishlar | Ҳамаи тағйиротҳо |  |
| `update.releasedOn` | Chiqarilgan sana | Санаи нашр |  |
| `update.entry` | yozuv | сабт |  |
| `update.unavailable` | O'zgarishlar ro'yxatini hozircha yuklab bo'lmadi. Birozdan so'ng qayta urinib ko'ring. | Рӯйхати тағйиротро бор карда нашуд. Баъдтар аз нав кӯшиш кунед. |  |
| `update.kind.new` | Yangi | Нав |  |
| `update.kind.improved` | Yaxshilandi | Беҳтар шуд |  |
| `update.kind.fixed` | Tuzatildi | Ислоҳ шуд |  |
| `update.kind.performance` | Tezlik | Суръат |  |
| `update.kind.security` | Xavfsizlik | Амният |  |
| `update.kind.design` | Dizayn | Тарҳ |  |
| `update.kind.content` | Kontent | Мазмун |  |
| `update.kind.infrastructure` | Infratuzilma | Зерсохтор |  |
| `update.kind.breaking` | Buzuvchi | Шикананда |  |
| `update.kind.deprecated` | Olib tashlanadi | Хориҷ мешавад |  |
| `update.module.problems` | Masalalar | Масъалаҳо |  |
| `update.module.contests` | Musobaqalar | Мусобиқаҳо |  |
| `update.module.arena` | Bellashuvlar | Арена |  |
| `update.module.judge` | Tekshiruv | Санҷиш |  |
| `update.module.ratings` | Reyting | Рейтинг |  |
| `update.module.qvant` | Qvant | Квант |  |
| `update.module.profile` | Profil | Профил |  |
| `update.module.classroom` | Sinf | Синф |  |
| `update.module.quizzes` | Testlar | Тестҳо |  |
| `update.module.content` | Kontent | Мазмун |  |
| `update.module.design` | Dizayn | Тарҳ |  |
| `update.module.core` | Umumiy | Умумӣ |  |
| `nav.problems` | Masalalar | Масъалаҳо |  |
| `nav.contests` | Musobaqalar | Мусобиқаҳо |  |
| `nav.leaderboard` | Reyting | Рейтинг |  |
| `nav.ratingInfo` | Reyting qanday hisoblanadi | Рейтинг чӣ гуна ҳисоб мешавад |  |
| `problems.title` | Masalalar arxivi | Бойгонии масъалаҳо |  |
| `problems.difficulty` | Qiyinlik | Мураккабӣ |  |
| `problems.solved` | Yechilgan | Ҳалшуда |  |
| `problems.solvedByYou` | Siz yechgansiz | Шумо ҳал кардед |  |
| `problems.topics` | Mavzular | Мавзӯъҳо |  |
| `problems.limits` | Cheklovlar | Маҳдудиятҳо |  |
| `contests.title` | Musobaqalar | Мусобиқаҳо |  |
| `contests.running` | Ketmoqda | Идома дорад |  |
| `contests.finished` | Tugagan | Анҷомёфта |  |
| `contests.upcoming` | Kelasi | Оянда |  |
| `contests.rated` | Reytingli | Рейтингӣ |  |
| `standings.title` | Natijalar jadvali | Ҷадвали натиҷаҳо |  |
| `standings.rank` | O'rin | Ҷой |  |
| `standings.user` | Foydalanuvchi | Корбар |  |
| `standings.solved` | Yechildi | Ҳал шуд |  |
| `standings.hacks` | Hacklar | Шикастҳо |  |
| `standings.penalty` | Jarima | Ҷарима |  |
| `standings.frozen` | Jadval muzlatilgan | Ҷадвал яхбаста |  |
| `leaderboard.title` | Reyting | Рейтинг |  |
| `leaderboard.skills` | Skills | Skills |  |
| `leaderboard.contest` | Contests | Contests |  |
| `nav.qvant` | Qvant | Qvant |  |
| `qvant.title` | Qvant | Qvant |  |
| `qvant.balance` | Balans | Тавозун |  |
| `qvant.today` | Bugun topildi | Имрӯз ба даст омад |  |
| `qvant.remaining` | Bugun qolgan limit | Ҳадди боқимондаи имрӯз |  |
| `qvant.quests` | Vazifalar | Вазифаҳо |  |
| `qvant.shop` | Do'kon | Мағоза |  |
| `qvant.done` | Bajarildi | Иҷро шуд |  |
| `qvant.price` | Narx | Нарх |  |
| `qvant.owned` | Sizda bor | Шумо доред |  |
| `leaderboard.activity` | Activity | Activity |  |
| `leaderboard.streak` | Streak | Streak |  |
| `nav.blog` | Yangiliklar | Хабарҳо |  |
| `nav.notifications` | Bildirishnomalar | Огоҳиномаҳо |  |
| `blog.title` | Yangiliklar | Хабарҳо |  |
| `notif.title` | Bildirishnomalar | Огоҳиномаҳо |  |
| `notif.unread` | O'qilmagan | Нахондашуда |  |
| `recommend.title` | Sizga tavsiya | Тавсия ба шумо |  |
| `recommend.target` | Maqsad qiyinlik | Мураккабии ҳадаф |  |
| `contest.virtual` | Virtual boshlash | Оғози виртуалӣ |  |
| `nav.learn` | O'rganish | Омӯзиш |  |
| `learn.title` | O'quv materiallari | Маводи таълимӣ |  |
| `learn.roadmaps` | Yo'l xaritalari | Харитаҳои роҳ |  |
| `learn.articles` | Maqolalar | Мақолаҳо |  |
| `learn.minutes` | daq | дақ |  |
| `learn.practice` | Mashq masalalari | Масъалаҳои машқӣ |  |
| `profile.history` | Reyting tarixi | Таърихи рейтинг |  |
| `profile.solved` | Yechilgan masalalar | Масъалаҳои ҳалшуда |  |
| `profile.reason` | Sabab | Сабаб |  |
| `profile.change` | O'zgarish | Тағйирот |  |
| `profile.rerated` | masala qayta baholandi | масъала аз нав баҳо дода шуд |  |
| `notFound.title` | Sahifa topilmadi | Саҳифа ёфт нашуд |  |
| `notFound.body` | Havola eskirgan yoki manzil noto'g'ri. | Пайванд кӯҳна шудааст ё суроға нодуруст аст. |  |
| `notFound.home` | Bosh sahifaga | Ба саҳифаи асосӣ |  |
| `nav.skipToContent` | Asosiy mazmunga o'tish | Гузаштан ба мӯҳтавои асосӣ |  |
| `nav.close` | Yopish | Пӯшидан |  |
| `nav.menu` | Menyu | Меню |  |
| `nav.collapseSidebar` | Yon panelni yig'ish | Печонидани панели паҳлӯ |  |
| `nav.expandSidebar` | Yon panelni ochish | Кушодани панели паҳлӯ |  |
| `nav.main` | Asosiy navigatsiya | Навигатсияи асосӣ |  |
| `theme.light` | Yorug' rejim | Ҳолати равшан |  |
| `theme.dark` | Qorong'u rejim | Ҳолати торик |  |
| `theme.system` | Tizim | Системавӣ |  |
| `auth.login` | Kirish | Ворид шудан |  |
| `auth.register` | Ro'yxatdan o'tish | Сабти ном |  |
| `auth.createAccount` | Hisob yaratish | Сохтани ҳисоб |  |
| `auth.logout` | Chiqish | Баромадан |  |
| `auth.username` | Foydalanuvchi nomi | Номи корбар |  |
| `auth.password` | Parol | Рамз |  |
| `auth.email` | Email | Email |  |
| `auth.linkTitle` | Hisobni bog'lash | Пайваст кардани ҳисоб |  |
| `auth.linkBody` | Bu email allaqachon ishlatilgan. Bog'lash uchun parolingizni kiriting. | Ин email аллакай истифода шудааст. Барои пайваст рамзи худро ворид кунед. |  |
| `auth.linkCta` | Bog'lash | Пайваст кардан |  |
| `auth.socialError` | Kirish amalga oshmadi. Qayta urinib ko'ring. | Ворид шудан муяссар нашуд. Аз нав кӯшиш кунед. |  |
| `footer.terms` | Shartlar | Шартҳо |  |
| `footer.privacy` | Maxfiylik | Махфият |  |
| `auth.usernameRequired` | Taxallus 3–30 belgi: bo'sh qolmasin | Тахаллус 3–30 аломат: холӣ намонад |  |
| `auth.usernameHint` | 3–30 belgi: lotin harflari, raqam, nuqta, pastki chiziq, chiziqcha | 3–30 аломат: ҳарфҳои лотинӣ, рақам, нуқта, зерхат, дефис |  |
| `auth.passwordHint` | Kamida 8 belgi. Faqat raqamdan iborat bo'lmasin. | Ҳадди ақал 8 аломат. Танҳо рақам набошад. |  |
| `auth.usernameFree` | Bu nom bo'sh | Ин ном озод аст |  |
| `auth.checking` | Tekshirilmoqda… | Санҷида мешавад… |  |
| `auth.passwordMatch` | Parollar mos | Паролҳо мувофиқанд |  |
| `auth.emailInvalid` | Email manzili noto'g'ri | Суроғаи почта нодуруст аст |  |
| `auth.strength1` | Juda zaif | Хеле заиф |  |
| `auth.strength2` | Zaif | Заиф |  |
| `auth.strength3` | O'rtacha | Миёна |  |
| `auth.strength4` | Kuchli | Қавӣ |  |
| `auth.socialConsent` | Davom etish orqali siz {terms} va {privacy} siyosatiga rozilik bildirasiz. | Бо идома додан шумо ба {terms} ва сиёсати {privacy} розӣ мешавед. |  |
| `auth.verifyTitle` | Emailni tasdiqlash | Тасдиқи почта |  |
| `auth.verifyPending` | Pochtangiz tasdiqlanmagan. Yuborilgan xatdagi havolani bosing. | Почтаи шумо тасдиқ нашудааст. Пайвандро аз номаи фиристодашуда кушоед. |  |
| `auth.verifyResend` | Xatni qayta yuborish | Номаро дубора фиристодан |  |
| `auth.verifySending` | Yuborilmoqda… | Фиристода мешавад… |  |
| `auth.verifyResendFail` | Xat yuborilmadi. | Нома фиристода нашуд. |  |
| `auth.verifySent` | Xat yuborildi | Нома фиристода шуд |  |
| `auth.verifyOk` | Pochta tasdiqlandi | Почта тасдиқ шуд |  |
| `auth.verifyFail` | Havola yaroqsiz yoki muddati tugagan | Пайванд нодуруст ё мӯҳлаташ гузаштааст |  |
| `auth.displayName` | Ism | Ном |  |
| `auth.displayNameHint` | Ixtiyoriy. Reytingda taxallus bilan birga ko'rinadi. | Ихтиёрӣ. Дар рейтинг ҳамроҳи тахаллус нишон дода мешавад. |  |
| `auth.loggingIn` | Kirilmoqda… | Ворид шуда истодааст… |  |
| `auth.registering` | Ro'yxatdan o'tilmoqda… | Сабти ном шуда истодааст… |  |
| `auth.welcome` | Xush kelibsiz! | Хуш омадед! |  |
| `auth.verifySentTo` | {email} ga tasdiqlash xati yubordik. Kodni shu yerga kiriting. | Ба {email} номаи рамздор фиристодем. Рамзро дар ин ҷо ворид кунед. |  |
| `auth.dismiss` | Yopish | Пӯшидан |  |
| `auth.passwordConfirm` | Parolni tasdiqlang | Рамзро тасдиқ кунед |  |
| `auth.passwordMismatch` | Parollar mos kelmadi | Рамзҳо мувофиқат намекунанд |  |
| `auth.togglePassword` | Parolni ko'rsatish | Рамзро нишон додан |  |
| `auth.forgot` | Parolni unutdingizmi? | Рамзро фаромӯш кардед? |  |
| `auth.orWith` | yoki | ё |  |
| `auth.withGoogle` | Google orqali davom etish | Бо Google идома додан |  |
| `auth.withGithub` | GitHub orqali davom etish | Бо GitHub идома додан |  |
| `auth.withTelegram` | Telegram orqali davom etish | Бо Telegram идома додан |  |
| `reset.title` | Parolni tiklash | Барқарорсозии рамз |  |
| `reset.intro` | Email yoki taxallusingizni kiriting — tiklash havolasini yuboramiz. | Email ё номи корбари худро ворид кунед — истиноди барқарорсозӣ мефиристем. |  |
| `reset.loginHint` | Email yoki taxallus | Email ё номи корбар |  |
| `reset.send` | Havola yuborish | Фиристодани истинод |  |
| `reset.sent` | Agar bunday hisob bo'lsa, xat yuborildi. Pochtangizni tekshiring. | Агар чунин ҳисоб вуҷуд дошта бошад, нома фиристода шуд. Почтаатонро тафтиш кунед. |  |
| `reset.newTitle` | Yangi parol | Рамзи нав |  |
| `reset.newIntro` | Yangi parolni kiriting. Havola bir soat amal qiladi. | Рамзи навро ворид кунед. Истинод як соат эътибор дорад. |  |
| `reset.save` | Saqlash | Нигоҳ доштан |  |
| `reset.done` | Parol o'zgartirildi. Endi kirishingiz mumkin. | Рамз иваз шуд. Акнун ворид шуда метавонед. |  |
| `reset.invalid` | Havola yaroqsiz yoki muddati tugagan. Yangisini so'rang. | Истинод нодуруст ё мӯҳлаташ гузаштааст. Наверо дархост кунед. |  |
| `auth.noAccount` | Hisobingiz yo'qmi? | Ҳисоб надоред? |  |
| `auth.hasAccount` | Hisobingiz bormi? | Ҳисоб доред? |  |
| `home.openRating` | Reyting yashirin emas | Рейтинг пинҳон нест |  |
| `problems.name` | Masala | Масъала |  |
| `home.attempts` | Urinishlar | Кӯшишҳо |  |
| `home.start` | Bepul boshlash | Оғози ройгон |  |
| `home.guestHint` | Masalalarni hisobsiz ham ko'rishingiz mumkin — yechish uchun ro'yxatdan o'ting. | Масъалаҳоро бе ҳисоб низ дида метавонед — барои ҳал кардан сабти ном шавед. |  |
| `home.upcoming` | Yaqin musobaqalar | Мусобиқаҳои наздик |  |
| `home.topUsers` | Reyting yetakchilari | Пешсафони рейтинг |  |
| `home.whereToStart` | Qayerdan boshlash | Аз куҷо оғоз кунем |  |
| `home.all` | Barchasi | Ҳама |  |
| `home.announcements` | So'nggi e'lonlar | Эълонҳои охирин |  |
| `navGroup.practice` | Mashq | Машқ |  |
| `navGroup.community` | Jamiyat | Ҷомеа |  |
| `navGroup.lab` | Laboratoriya | Лаборатория |  |
| `navGroup.library` | Kutubxona | Китобхона |  |
| `navGroup.compete` | Musobaqa | Мусобиқа |  |
| `navGroup.campus` | Kampus | Кампус |  |
| `navGroup.platform` | Platforma | Платформа |  |
| `nav.attempts` | Urinishlar | Кӯшишҳо |  |
| `nav.quizzes` | Testlar | Тестҳо |  |
| `nav.articles` | Maqolalar | Мақолаҳо |  |
| `nav.roadmap` | Traektoriya | Траектория |  |
| `nav.algorithms` | Algoritmlar | Алгоритмҳо |  |
| `nav.classroom` | Auditoriya | Синфхона |  |
| `nav.arena` | Arena | Арена |  |
| `nav.duels` | Duel | Дуэл |  |
| `nav.tournaments` | Chempionat | Чемпионат |  |
| `nav.hackathons` | Hakaton | Хакатон |  |
| `nav.calendar` | Taqvim | Тақвим |  |
| `nav.formulas` | Formulalar | Формулаҳо |  |
| `nav.shop` | Do'kon | Мағоза |  |
| `nav.about` | Qanday ishlaydi | Чӣ тавр кор мекунад |  |
| `nav.team` | Jamoa | Даста |  |
| `header.search` | Qidirish… | Ҷустуҷӯ… |  |
| `header.streak` | kun | рӯз |  |
| `header.noUnread` | Yangi bildirishnoma yo'q | Огоҳиномаи нав нест |  |
| `leaderboard.challenges` | Challenges | Challenges |  |
| `attempt.title` | Urinish #{id} | Кӯшиш #{id} |  |
| `attempt.source` | Manba kod | Рамзи манбаъ |  |
| `attempt.sourceHidden` | Manba kod faqat egasiga va hack huquqi borlarga ko'rinadi | Рамзи манбаъ танҳо ба муаллиф ва онҳое, ки ҳуқуқи шикастан доранд, намоён аст |  |
| `attempt.failedAt` | {index}-testda to'xtadi | Дар тести {index} қатъ шуд |  |
| `attempts.title` | Urinishlar oqimi | Ҷараёни кӯшишҳо |  |
| `attempts.verdict` | Verdikt | Вердикт |  |
| `attempts.language` | Til | Забон |  |
| `quiz.start` | Boshlash | Оғоз |  |
| `quiz.submit` | Topshirish | Супоридан |  |
| `quiz.result` | Natija | Натиҷа |  |
| `quiz.questions` | savol | савол |  |
| `quiz.best` | Eng yaxshi | Беҳтарин |  |
| `arena.join` | Qo'shilish | Ҳамроҳ шудан |  |
| `arena.joined` | Qo'shildingiz | Ҳамроҳ шудед |  |
| `arena.waiting` | Boshlanishini kuting | Оғозро интизор шавед |  |
| `arena.perQuestion` | s / savol | с / савол |  |
| `arena.answered` | Javob berildi | Ҷавоб дода шуд |  |
| `arena.finished` | Raund tugadi | Раунд анҷом ёфт |  |
| `duel.create` | Chaqiriq tashlash | Даъват фиристодан |  |
| `duel.accept` | Qabul qilish | Қабул кардан |  |
| `duel.cancel` | Bekor qilish | Бекор кардан |  |
| `duel.waiting` | Kutish xonasi | Ҳуҷраи интизорӣ |  |
| `duel.mine` | Mening duellarim | Дуэлҳои ман |  |
| `duel.record` | G/D/M | Ғ/Б/М |  |
| `duel.problems` | masala | масъала |  |
| `duel.minutes` | daqiqa | дақиқа |  |
| `tournament.stages` | Bosqichlar | Марҳилаҳо |  |
| `tournament.points` | Ball | Хол |  |
| `tournament.formula` | Ball = koeffitsient × (ishtirokchilar − o'rin + 1). Har bosqich alohida hisoblanadi. | Хол = коэффитсиент × (иштирокчиён − ҷой + 1). Ҳар марҳила алоҳида ҳисоб мешавад. |  |
| `hackathon.submit` | Loyiha topshirish | Супоридани лоиҳа |  |
| `hackathon.deadline` | Topshirish muddati | Мӯҳлати супоридан |  |
| `hackathon.entries` | Loyihalar | Лоиҳаҳо |  |
| `hackathon.score` | Ball | Хол |  |
| `hackathon.repo` | Repozitoriy | Репозиторий |  |
| `hackathon.demo` | Demo | Демо |  |
| `hackathon.team` | Jamoa nomi | Номи даста |  |
| `calendar.title` | Taqvim | Тақвим |  |
| `calendar.upcoming` | Kelgusi | Оянда |  |
| `calendar.past` | O'tgan | Гузашта |  |
| `classroom.create` | Sinf yaratish | Сохтани синф |  |
| `classroom.join` | Kodi bilan qo'shilish | Бо код ҳамроҳ шудан |  |
| `classroom.code` | Qo'shilish kodi | Рамзи ҳамроҳшавӣ |  |
| `classroom.members` | A'zolar | Аъзоён |  |
| `classroom.assignments` | Vazifalar | Вазифаҳо |  |
| `about.title` | RankWant qanday ishlaydi | RankWant чӣ тавр кор мекунад |  |
| `team.title` | Jamoa | Даста |  |
| `admin.title` | Boshqaruv | Идоракунӣ |  |
| `admin.create` | Yaratish | Сохтан |  |
| `admin.edit` | Tahrirlash | Таҳрир |  |
| `admin.save` | Saqlash | Нигоҳ доштан |  |
| `admin.delete` | O'chirish | Нест кардан |  |
| `admin.cancel` | Bekor | Бекор |  |
| `admin.confirmDelete` | Rostdan o'chirilsinmi? | Дар ҳақиқат нест карда шавад? |  |
| `admin.forbidden` | Bu bo'lim faqat xodimlar uchun. | Ин бахш танҳо барои кормандон аст. |  |
| `admin.search` | Qidirish… | Ҷустуҷӯ… |  |
| `admin.noRows` | Hech narsa yo'q | Чизе нест |  |
| `admin.actions` | Amallar | Амалҳо |  |
| `admin.saved` | Saqlandi | Нигоҳ дошта шуд |  |
| `common.clear` | Tozalash | Тоза кардан |  |
| `common.yes` | Ha | Бале |  |
| `common.notification` | Bildirishnoma | Огоҳинома |  |
| `col.time` | Vaqt | Вақт |  |
| `col.memory` | Xotira | Ҳофиза |  |
| `col.size` | Hajm | Ҳаҷм |  |
| `col.attempt` | Urinish | Кӯшиш |  |
| `col.sample` | Namuna | Намуна |  |
| `col.points` | Ball | Хол |  |
| `col.input` | Kirish | Вуруд |  |
| `col.output` | Chiqish | Хуруҷ |  |
| `col.weight` | Vazn | Вазн |  |
| `col.score` | Baholash | Баҳо |  |
| `col.role` | Rol | Нақш |  |
| `col.question` | Savol | Савол |  |
| `col.options` | Variantlar | Вариантҳо |  |
| `col.links` | Havolalar | Пайвандҳо |  |
| `col.project` | Loyiha | Лоиҳа |  |
| `action.save` | Saqlash | Нигоҳ доштан |  |
| `action.reset` | Reset | Аз нав |  |
| `action.finalize` | Yakunlash | Анҷом додан |  |
| `common.empty` | Hozircha bo'sh | Ҳоло холӣ |  |
| `common.emptyHint` | Bu yerda hozircha hech narsa yo'q. Keyinroq qayta ko'ring. | Дар ин ҷо ҳанӯз чизе нест. Баъдтар боз оед. |  |
| `settings.title` | Sozlamalar | Танзимот |  |
| `settings.export` | Ma'lumotni yuklab olish | Боргирии маълумот |  |
| `settings.exportHint` | Profil, yechimlar, reyting tarixi va Qvant amallari — bitta JSON fayl. | Профил, ҳалҳо, таърихи рейтинг ва амалиёти Qvant — як файли JSON. |  |
| `settings.exportAction` | Yuklab olish | Боргирӣ |  |
| `settings.social` | Ulangan hisoblar | Ҳисобҳои пайвастшуда |  |
| `settings.socialHint` | Google, GitHub yoki Telegram bilan kirishni ulashingiz mumkin. Pochta manzillari mos kelishi shart emas. | Шумо метавонед вуруд тавассути Google, GitHub ё Telegram-ро пайваст кунед. Суроғаҳои почта бояд мувофиқ набошанд. |  |
| `settings.socialConnect` | Ulash | Пайваст кардан |  |
| `settings.socialDisconnect` | Uzish | Ҷудо кардан |  |
| `settings.socialConnected` | Ulangan | Пайваст |  |
| `settings.socialLinked` | Hisob ulandi | Ҳисоб пайваст шуд |  |
| `settings.socialTaken` | Bu hisob boshqa foydalanuvchiga ulangan. Ko'chirish uchun o'sha provayder bilan kiring, Sozlamalardan uzing va shu yerga qayting. | Ин ҳисоб ба корбари дигар пайваст аст. Барои интиқол бо ҳамон провайдер ворид шавед, дар Танзимот ҷудо кунед ва ба ин ҷо баргардед. |  |
| `settings.socialLast` | Bu yagona kirish yo'lingiz — avval parol o'rnating | Ин ягона роҳи вуруди шумост — аввал парол гузоред |  |
| `settings.socialTelegramStep` | Endi Telegram tugmasini bosing | Акнун тугмаи Telegram-ро пахш кунед |  |
| `settings.delete` | Hisobni o'chirish | Ҳисобро нест кардан |  |
| `settings.deleteHint` | Ism, email va bio o'chadi, hisob anonim bo'ladi. Yechimlar va musobaqa natijalari joyida qoladi — ularni olib tashlash boshqa qatnashchilarning o'rnini siljitardi. | Ном, email ва тавсиф нест мешаванд, ҳисоб беном мегардад. Ҳалҳо ва натиҷаҳои мусобиқа боқӣ мемонанд — нест кардани онҳо ҷойи дигар иштирокчиёнро тағйир медод. |  |
| `settings.deletePassword` | Parolingiz | Пароли шумо |  |
| `settings.deleteAction` | Hisobni butunlay o'chirish | Ҳисобро тамоман нест кардан |  |
| `settings.deleteConfirm` | Bu amalni qaytarib bo'lmaydi. Davom etasizmi? | Ин амалро баргардонидан мумкин нест. Идома медиҳед? |  |
| `settings.deleteError` | Parol noto'g'ri | Парол нодуруст аст |  |
| `standings.you` | Sizning o'rningiz | Ҷойи шумо |  |
| `status.ok` | Muvaffaqiyat | Муваффақият |  |
| `status.warn` | Ogohlantirish | Огоҳӣ |  |
| `status.bad` | Xato | Хатогӣ |  |
| `status.info` | Ma'lumot | Маълумот |  |
| `status.hint.ok` | Amal muvaffaqiyatli bajarildi. | Амал бомуваффақият иҷро шуд. |  |
| `status.hint.warn` | Ehtiyot bo'ling — biror narsa chegaraga yaqin. | Эҳтиёт бошед — чизе ба ҳад наздик аст. |  |
| `status.hint.bad` | Amal bajarilmadi — sababini ko'ring. | Амал иҷро нашуд — сабабашро бубинед. |  |
| `status.hint.info` | Qo'shimcha ma'lumot. | Маълумоти иловагӣ. |  |
| `status.style.auto` | Avtomatik | Худкор |  |
| `status.style.autoHint` | Shaklni ekranga qarab tanlaydi: telefonda doira, kengroqda ikonka va matn. | Шаклро аз рӯи экран интихоб мекунад: дар телефон доира, дар васеътар нишона ва матн. |  |
| `status.style.text` | Faqat rangli matn | Танҳо матни рангӣ |  |
| `status.style.textHint` | Rang va so'z, ikonka yo'q. Eng yengil, lekin rangni ko'rmaydiganlar uchun signal yo'q. | Ранг ва сухан, нишона нест. Сабуктарин, вале барои онҳое, ки рангро намебинанд, сигнал нест. |  |
| `status.style.iconText` | Ikonka va matn | Нишона ва матн |  |
| `status.style.iconTextHint` | Ikonka, rang va so'z. Eng ko'p ishlatiladigan ko'rinish. | Нишона, ранг ва сухан. Маъмултарин намуд. |  |
| `status.style.badge` | To'ldirilgan nishon | Нишони пурра |  |
| `status.style.badgeHint` | Yumshoq fonda yumaloq nishon. Ro'yxat qatorlari uchun ixcham. | Нишони мудаввар дар фони мулоим. Барои сатрҳои рӯйхат ҷамъбаст. |  |
| `status.style.circle` | Doira va ikonka | Доира ва нишона |  |
| `status.style.circleHint` | To'ldirilgan doirada oq ikonka. Eng kichik — zich jadval uchun. | Нишонаи сафед дар доираи пурра. Хурдтарин — барои ҷадвалҳои зич. |  |
| `status.style.dot` | Nuqta va matn | Нуқта ва матн |  |
| `status.style.dotHint` | Rangli nuqta va so'z. Fon va ramka yo'q — yengil signal. | Нуқтаи рангӣ ва сухан. Бе фон ва чорчӯба — сигнали сабук. |  |
| `status.style.box` | Ramkali kvadrat | Чоркунҷаи чорчӯбадор |  |
| `status.style.boxHint` | Ramkali kvadrat ichida ikonka. Faqat signal, matnsiz. | Нишона дар дохили чоркунҷаи чорчӯбадор. Танҳо сигнал, бе матн. |  |
| `status.style.alert` | Chap chiziq | Хатти чап |  |
| `status.style.alertHint` | Chap tomonda rangli chiziq. Sahifa yuqorisidagi xabar uchun. | Хатти рангӣ дар тарафи чап. Барои паёми болои саҳифа. |  |
| `status.style.soft` | Yumshoq fonli karta | Корти фони мулоим |  |
| `status.style.softHint` | Yumshoq fon, ikonka, sarlavha va izoh. Forma natijasi uchun. | Фони мулоим, нишона, сарлавҳа ва эзоҳ. Барои натиҷаи форм. |  |
| `status.style.outline` | Ramkali karta | Корти чорчӯбадор |  |
| `status.style.outlineHint` | Ramka, ikonka, sarlavha va izoh. Xato tafsiloti uchun. | Чорчӯба, нишона, сарлавҳа ва эзоҳ. Барои тафсилоти хатогӣ. |  |
| `status.style.stack` | Katta karta | Корти калон |  |
| `status.style.stackHint` | Ikonka ustida, sarlavha va izoh ostida. Eng batafsil ko'rinish. | Нишона дар боло, сарлавҳа ва эзоҳ дар поён. Муфассалтарин намуд. |  |
| `verdict.PENDING` | Navbatda | Дар навбат |  |
| `verdict.RUNNING` | Tekshirilmoqda | Санҷида мешавад |  |
| `verdict.AC` | Qabul qilindi | Қабул шуд |  |
| `verdict.WA` | Javob noto'g'ri | Ҷавоб нодуруст |  |
| `verdict.TLE` | Vaqt tugadi | Вақт тамом шуд |  |
| `verdict.MLE` | Xotira tugadi | Хотира тамом шуд |  |
| `verdict.OLE` | Chiqish juda katta | Баромад хеле калон |  |
| `verdict.RE` | Bajarilishda xato | Хатои иҷро |  |
| `verdict.RE_SIGNAL` | Bajarilishda xato (signal) | Хатои иҷро (сигнал) |  |
| `verdict.RE_EXIT` | Bajarilishda xato (chiqish kodi) | Хатои иҷро (рамзи баромад) |  |
| `verdict.CE` | Kompilyatsiya xatosi | Хатои компилятсия |  |
| `verdict.PE` | Format xatosi | Хатои формат |  |
| `hack.title` | Hack | Шикастан |  |
| `hack.closed` | Bu yechim uchun hack oynasi yopiq | Равзанаи шикастан барои ин ҳал баста аст |  |
| `hack.mode.input` | Tayyor kiritma | Вуруди тайёр |  |
| `hack.mode.generator` | Generator | Генератор |  |
| `hack.input` | Test kiritmasi | Вуруди тест |  |
| `hack.inputHint` | Kiritma masala cheklovlariga mos bo'lishi kerak — buni validator tekshiradi | Вуруд бояд ба маҳдудиятҳои масъала мувофиқ бошад — инро валидатор месанҷад |  |
| `hack.generatorSource` | Generator manbasi | Рамзи генератор |  |
| `hack.generatorHint` | Dastur kiritmani chiqarishga yozadi — katta testlar uchun | Барнома вурудро ба баромади стандартӣ менависад — барои тестҳои калон |  |
| `hack.send` | Hack yuborish | Фиристодани шикаст |  |
| `hack.sent` | Hack yuborildi — natija tekshiruvdan keyin ko'rinadi | Шикаст фиристода шуд — натиҷа пас аз санҷиш пайдо мешавад |  |
| `hack.lock` | Masalani lock qilish | Қулф кардани масъала |  |
| `hack.lockHint` | Lock qilsangiz bu masalaga qayta yubora olmaysiz, evaziga xonadagi yechimlar ochiladi | Пас аз қулф ба ин масъала аз нав фиристода наметавонед, ба ҷояш ҳалҳои утоқ кушода мешаванд |  |
| `hack.status.TESTING` | Tekshirilmoqda | Дар санҷиш |  |
| `hack.status.SUCCESSFUL` | Muvaffaqiyatli | Муваффақ |  |
| `hack.status.UNSUCCESSFUL` | Ishlamadi | Кор накард |  |
| `hack.status.INVALID_INPUT` | Kiritma yaroqsiz | Вуруд нодуруст |  |
| `hack.status.GENERATOR_CRASHED` | Generator yiqildi | Генератор афтод |  |
| `hack.status.IGNORED` | Hisobga olinmadi | Ҳисоб нашуд |  |
| `hack.status.RATE_LIMITED` | Tezlik chegarasi | Ҳадди суръат |  |
| `hack.policy.contest_room` | Musobaqa xonasi | Утоқи мусобиқа |  |
| `hack.policy.open_phase` | Ochiq faza | Фазаи кушода |  |
| `hack.policy.practice` | Amaliyot | Амалия |  |
| `hack.policy.uphack` | Uphack | Апҳак |  |
| `verdict.HACKED` | Hack qilindi | Шикаст хӯрд |  |
| `verdict.PARTIAL` | Qisman ball | Холи қисман |  |
| `verdict.IE` | Ichki xato | Хатои дохилӣ |  |
| `verdict.WRONG_TEST` | Masala testi yaroqsiz | Тестҳои масъала нодурустанд |  |
| `verdict.group.ok.hint` | Yechimingiz to'g'ri — barcha testlar o'tdi. | Ҳалли шумо дуруст — ҳамаи тестҳо гузаштанд. |  |
| `verdict.group.warn.hint` | Hali yakunlanmagan yoki qisman bajarilgan. | Ҳанӯз тамом нашудааст ё қисман гузаштааст. |  |
| `verdict.group.bad.hint` | Yechimingizdagi xato — tuzatib qayta yuboring. | Дар ҳалли шумо хатогӣ ҳаст — ислоҳ карда, аз нав фиристед. |  |
| `verdict.group.neutral.hint` | Sizning xatoyingiz emas — tizim tomonidan. Qayta urinib ko'ring. | Ин хатогии шумо нест — нуқсони система. Аз нав кӯшиш кунед. |  |
| `verdict.group.unknown.hint` | Notanish natija kodi — tizim yangilangan bo'lishi mumkin. | Рамзи натиҷаи номаълум — эҳтимол система навсозӣ шудааст. |  |
| `verdict.SKIPPED` | Hisobga olinmadi | Ба ҳисоб гирифта нашуд |  |
| `verdict.COMPILE_TIMEOUT` | Kompilyatsiya cho'zildi | Компилятсия дароз кашид |  |
| `verdict.IDLENESS` | Dastur kutib qoldi | Барнома интизор монд |  |
| `verdict.SECURITY_VIOLATION` | Xavfsizlik qoidasi buzildi | Қоидаи амният вайрон шуд |  |
| `verdict.CHECKER_ERROR` | Tekshiruvchi xatosi | Хатои санҷанда |  |
| `verdict.TESTING_ABORTED` | Qayta tekshirilmoqda | Аз нав санҷида мешавад |  |
| `verdict.RATE_LIMITED` | Juda tez yuborildi | Хеле зуд фиристода шуд |  |
| `verdict.DENIAL_OF_JUDGEMENT` | Tekshirib bo'lmadi | Санҷида нашуд |  |
| `attempts.allVerdicts` | Hamma verdikt | Ҳамаи вердиктҳо |  |
| `error.already_answered` | Bu savolga allaqachon javob berdingiz | Шумо аллакай ба ин савол ҷавоб додаед |  |
| `error.already_finalized` | Allaqachon yakunlangan | Аллакай анҷом ёфтааст |  |
| `error.already_paid` | Bu allaqachon to'langan | Ин аллакай пардохт шудааст |  |
| `error.authentication_failed` | Autentifikatsiya o'tmadi | Санҷиши ҳувият ноком шуд |  |
| `error.bad_choice` | Variant bu savolga tegishli emas | Ин вариант ба ин савол тааллуқ надорад |  |
| `error.closed` | Topshirish muddati ochiq emas | Мӯҳлати супоридан баста аст |  |
| `error.contest_finished` | Musobaqa tugagan | Мусобиқа анҷом ёфт |  |
| `error.dependency_unavailable` | Xizmat vaqtincha mavjud emas, birozdan keyin urinib ko'ring | Хидмат муваққатан дастрас нест, пас аз каме кӯшиш кунед |  |
| `error.error` | Nimadir noto'g'ri ketdi | Чизе нодуруст шуд |  |
| `error.expired` | Muddati o'tib ketgan | Мӯҳлаташ гузаштааст |  |
| `error.finished` | Allaqachon tugagan | Аллакай анҷом ёфтааст |  |
| `error.forbidden` | Bunga ruxsatingiz yo'q | Шумо ба ин иҷозат надоред |  |
| `error.invalid` | Kiritilgan ma'lumot noto'g'ri | Маълумоти воридшуда нодуруст аст |  |
| `error.invalid_credentials` | Login yoki parol noto'g'ri | Ном ё рамз нодуруст аст |  |
| `error.invalid_expiry` | Amal qilish muddati noto'g'ri | Мӯҳлати эътибор нодуруст аст |  |
| `error.join_failed` | Qo'shilib bo'lmadi | Ҳамроҳ шудан муяссар нашуд |  |
| `error.method_not_allowed` | Bu amal qo'llab-quvvatlanmaydi | Ин амал дастгирӣ намешавад |  |
| `error.no_problems` | Mos masala topilmadi | Масъалаи мувофиқ ёфт нашуд |  |
| `error.not_accepted` | Faqat qabul qilingan duelni yakunlash mumkin | Танҳо дуэли қабулшударо анҷом додан мумкин |  |
| `error.not_authenticated` | Buning uchun tizimga kiring | Барои ин ворид шавед |  |
| `error.not_due` | Hali tugamagan | Ҳанӯз анҷом наёфтааст |  |
| `error.not_finished` | Hali tugamagan | Ҳанӯз анҷом наёфтааст |  |
| `error.not_found` | Topilmadi | Ёфт нашуд |  |
| `error.not_joined` | Avval qo'shiling | Аввал ҳамроҳ шавед |  |
| `error.not_open` | Chaqiriq endi ochiq emas | Даъват дигар кушода нест |  |
| `error.not_owner` | Bu faqat egasi uchun | Ин танҳо ба соҳиб иҷозат аст |  |
| `error.not_running` | Hozir faol emas | Ҳоло фаъол нест |  |
| `error.parse_error` | So'rovni o'qib bo'lmadi | Дархостро хондан нашуд |  |
| `error.permission_denied` | Bunga ruxsatingiz yo'q | Иҷозат надоред |  |
| `error.protected` | Bu yozuv boshqa joyda ishlatilmoqda, avval bog'lanishni uzing | Ин сабт дар ҷои дигар истифода мешавад, аввал пайвандро бардоред |  |
| `error.purchase_failed` | Xarid bajarilmadi | Харид иҷро нашуд |  |
| `error.range` | Qiymat ruxsat etilgan oraliqdan tashqarida | Қиймат берун аз ҳудуди иҷозатдодашуда |  |
| `error.self` | O'z chaqirig'ingizni qabul qila olmaysiz | Даъвати худро қабул карда наметавонед |  |
| `error.throttled` | Juda tez-tez urinyapsiz, biroz kuting | Хеле зуд-зуд, каме интизор шавед |  |
| `error.token_limit` | Faol tokenlar chegarasiga yetdingiz | Ба ҳадди токенҳои фаъол расидед |  |
| `error.too_many` | Juda ko'p — avval borlarini yakunlang | Хеле зиёд — аввал мавҷудаҳоро анҷом диҳед |  |
| `error.too_soon` | Boshlanish kamida 5 daqiqadan keyin bo'lishi kerak | Оғоз бояд ҳадди ақал пас аз 5 дақиқа бошад |  |
| `error.wrong_question` | Bu savol hozir ochiq emas | Ин савол ҳоло кушода нест |  |
| `profile.aboutEmpty` | Foydalanuvchi hali o'zi haqida ma'lumot qo'shmagan. | Корбар ҳанӯз дар бораи худ маълумот илова накардааст. |  |
| `profile.achContest` | Qatnashilgan musobaqalar: {n} | Мусобиқаҳои иштироккарда: {n} |  |
| `profile.achDone` | {done} / {total} yutuq qo'lga kiritilgan | {done} аз {total} дастовард ба даст омад |  |
| `profile.achProfile` | Profil to'ldirilgan | Профил пур карда шуд |  |
| `profile.achSolve` | Yechilgan masalalar: {n} | Масъалаҳои ҳалшуда: {n} |  |
| `profile.achStreak` | Uzluksiz kunlar: {n} | Рӯзҳои пайдарпай: {n} |  |
| `profile.activityContest` | Musobaqa | Мусобиқа |  |
| `profile.activityEmpty` | Hozircha faoliyat yo'q. | Ҳоло фаъолият нест. |  |
| `profile.activityHardSolve` | Qiyin masala yechildi | Масъалаи душвор ҳал шуд |  |
| `profile.activityOlder` | Oldingilari | Пештара |  |
| `profile.activityQuest` | Vazifa bajarildi | Супориш иҷро шуд |  |
| `profile.byLevel` | Daraja bo'yicha yechilganlar | Ҳалшуда аз рӯи сатҳ |  |
| `profile.date` | Sana | Сана |  |
| `profile.edit` | Profilni tahrirlash | Таҳрири профил |  |
| `profile.equipped` | Kiyilgan | Пӯшида |  |
| `profile.follow` | Kuzatish | Обуна шудан |  |
| `profile.following` | Kuzatilmoqda | Обуна шудед |  |
| `profile.followers` | Obunachilar | Обуначиён |  |
| `profile.followingTab` | Kuzatilayotganlar | Обунаҳо |  |
| `profile.freeze` | Streak muzlatish | Яхкунонии streak |  |
| `profile.hiddenChip` | faqat sizga ko'rinadi | танҳо ба шумо намоён |  |
| `profile.highest` | eng yuqori {max} | баландтарин {max} |  |
| `profile.joined` | Ro'yxatdan o'tgan: {date} | Сабти ном: {date} |  |
| `profile.next` | Keyingi | Навбатӣ |  |
| `profile.prev` | Oldingi | Қаблӣ |  |
| `profile.present` | hozirgacha | то ҳол |  |
| `profile.purchasesEmpty` | Hali xarid yo'q. | Ҳоло харид нест. |  |
| `profile.ratingColumn` | Reyting | Рейтинг |  |
| `profile.sections` | Profil bo'limlari | Бахшҳои профил |  |
| `profile.tab.about` | Shaxsiy | Шахсӣ |  |
| `profile.tab.achievements` | Yutuqlar | Дастовардҳо |  |
| `profile.tab.activity` | Faoliyat | Фаъолият |  |
| `profile.tab.purchases` | Xaridlar | Харидҳо |  |
| `profile.tab.rating` | Reyting | Рейтинг |  |
| `settings.addEducation` | Ta'lim joyi qo'shish | Иловаи ҷои таҳсил |  |
| `settings.addWork` | Ish joyi qo'shish | Иловаи ҷои кор |  |
| `settings.appearanceHint` | Sozlamalar hisobingizda saqlanadi — boshqa qurilmadan kirsangiz ham shunday ko'rinadi. | Танзимот дар ҳисоби шумо нигоҳ дошта мешавад — аз дастгоҳи дигар ҳам ҳамин тавр намоён мешавад. |  |
| `settings.avatar` | Profil rasmi | Акси профил |  |
| `settings.avatarBad` | Bu faylni rasm sifatida o'qib bo'lmadi. | Ин файлро ҳамчун тасвир хондан нашуд. |  |
| `settings.avatarHint` | PNG, JPEG yoki WebP. Rasm kvadrat qilib qirqiladi va 256 pikselga kichraytiriladi. | PNG, JPEG ё WebP. Тасвир ба шакли мураббаъ бурида ва то 256 пиксел хурд карда мешавад. |  |
| `settings.avatarImport` | {provider} rasmini olish | Гирифтани акс аз {provider} |  |
| `settings.avatarRemove` | Rasmni olib tashlash | Нест кардани акс |  |
| `settings.avatarUpload` | Rasm yuklash | Боргузории акс |  |
| `settings.bio` | O'zim haqimda | Дар бораи худ |  |
| `settings.bioHint` | Profil sahifasida ismingiz tagida ko'rinadi. | Дар саҳифаи профил зери номи шумо намоён мешавад. |  |
| `settings.birthDate` | Tug'ilgan sana | Санаи таваллуд |  |
| `settings.channelEmailSoon` | Pochta orqali yuborish keyinroq qo'shiladi. | Фиристодан тавассути почта баъдтар илова мешавад. |  |
| `settings.channelSite` | Saytda | Дар сайт |  |
| `settings.channelTelegram` | Telegram | Telegram |  |
| `settings.company` | Kompaniya | Ширкат |  |
| `settings.cosmetics` | Profil bezaklari | Ороишҳои профил |  |
| `settings.cosmeticsEmpty` | Hali bezak yo'q — ularni Qvant do'konidan olish mumkin. | Ҳоло ороиш нест — онҳоро аз мағозаи Qvant гирифтан мумкин. |  |
| `settings.cosmeticsHint` | Do'kondan olingan muqova, ramka va nishonlar. Har turdan bittasini kiyish mumkin. | Муқова, чорчӯба ва нишонҳо аз мағоза. Аз ҳар навъ як доно пӯшидан мумкин. |  |
| `settings.cosmeticsShop` | Do'konga o'tish | Ба мағоза гузаштан |  |
| `settings.country` | Mamlakat | Кишвар |  |
| `settings.degree` | Yo'nalish yoki daraja | Самт ё дараҷа |  |
| `settings.education` | Ta'lim | Таҳсил |  |
| `settings.effect` | Mavzu almashish effekti | Эффекти ивази мавзӯъ |  |
| `settings.effect.circle` | Doira | Доира |  |
| `settings.effect.fade` | Silliq o'tish | Гузариши ҳамвор |  |
| `settings.effect.none` | Effektsiz | Бе эффект |  |
| `settings.effectHint` | Harakatni kamaytirish yoqilgan qurilmada mavzu effektsiz almashadi. | Дар дастгоҳе, ки коҳиши ҳаракат фаъол аст, мавзӯъ бе эффект иваз мешавад. |  |
| `settings.effectsTitle` | Ovoz va effektlar | Садо ва эффектҳо |  |
| `settings.email` | Pochta manzili | Суроғаи почта |  |
| `settings.emailCode` | Tasdiqlash kodi | Рамзи тасдиқ |  |
| `settings.emailCodeSent` | Kod {email} ga yuborildi. Uni shu yerga kiriting. | Рамз ба {email} фиристода шуд. Онро дар ин ҷо ворид кунед. |  |
| `settings.emailConfirm` | Tasdiqlash | Тасдиқ кардан |  |
| `settings.emailCurrent` | Hozirgi manzil: {email} | Суроғаи ҷорӣ: {email} |  |
| `settings.emailDone` | Pochta manzili almashtirildi | Суроғаи почта иваз шуд |  |
| `settings.emailHint` | Manzil yangi pochtaga yuborilgan kod tasdiqlangandan keyingina almashadi. Eski manzilga ogohlantirish yuboriladi. | Суроға танҳо пас аз тасдиқи рамзе, ки ба почтаи нав фиристода шудааст, иваз мешавад. Ба суроғаи кӯҳна огоҳӣ фиристода мешавад. |  |
| `settings.emailNew` | Yangi manzil | Суроғаи нав |  |
| `settings.emailNone` | Pochta manzili ko'rsatilmagan | Суроғаи почта нишон дода нашудааст |  |
| `settings.emailSend` | Kod yuborish | Фиристодани рамз |  |
| `settings.emailUnverified` | Tasdiqlanmagan | Тасдиқнашуда |  |
| `settings.emailVerified` | Tasdiqlangan | Тасдиқшуда |  |
| `settings.endYear` | Tugagan yili | Соли анҷом |  |
| `settings.endYearHint` | Bo'sh qoldiring — hozir ham shu yerda | Холӣ монед — агар ҳоло ҳам дар ин ҷо бошед |  |
| `settings.external` | Boshqa platformalardagi profillar | Профилҳо дар платформаҳои дигар |  |
| `settings.externalHint` | Handle yoki profil havolasini kiriting. Reyting ochiq API'dan olinadi va bizning reytingga aralashmaydi. | Handle ё пайванди профилро ворид кунед. Рейтинг аз API-и кушода гирифта мешавад ва ба рейтинги мо таъсир намерасонад. |  |
| `settings.externalNoRating` | Reytingli musobaqa topilmadi | Мусобиқаи рейтингдор ёфт нашуд |  |
| `settings.externalPending` | Reyting olinmoqda… | Рейтинг гирифта мешавад… |  |
| `settings.externalRating` | Reyting: {rating} (eng yuqori {max}) | Рейтинг: {rating} (баландтарин {max}) |  |
| `settings.grade` | Sinf yoki kurs | Синф ё курс |  |
| `settings.info` | Shaxsiy ma'lumotlar | Маълумоти шахсӣ |  |
| `settings.infoHint` | Hammasi ixtiyoriy. Standart holatda profilda ko'rinadi — istalganini yashirishingiz mumkin. | Ҳама ихтиёрӣ аст. Бо нобаёнӣ дар профил намоён аст — ҳар кадомашро пинҳон карда метавонед. |  |
| `settings.kind.contest_result` | Musobaqa natijasi | Натиҷаи мусобиқа |  |
| `settings.kind.duel` | Duellar | Дуэлҳо |  |
| `settings.kind.hack` | Hack natijasi | Натиҷаи шикастан |  |
| `settings.kind.problem_rerated` | Masala qayta baholandi | Масъала аз нав баҳогузорӣ шуд |  |
| `settings.kind.quest_awarded` | Vazifa mukofoti | Мукофоти супориш |  |
| `settings.kind.rating_changed` | Reyting o'zgarishi | Тағйири рейтинг |  |
| `settings.kind.streak_milestone` | Streak yutug'i | Дастоварди streak |  |
| `settings.kind.system` | Tizim xabarlari | Паёмҳои система |  |
| `settings.kindColumn` | Tur | Навъ |  |
| `settings.language` | Til | Забон |  |
| `settings.linkedinHint` | https://linkedin.com/in/… ko'rinishida | Дар шакли https://linkedin.com/in/… |  |
| `settings.loading` | Yuklanmoqda… | Боргирӣ… |  |
| `settings.nav.account` | Hisob | Ҳисоб |  |
| `settings.nav.appearance` | Ko'rinish | Намуди зоҳирӣ |  |
| `settings.nav.career` | Ta'lim va ish | Таҳсил ва кор |  |
| `settings.nav.info` | Ma'lumotlar | Маълумот |  |
| `settings.nav.notifications` | Bildirishnomalar | Огоҳиномаҳо |  |
| `settings.nav.profile` | Profil | Профил |  |
| `settings.nav.security` | Xavfsizlik | Амният |  |
| `settings.nav.skills` | Ko'nikmalar | Малакаҳо |  |
| `settings.nav.social` | Ijtimoiy tarmoqlar | Шабакаҳои иҷтимоӣ |  |
| `settings.nav.teams` | Jamoalar | Дастаҳо |  |
| `settings.notChosen` | Tanlanmagan | Интихоб нашудааст |  |
| `settings.notify` | Bildirishnomalar | Огоҳиномаҳо |  |
| `settings.notifyHint` | Har bir tur uchun qayerga yuborilishini tanlang. | Барои ҳар навъ интихоб кунед, ки ба куҷо фиристода шавад. |  |
| `settings.organization` | Muassasa | Муассиса |  |
| `settings.password` | Parol | Парол |  |
| `settings.passwordChange` | Parolni almashtirish | Иваз кардани парол |  |
| `settings.passwordCurrent` | Joriy parol | Пароли ҷорӣ |  |
| `settings.passwordDone` | Parol saqlandi. Boshqa qurilmalardagi kirishlar yopildi. | Парол нигоҳ дошта шуд. Воридшавӣ дар дастгоҳҳои дигар баста шуд. |  |
| `settings.passwordNew` | Yangi parol | Пароли нав |  |
| `settings.passwordSet` | Parol o'rnatish | Гузоштани парол |  |
| `settings.passwordSetHint` | Hisobingizda parol yo'q — siz faqat Google, GitHub yoki Telegram bilan kirasiz. Parol o'rnatsangiz, taxallus va parol bilan ham kira olasiz. | Ҳисоби шумо парол надорад — шумо танҳо тавассути Google, GitHub ё Telegram ворид мешавед. Парол гузоред, то бо тахаллус низ ворид шавед. |  |
| `settings.position` | Lavozim | Вазифа |  |
| `settings.region` | Viloyat | Вилоят |  |
| `settings.remove` | O'chirish | Нест кардан |  |
| `settings.save` | Saqlash | Нигоҳ доштан |  |
| `settings.saved` | Saqlandi | Нигоҳ дошта шуд |  |
| `settings.school` | Maktab yoki universitet | Мактаб ё донишгоҳ |  |
| `settings.section` | Bo'lim | Бахш |  |
| `settings.selected` | {count} / {max} tanlangan | {count} аз {max} интихоб шуд |  |
| `settings.sessionCurrent` | Shu qurilma | Ҳамин дастгоҳ |  |
| `settings.sessionEnd` | Chiqarish | Хориҷ кардан |  |
| `settings.sessionEndOthers` | Boshqa barcha qurilmalardan chiqish | Аз ҳамаи дастгоҳҳои дигар баромадан |  |
| `settings.sessionSeen` | Oxirgi faollik: {time} | Фаъолияти охирин: {time} |  |
| `settings.sessionUnknown` | Noma'lum qurilma | Дастгоҳи номаълум |  |
| `settings.sessions` | Kirilgan qurilmalar | Дастгоҳҳои воридшуда |  |
| `settings.sessionsHint` | Tanimagan qurilmani ko'rsangiz — uni chiqaring va parolni almashtiring. | Агар дастгоҳи ношиносро бинед — онро хориҷ кунед ва паролро иваз намоед. |  |
| `settings.showEmail` | Pochta manzilini profilda ko'rsatish | Нишон додани почта дар профил |  |
| `settings.showOnProfile` | Profilda ko'rsatish | Дар профил нишон додан |  |
| `settings.skillAdd` | Ko'nikma qo'shish… | Иловаи малака… |  |
| `settings.skills` | Ko'nikmalar | Малакаҳо |  |
| `settings.skillsHint` | O'zingizni baholang — daraja faqat profilda ko'rinadi va reytingga ta'sir qilmaydi. | Худро баҳо диҳед — сатҳ танҳо дар профил намоён аст ва ба рейтинг таъсир намерасонад. |  |
| `settings.slot.badge` | Nishon | Нишон |  |
| `settings.slot.cover` | Muqova | Муқова |  |
| `settings.slot.frame` | Avatar ramkasi | Чорчӯбаи аватар |  |
| `settings.sound` | Ovoz | Садо |  |
| `settings.soundHint` | Yechim qabul qilinganda qisqa ohang chalinadi. | Ҳангоми қабули ҳал оҳанги кӯтоҳ садо медиҳад. |  |
| `settings.soundTry` | Eshitib ko'rish | Гӯш кардан |  |
| `settings.startYear` | Boshlangan yili | Соли оғоз |  |
| `settings.style` | Uslub | Услуб |  |
| `settings.takeOff` | Yechish | Кашидан |  |
| `settings.teamCopied` | Nusxalandi | Нусхабардорӣ шуд |  |
| `settings.teamCopy` | Nusxalash | Нусхабардорӣ |  |
| `settings.teamCreate` | Jamoa yaratish | Сохтани даста |  |
| `settings.teamDelete` | Jamoani o'chirish | Нест кардани даста |  |
| `settings.teamDeleteConfirm` | Jamoa butunlay o'chiriladi. Davom etasizmi? | Даста тамоман нест карда мешавад. Идома медиҳед? |  |
| `settings.teamInvite` | Taklif havolasi | Пайванди даъват |  |
| `settings.teamInvited` | Sizni jamoaga taklif qilishdi — «Qo'shilish» ni bosing. | Шуморо ба даста даъват карданд — «Ҳамроҳ шудан»-ро пахш кунед. |  |
| `settings.teamJoin` | Qo'shilish | Ҳамроҳ шудан |  |
| `settings.teamJoinCode` | Taklif kodi yoki havolasi | Рамз ё пайванди даъват |  |
| `settings.teamJoined` | Jamoaga qo'shildingiz | Шумо ба даста ҳамроҳ шудед |  |
| `settings.teamLeave` | Jamoadan chiqish | Тарк кардани даста |  |
| `settings.teamMember` | A'zo | Аъзо |  |
| `settings.teamName` | Jamoa nomi | Номи даста |  |
| `settings.teamOwner` | Egasi | Соҳиб |  |
| `settings.teamRefresh` | Yangi havola | Пайванди нав |  |
| `settings.teamRefreshHint` | Eski havola ishlamay qoladi. | Пайванди кӯҳна кор намекунад. |  |
| `settings.teamRemove` | Chiqarish | Хориҷ кардан |  |
| `settings.teams` | Jamoalar | Дастаҳо |  |
| `settings.teamsEmpty` | Siz hali hech qaysi jamoada emassiz. | Шумо ҳоло дар ягон даста нестед. |  |
| `settings.teamsHint` | Jamoa yarating va do'stlaringizni havola orqali taklif qiling. Jamoada 10 kishigacha. | Даста созед ва дӯстонро тавассути пайванд даъват кунед. Дар даста то 10 нафар. |  |
| `settings.technologies` | Texnologiyalar | Технологияҳо |  |
| `settings.technologiesHint` | Ishlatadigan til va vositalaringizni belgilang. | Забонҳо ва абзорҳоеро, ки истифода мебаред, қайд кунед. |  |
| `settings.telegramAccess` | Bot sizga yozishi uchun Telegram orqali ulanganda xabar yuborishga ruxsat bering. | Барои он ки бот ба шумо нависад, ҳангоми пайваст кардани Telegram ба фиристодани паём иҷозат диҳед. |  |
| `settings.telegramMissing` | Telegram ulanmagan — uni shu bo'limda ulang: | Telegram пайваст нашудааст — онро дар ин бахш пайваст кунед: |  |
| `settings.theme` | Mavzu | Мавзӯъ |  |
| `settings.themeFixed` | Bu uslub bitta mavzuga chizilgan — yorug'/qorong'u almashmaydi. | Ин услуб барои як мавзӯъ сохта шудааст — равшан/торик иваз намешавад. |  |
| `settings.username` | Taxallus | Тахаллус |  |
| `settings.usernameChange` | Almashtirish | Иваз кардан |  |
| `settings.usernameConfirm` | Taxallusni «{name}» ga almashtirasizmi? | Тахаллусро ба «{name}» иваз мекунед? |  |
| `settings.usernameDone` | Taxallus almashtirildi | Тахаллус иваз шуд |  |
| `settings.usernameFree` | Yiliga bir marta bepul almashtirish mumkin — hozir mavjud. | Соле як бор ройгон иваз кардан мумкин — ҳоло дастрас аст. |  |
| `settings.usernameKept` | Eski taxallus 90 kun band turadi va sizning profilingizga yo'naltiradi. | Тахаллуси кӯҳна 90 рӯз банд мемонад ва ба профили шумо равона мекунад. |  |
| `settings.usernameNew` | Yangi taxallus | Тахаллуси нав |  |
| `settings.usernameNextFree` | Keyingi bepul almashtirish: {date}. Undan oldin — {price} Qvant. | Ивази ройгони навбатӣ: {date}. То он вақт — {price} Qvant. |  |
| `settings.usernamePay` | {price} Qvant evaziga almashtirish | Иваз кардан бо {price} Qvant |  |
| `settings.wear` | Kiyish | Пӯшидан |  |
| `settings.website` | Veb-sayt | Вебсайт |  |
| `settings.work` | Ish tajribasi | Таҷрибаи корӣ |  |
| `level.beginner` | Boshlang'ich | Ибтидоӣ |  |
| `level.basic` | Asosiy | Асосӣ |  |
| `level.intermediate` | O'rta | Миёна |  |
| `level.upper` | Yaxshi | Хуб |  |
| `level.hard` | Qiyin | Душвор |  |
| `level.expert` | Ekspert | Коршинос |  |
| `level.master` | Master | Устод |  |
| `loading.label` | Yuklanmoqda | Бор шуда истодааст |  |
| `loading.style.spinner` | Aylanuvchi yoy | Камончаи чархзананда |  |
| `loading.style.spinnerHint` | Eng tushunarli va eng arzon. Tugma ichida ham ishlaydi. | Фаҳмотарин ва арзонтарин. Дар дохили тугма ҳам кор мекунад. |  |
| `loading.style.ring` | Uzuk | Ҳалқа |  |
| `loading.style.ringHint` | SVG uzuk — chiziq qalinligi bir xil, kattaroq joy uchun. | Ҳалқаи SVG — ғафсӣ якхела, барои ҷои калонтар. |  |
| `loading.style.skeleton` | Skeleton | Скелетон |  |
| `loading.style.skeletonHint` | Kulrang ustunlar — kelayotgan kontent joyini oldin egallaydi. | Хатҳои хокистарӣ, ки ҷои мазмуни ояндаро пешакӣ мегиранд. |  |
| `loading.style.shimmer` | Shimmer | Дурахш |  |
| `loading.style.shimmerHint` | Yorug'lik chapdan o'ngga o'tadi — jonli tuyuladi. | Рӯшноӣ аз чап ба рост меравад — зинда менамояд. |  |
| `loading.style.dotsBounce` | Sakrayotgan nuqtalar | Нуқтаҳои ҷаҳанда |  |
| `loading.style.dotsBounceHint` | «Yozmoqda…» kabi qisqa kutish uchun. | Барои интизори кӯтоҳ, мисли «навишта истодааст». |  |
| `loading.style.dotsFade` | So'nayotgan nuqtalar | Нуқтаҳои хомӯшшаванда |  |
| `loading.style.dotsFadeHint` | Sokinroq — fon amallari uchun. | Оромтар — барои амалҳои заминавӣ. |  |
| `loading.style.bars` | Ekvalayzer | Эквалайзер |  |
| `loading.style.barsHint` | Media va real vaqt oqimi uchun. | Барои медиа ва ҷараёнҳои зинда. |  |
| `loading.style.iconSpin` | Aylanuvchi ikonka | Нишонаи чархзананда |  |
| `loading.style.iconSpinHint` | «Yangilash» ma'nosini beradi — tugma ichida. | Маънои «навсозӣ» медиҳад — дар дохили тугма. |  |
| `loading.style.pulseIcon` | Pulsatsiyalanuvchi ikonka | Нишонаи набзнок |  |
| `loading.style.pulseIconHint` | Live indikator uchun. | Барои индикатори зинда. |  |
| `loading.style.progress` | Progress chizig'i | Хатти пешрафт |  |
| `loading.style.progressHint` | Sahifa yuqorisi yoki uzoq amal uchun. | Барои болои саҳифа ё кори тӯлонӣ. |  |
| `title.kvark` | Kvark | Кварк |  |
| `title.foton` | Foton | Фотон |  |
| `title.elektron` | Elektron | Электрон |  |
| `title.proton` | Proton | Протон |  |
| `title.atom` | Atom | Атом |  |
| `title.molekula` | Molekula | Молекула |  |
| `title.kristal` | Kristal | Кристалл |  |
| `title.yulduz` | Yulduz | Ситора |  |
| `title.galaktika` | Galaktika | Галактика |  |
| `profile.acceptance` | Qabul qilingan urinishlar: {rate}% | Кӯшишҳои қабулшуда: {rate}% |  |
| `profile.accepted` | qabul | қабул |  |
| `profile.errors` | xato | хато |  |
| `profile.allLanguages` | Hamma tillar | Ҳамаи забонҳо |  |
| `profile.bestMemory` | Xotira | Хотира |  |
| `profile.bestTime` | Eng yaxshi vaqt | Беҳтарин вақт |  |
| `profile.chartEmpty` | Reyting hali o'zgarmagan. | Рейтинг ҳанӯз тағйир наёфтааст. |  |
| `profile.chartKeys` | Reyting grafigi: nuqtalar orasida chap va o'ng strelka bilan yuring | Графики рейтинг: байни нуқтаҳо бо тирчаҳои чап ва рост ҳаракат кунед |  |
| `profile.clearFilter` | filtrni olib tashlash | бекор кардани филтр |  |
| `profile.contestCol` | Musobaqa | Мусобиқа |  |
| `profile.contestsEmpty` | Hali musobaqada qatnashmagan. | Ҳанӯз дар мусобиқа иштирок накардааст. |  |
| `profile.contestsHint` | Faqat ommaviy musobaqalar. Teng natija bo'lsa o'rin oraliq bilan yoziladi (masalan 33–35). | Танҳо мусобиқаҳои кушода. Ҳангоми натиҷаи баробар ҷой бо фосила навишта мешавад (масалан, 33–35). |  |
| `profile.durationCol` | Davomiyligi | Давомнокӣ |  |
| `profile.filterByProblem` | Faqat shu masala urinishlari | Танҳо кӯшишҳои ҳамин масъала |  |
| `profile.firstAc` | Birinchi AC | AC-и аввал |  |
| `profile.heatmapHint` | Har kvadrat — bir kun: rang qanchalik to'q bo'lsa, shuncha ko'p urinish. Ustiga borib aniq sonni ko'ring. | Ҳар мураббаъ — як рӯз: ҳар қадар ранг торик бошад, ҳамон қадар кӯшиш бисёр. Барои дидани адади дақиқ курсорро болои он баред. |  |
| `profile.heatmapTip` | {date}: {attempts} ta urinish, {solved} ta yangi yechim | {date}: {attempts} кӯшиш, {solved} ҳалли нав |  |
| `profile.heatmapTitle` | Faollik xaritasi | Харитаи фаъолият |  |
| `profile.heatmapTotal` | {year}-yil: {attempts} ta urinish, {solved} ta yangi yechim | Соли {year}: {attempts} кӯшиш, {solved} ҳалли нав |  |
| `profile.hintActivity` | 30 kunlik faollik: faol kunlar, vazifalar va streak. | Фаъолияти 30-рӯза: рӯзҳои фаъол, супоришҳо ва streak. |  |
| `profile.hintContests` | Musobaqa natijalaridan (Elo): kimdan yuqori o'rin olganingizga qarab o'zgaradi. | Аз натиҷаҳои мусобиқа (Elo): вобаста ба он ки аз кӣ болотар ҷой гирифтед. |  |
| `profile.hintSkills` | Yechilgan masalalar qiyinligidan: yangi va qiyinroq masala ko'proq qo'shadi. | Аз душвории масъалаҳои ҳалшуда: масъалаи нав ва душвортар бештар илова мекунад. |  |
| `profile.hintStreak` | Ketma-ket AC olingan kunlar soni. | Шумораи рӯзҳои пайдарпай бо AC. |  |
| `profile.kindCol` | Turi | Навъ |  |
| `profile.languagesCol` | Tillar | Забонҳо |  |
| `profile.languagesHint` | Har til bo'yicha qabul qilingan va xato urinishlar. Infra xatolari hisobga olinmaydi. | Кӯшишҳои қабулшуда ва хато аз рӯи ҳар забон. Хатоҳои инфрасохтор ҳисоб намешаванд. |  |
| `profile.languagesTitle` | Dasturlash tillari | Забонҳои барномасозӣ |  |
| `profile.less` | Kamroq | Камтар |  |
| `profile.more` | Ko'proq | Бештар |  |
| `profile.mapByCode` | Raqam tartibida | Аз рӯи рақам |  |
| `profile.mapByLevel` | Daraja bo'yicha | Аз рӯи сатҳ |  |
| `profile.mapHint` | Arxivdagi har masala: yashil — yechilgan, sariq — urinilgan, kulrang — tegilmagan. Katak shu masaladagi urinishlarni ochadi. | Ҳар масъалаи бойгонӣ: сабз — ҳалшуда, зард — кӯшиш шуда, хокистарӣ — даст нарасида. Катак кӯшишҳои ҳамин масъаларо мекушояд. |  |
| `profile.mapTitle` | Masalalar xaritasi | Харитаи масъалаҳо |  |
| `profile.memberSince` | Ro'yxatdan o'tgan sana | Санаи сабти ном |  |
| `profile.official` | Rasmiy | Расмӣ |  |
| `profile.participants` | Ishtirokchilar | Иштирокчиён |  |
| `profile.problemsCol` | Masalalar | Масъалаҳо |  |
| `profile.ratingChange` | Reyting o'zgarishi | Тағйири рейтинг |  |
| `profile.ratingHint` | Nuqta ustiga boring: musobaqa, o'rin va o'zgarish ko'rinadi. Rangli yo'laklar — unvon chegaralari. | Курсорро болои нуқта баред: мусобиқа, ҷой ва тағйир намоён мешавад. Хатҳои ранга — ҳудуди унвонҳо. |  |
| `profile.reason.contest` | musobaqa | мусобиқа |  |
| `profile.reason.duel` | duel | дуэл |  |
| `profile.reason.problem_rerated` | masala qayta baholandi | масъала аз нав баҳогузорӣ шуд |  |
| `profile.reason.problem_solved` | masala yechildi | масъала ҳал шуд |  |
| `profile.reason.recalculation` | qayta hisoblash | аз нав ҳисобкунӣ |  |
| `profile.search` | Qidirish | Ҷустуҷӯ |  |
| `profile.searchContests` | Musobaqa nomi… | Номи мусобиқа… |  |
| `profile.searchSolved` | Masala nomi yoki raqami… | Ном ё рақами масъала… |  |
| `profile.share` | Ulashish | Мубодила |  |
| `profile.shareCopied` | Havola nusxalandi | Пайванд нусхабардорӣ шуд |  |
| `profile.solvedHint` | Arxivdagi ommaviy masalalardan nechtasi yechilgan va daraja bo'yicha taqsimot. | Чанд масъалаи кушодаи бойгонӣ ҳал шудааст ва тақсимот аз рӯи сатҳ. |  |
| `profile.solvedTitle` | Yechilgan masalalar | Масъалаҳои ҳалшуда |  |
| `profile.sortDifficulty` | Qiyinlik bo'yicha | Аз рӯи душворӣ |  |
| `profile.sortNewest` | Avval yangilari | Аввал навҳо |  |
| `profile.sortOldest` | Avval eskilari | Аввал кӯҳнаҳо |  |
| `profile.sortTitle` | Nomi bo'yicha | Аз рӯи ном |  |
| `profile.startCol` | Boshlanishi | Оғоз |  |
| `profile.stateAttempted` | Urinilgan | Кӯшиш шуда |  |
| `profile.stateSolved` | Yechilgan | Ҳалшуда |  |
| `profile.stateUntouched` | Tegilmagan | Даст нарасида |  |
| `profile.streakCurrent` | Joriy streak: {n} kun | Streak-и ҷорӣ: {n} рӯз |  |
| `profile.streakLongest` | Eng uzuni: {n} kun | Дарозтарин: {n} рӯз |  |
| `profile.tab.attempts` | Urinishlar | Кӯшишҳо |  |
| `profile.tab.contests` | Musobaqalar | Мусобиқаҳо |  |
| `profile.tab.overview` | Umumiy | Умумӣ |  |
| `profile.tab.solved` | Yechilganlar | Ҳалшудаҳо |  |
| `profile.topicStuck` | ({n} ta tiqilgan) | ({n} мондагӣ) |  |
| `profile.topicsHint` | Skills formulasi mavzu kesimida: yechilganlar qiyinligidan. «Tiqilgan» — urinilgan, lekin yechilmagan. | Формулаи Skills аз рӯи мавзӯъ: аз душвории масъалаҳои ҳалшуда. «Мондагӣ» — кӯшиш шуда, вале ҳал нашудааст. |  |
| `profile.topicsTitle` | Mavzular bo'yicha kuch | Қувва аз рӯи мавзӯъҳо |  |
| `profile.verdictOther` | Boshqa | Дигар |  |
| `profile.verdictsHint` | Barcha tekshirilgan urinishlar. Markazda — qabul qilinganlar ulushi. | Ҳамаи кӯшишҳои санҷидашуда. Дар марказ — ҳиссаи қабулшудаҳо. |  |
| `profile.verdictsTitle` | Verdiktlar | Вердиктҳо |  |
| `profile.viewChips` | Chiplar | Нишонаҳо |  |
| `profile.viewTable` | Jadval | Ҷадвал |  |
| `profile.virtual` | Virtual | Виртуалӣ |  |
| `profile.year` | Yil | Сол |  |
| `role.staff` | Xodim | Корманд |  |
| `role.author` | Masala muallifi | Муаллифи масъала |  |
| `role.jury` | Hakam | Ҳакам |  |
| `role.champion` | Chempion | Қаҳрамон |  |
| `role.championOf` | {contest} g'olibi | Ғолиби {contest} |  |
| `profile.online` | Onlayn | Онлайн |  |
| `profile.lastSeen` | Oxirgi faollik: {time} | Охирин фаъолият: {time} |  |
| `profile.titleHint` | Unvon Contests reytingidan | Унвон аз рейтинги Contests |  |
| `settings.showOnline` | Onlayn holat va oxirgi faollikni ko'rsatish | Намоиши ҳолати онлайн ва охирин фаъолият |  |
| `tier.bronze` | Bronza | Биринҷӣ |  |
| `tier.silver` | Kumush | Нуқра |  |
| `tier.gold` | Oltin | Тилло |  |
| `profile.rarity` | {pct}% foydalanuvchida bor | Дар {pct}% корбарон ҳаст |  |
| `profile.achievedOn` | Olingan: {date} | Гирифта шуд: {date} |  |
| `profile.pin` | Profilga qo'yish | Ба профил гузоштан |  |
| `profile.unpin` | Profildan olish | Аз профил гирифтан |  |
| `profile.pinLimit` | Ko'pi bilan uchta yutuq tanlanadi | Ҳадди аксар се дастовард |  |
| `profile.pinnedTitle` | Tanlangan yutuqlar | Дастовардҳои интихобшуда |  |
| `profile.pinHint` | Uchtagacha yutuqni tanlang — ular profil kartasida ko'rinadi. | То се дастовардро интихоб кунед — онҳо дар корти профил намоён мешаванд. |  |
| `profile.tab.certificates` | Sertifikatlar | Сертификатҳо |  |
| `profile.certificatesHint` | Rasmiy musobaqada kamida bitta yechim yuborgan har bir ishtirokchiga beriladi. Haqiqiyligini QR yoki ID orqali tekshirish mumkin. | Ба ҳар иштирокчие дода мешавад, ки дар мусобиқаи расмӣ ақаллан як ҳал фиристодааст. Аслиятро тавассути QR ё ID санҷидан мумкин. |  |
| `profile.certificatesEmpty` | Hali sertifikat yo'q. | Ҳоло сертификат нест. |  |
| `cert.title` | Sertifikat | Сертификат |  |
| `cert.tier.gold` | 1-o'rin | Ҷойи 1 |  |
| `cert.tier.silver` | 2-o'rin | Ҷойи 2 |  |
| `cert.tier.bronze` | 3-o'rin | Ҷойи 3 |  |
| `cert.tier.top10` | Eng yaxshi 10% | Беҳтарин 10% |  |
| `cert.tier.participant` | Ishtirokchi | Иштирокчӣ |  |
| `cert.place` | {place}-o'rin · {total} ishtirokchi | Ҷойи {place} аз {total} |  |
| `cert.verify` | Tekshirish | Санҷиш |  |
| `cert.valid` | Bu sertifikat haqiqiy — RankWant tomonidan berilgan. | Ин сертификат аслӣ аст — аз ҷониби RankWant дода шудааст. |  |
| `cert.id` | Sertifikat ID | ID-и сертификат |  |
| `cert.issued` | Berilgan sana | Санаи додан |  |
| `cert.holder` | Egasi | Соҳиб |  |
| `profile.coach` | Murabbiy | Мураббӣ |  |
| `profile.searchPeople` | Ism yoki taxallus… | Ном ё тахаллус… |  |
| `profile.sortBy` | Saralash | Мураттабсозӣ |  |
| `profile.sortRating` | Contests reytingi bo'yicha | Аз рӯи рейтинги Contests |  |
| `profile.sortName` | Taxallus bo'yicha | Аз рӯи тахаллус |  |
| `profile.lastActivityCol` | Oxirgi faollik | Охирин фаъолият |  |
| `profile.schoolRanking` | Maktab reytingi | Рейтинги мактаб |  |
| `settings.district` | Tuman yoki shahar | Ноҳия ё шаҳр |  |
| `settings.districts` | Tumanlar | Ноҳияҳо |  |
| `settings.cities` | Shaharlar | Шаҳрҳо |  |
| `settings.city` | Shahar | Шаҳр |  |
| `settings.showCoach` | Murabbiyni ko'rsatish | Намоиши мураббӣ |  |
| `settings.showSocial` | Ijtimoiy havolalarni ko'rsatish | Намоиши пайвандҳои иҷтимоӣ |  |
| `settings.schoolFromCatalog` | Katalogdan tanlandi — maktab reytingida ko'rinasiz | Аз каталог интихоб шуд — шумо дар рейтинги мактаб ҳастед |  |
| `settings.schoolFreeText` | Katalogdan tanlang yoki o'zingiz yozing | Аз каталог интихоб кунед ё худатон нависед |  |
| `settings.phone` | Telefon raqami | Рақами телефон |  |
| `settings.phoneHint` | Ixtiyoriy. Hisobni tiklash va musobaqa bildirishnomalari uchun. Profilingizda ko'rinmaydi. | Ҳатмӣ нест. Барои барқарорсозии ҳисоб ва огоҳиномаҳои мусобиқа. Дар профил нишон дода намешавад. |  |
| `settings.fromConnected` | Ulangan hisobdan: @{handle} | Аз ҳисоби пайвастшуда: @{handle} |  |
| `settings.blogHint` | https:// bilan boshlanadigan manzil | Суроғае, ки бо https:// оғоз мешавад |  |
| `leaderboard.school` | «{school}» reytingi | Рейтинги «{school}» |  |
| `leaderboard.schoolAll` | Umumiy reyting | Рейтинги умумӣ |  |
| `auth.tabLogin` | Kirish | Даромадан |  |
| `auth.tabRegister` | Ro'yxatdan o'tish | Бақайдгирӣ |  |
| `auth.tabReset` | Parolni tiklash | Барқарорсозии рамз |  |
| `auth.tabHint` | Bo'limni tanlang | Бахшро интихоб кунед |  |
| `auth.usernameOrEmail` | Foydalanuvchi nomi yoki email | Номи корбар ё email |  |
| `auth.identifierHint` | Taxallusingizni yoki emailingizni kiriting | Тахаллус ё emailи худро ворид кунед |  |
| `auth.haveAccount` | Hisobingiz bormi? Kirish | Ҳисоб доред? Даромадан |  |
| `auth.notFoundEmail` | Bu email bilan hisob topilmadi. Ro'yxatdan o'tishingiz mumkin. | Ҳисоб бо ин email ёфт нашуд. Метавонед бақайд гиред. |  |
| `auth.notFoundReset` | Bu email bilan hisob topilmadi. Ro'yxatdan o'tish | Ҳисоб бо ин email ёфт нашуд. Бақайдгирӣ |  |
| `auth.emailTaken` | Bu email allaqachon band. Kirish yoki parolni tiklash mumkin. | Ин email банд аст. Метавонед дароед ё рамзро барқарор кунед. |  |
| `auth.usernameTaken` | Bu foydalanuvchi nomi band. Boshqasini tanlang. | Ин номи корбар банд аст. Дигареро интихоб кунед. |  |
| `auth.throttledWait` | Juda tez-tez urinyapsiz. {seconds} soniyadan keyin qayta urinib ko'ring. | Кӯшишҳо аз ҳад зиёд. Баъди {seconds} сония такрор кунед. |  |
| `auth.step2ProfileTitle` | Taxallusni tanlang | Тахаллуси худро интихоб кунед |  |
| `auth.socialProof` | {count} ta dasturchi reyting uchun bellashadi | {count} барномасоз барои рейтинг рақобат мекунанд |  |
| `auth.contestInvite` | AtCoder va Codeforcesdagi natijangizni qo'shing — reyting aniqroq bo'ladi. | Натиҷаҳои AtCoder ва Codeforces-ро илова кунед — рейтинг дақиқтар мешавад. |  |
| `auth.contestInviteCta` | Natijani qo'shish | Илова кардани натиҷа |  |
| `auth.country` | Mamlakat | Кишвар |  |
| `auth.remember` | Meni eslab qol | Маро дар ёд нигоҳ дор |  |
| `auth.termsAccept` | Shartlar va maxfiylik siyosatiga roziman | Ман бо шартҳо ва сиёсати махфият розӣ ҳастам |  |
| `auth.marketingOptIn` | Yangiliklar va foydali xatlarni olishni xohlayman (ixtiyoriy) | Мехоҳам хабарҳо ва номаҳои муфид гирам (ихтиёрӣ) |  |
| `auth.termsRequired` | Shartlarga rozilik majburiy | Розигӣ бо шартҳо ҳатмист |  |
| `auth.step2Title` | Joy va maktab | Ҷой ва мактаб |  |
| `auth.step2Body` | Bu ma'lumot maktab reytingida ko'rinish uchun kerak. Hozir o'tkazib yuborsangiz ham bo'ladi — keyin sozlamalarda to'ldirasiz. | Ин маълумот барои дида шудан дар рейтинги мактабҳо лозим аст. Ҳозир метавонед гузаред — баъдтар дар танзимот пур мекунед. |  |
| `auth.skip` | O'tkazib yuborish | Гузаштан |  |
| `auth.schoolSearch` | Maktab nomi bo'yicha qidirish | Ҷустуҷӯ аз рӯи номи мактаб |  |
| `auth.tagline` | Reyting xohlaganlar uchun | Барои хоҳишмандони рейтинг |  |
| `auth.members` | A'zolar | Аъзоён |  |
| `geo.nudgeTitle` | Davlat va maktabingizni qo'shing | Кишвар ва мактаби худро илова кунед |  |
| `geo.nudgeBody` | Maktab reytingida ko'rinish uchun kerak — 20 soniya vaqt oladi. | Барои дида шудан дар рейтинги мактабҳо лозим — 20 сония мегирад. |  |
| `geo.nudgeCta` | To'ldirish | Пур кардан |  |
| `geo.searchPlaceholder` | Mamlakat qidirish | Ҷустуҷӯи кишвар |  |
| `geo.noResults` | Topilmadi | Ёфт нашуд |  |
| `locale.switchLabel` | Tilni tanlang | Забонро интихоб кунед |  |
| `locale.auto` | Avtomatik | Худкор |  |
| `locale.autoDetected` | Avtomatik ({language}) | Худкор ({language}) |  |
| `locale.group.core` | Asosiy | Асосӣ |  |
| `locale.group.region` | Mintaqa | Минтақавӣ |  |
| `locale.group.broad` | Keng qamrov | Фароҳи васеъ |  |
| `locale.loading` | Yuklanmoqda | Боргирӣ |  |
| `locale.listLabel` | Tillar ro'yxati | Рӯйхати забонҳо |  |
| `content.uzOnly` | Bu nom o'zbekcha — tarjimasi tayyorlanmoqda | Ин ном ба забони ӯзбекӣ аст — тарҷума омода мешавад |  |
| `problem.tab.statement` | Tavsif | Шарт |  |
| `problem.tab.status` | Urinishlar | Фиристодаҳо |  |
| `problem.tab.stats` | Statistika | Омор |  |
| `problem.tab.solvers` | Yechganlar | Ҳалкунандагон |  |
| `problem.tab.mine` | Urinishlarim | Кӯшишҳои ман |  |
| `problem.tab.myStats` | Statistikam | Омори ман |  |
| `problem.tab.favourites` | Sevimlilar | Дӯстдоштаҳо |  |
| `problem.tabsLabel` | Masala bo'limlari | Бахшҳои масъала |  |
| `problem.solvers.count` | Bu masalani {count} kishi yechdi | Ҳал кардаанд: {count} |  |
| `problem.solvers.none` | Hali hech kim yechmagan | То ҳол ҳеҷ кас ҳал накардааст |  |
| `problem.solvers.first` | Birinchi yechgan | Аввалин ҳалкунанда |  |
| `problem.solvers.fast` | Eng tez | Суръаттарин |  |
| `problem.solvers.short` | Eng qisqa yechim | Кӯтоҳтарин ҳал |  |
| `problem.solvers.tries` | Eng kam urinish | Камтарин кӯшиш |  |
| `problem.voteUp` | Yoqdi | Маъқул |  |
| `problem.voteDown` | Yoqmadi | Ноқулай |  |
| `problem.voteUpTitle` | Yoqdi — bir bosishda ovoz berish | Маъқул — бо як зер даъват |  |
| `problem.voteDownTitle` | Yoqmadi — bir bosishda ovoz berish | Ноқулай — бо як зер даъват |  |
| `problem.ratingSummary` | {average} · {count} baho | {average} · {count} баҳо |  |
| `problem.ratingEmpty` | Baho yo'q | Баҳо нест |  |
| `problem.rateWith` | {score} baho berish | {score} баҳо додан |  |
| `problem.inFavourites` | ★ Sevimlilarda | ★ Дар интихобшудаҳо |  |
| `problem.addFavourite` | ☆ Sevimlilarga | ☆ Ба интихобшудаҳо |  |
| `problem.favouriteOn` | {title} — sevimlilardan olib tashlash | {title} — аз интихобшудаҳо гирифтан |  |
| `problem.favouriteOff` | {title} — sevimlilarga qo'shish | {title} — ба интихобшудаҳо илова кардан |  |
| `problem.statementSizeDown` | Shriftni kichraytirish | Хатро хурд кардан |  |
| `problem.statementSizeUp` | Shriftni kattalashtirish | Хатро калон кардан |  |
| `problem.samples` | Namunalar | Намунаҳо |  |
| `problem.sampleInput` | Kirish | Вуруд |  |
| `problem.sampleOutput` | Chiqish | Баромад |  |
| `problem.copy` | Nusxalash | Нусхабардорӣ |  |
| `problem.copied` | Nusxalandi | Нусхабардорӣ шуд |  |
| `problem.copyInput` | {order}-namuna kirishini nusxalash | Вуруди намунаи {order}-ро нусхабардорӣ кардан |  |
| `problem.copyOutput` | {order}-namuna chiqishini nusxalash | Баромади намунаи {order}-ро нусхабардорӣ кардан |  |
| `problem.attachments` | Biriktirilgan fayllar | Замимаҳо |  |
| `problem.similar` | O'xshash masalalar | Масъалаҳои монанд |  |
| `filter.sort.easiest` | Eng oson | Аввал осон |  |
| `filter.sort.hardest` | Eng qiyin | Аввал душвор |  |
| `filter.sort.mostSolved` | Ko'p yechilgan | Бештарин ҳалшуда |  |
| `filter.sort.newest` | Yangi | Навтарин |  |
| `filter.status.unsolved` | Yechilmagan | Ҳалнашуда |  |
| `filter.status.solved` | Yechilgan | Ҳалшуда |  |
| `filter.status.attempted` | Urinib ko'rgan | Кӯшишшуда |  |
| `filter.status.favourites` | Sevimlilarim | Дӯстдоштаҳо |  |
| `filter.status.recommended` | Menga tavsiya | Барои ман тавсияшуда |  |
| `filter.sortLabel` | Saralash | Тартиб |  |
| `filter.filters` | Filtrlar | Филтрҳо |  |
| `filter.clear` | Filtrlarni tozalash | Филтрҳоро тоза кардан |  |
| `filter.searchPlaceholder` | Masala qidirish… | Ҷустуҷӯи масъала… |  |
| `filter.searchLabel` | Masala qidirish | Ҷустуҷӯи масъала |  |
| `filter.levelLabel` | Daraja | Сатҳ |  |
| `filter.statusLabel` | Holat | Ҳолат |  |
| `filter.all` | Hammasi | Ҳама |  |
| `filter.topicsLabel` | Mavzular | Мавзӯъҳо |  |
| `filter.showAllTopics` |  (hammasi) |  (ҳама) |  |
| `filter.statementLocaleLabel` | Matn tili | Забони шарт |  |
| `filter.viewLabel` | Ko'rinish | Намуд |  |
| `filter.hideTagsUnsolved` | Yechilmaganlarda mavzuni yashirish | Пинҳон кардани мавзӯъҳо барои масъалаҳои ҳалнашуда |  |
| `filter.topicSearchPlaceholder` | {count} ta mavzudan qidirish… | Ҷустуҷӯ дар байни {count} мавзӯъ… |  |
| `filter.topicSearchLabel` | Mavzu qidirish | Ҷустуҷӯи мавзӯъ |  |
| `filter.noTopicMatch` | Bunday mavzu yo'q | Чунин мавзӯъ нест |  |
| `editorial.title` | Yechim tahlili | Таҳлили ҳал |  |
| `editorial.lockedTitle` | Tahlil hisobga kirgan foydalanuvchilar uchun. | Таҳлил барои корбарони воридшуда дастрас аст. |  |
| `editorial.login` | Kirish | Даромадан |  |
| `editorial.solvedFree` | Masalani yechdingiz — tahlil ochiq. | Шумо ҳал кардед — таҳлил кушода аст. |  |
| `editorial.free` | Bepul | Ройгон |  |
| `editorial.unlockFor` | Ochish — {price} Qvant | Кушодан — {price} Qvant |  |
| `editorial.unlocking` | Ochilmoqda… | Кушода мешавад… |  |
| `editorial.show` | Ko'rsatish | Нишон додан |  |
| `editorial.hide` | Yashirish | Пинҳон кардан |  |
| `editorial.open` | Tahlil ochiq. | Таҳлил кушода аст. |  |
| `editorial.notEnough` | Balans yetarli emas — {price} Qvant kerak | Баланс кофӣ нест — {price} Qvant лозим |  |
| `editorial.unlockFailed` | Ochib bo'lmadi, qaytadan urinib ko'ring | Кушодан нашуд — боз кӯшиш кунед |  |
| `editorial.lockedLead` | Masalani yechsangiz tahlil bepul ochiladi. | Агар ҳал кунед, таҳлил ройгон кушода мешавад. |  |
| `editorial.lockedBody` | Va o'shanda undan haqiqiy foyda bo'ladi. Hoziroq ko'rmoqchi bo'lsangiz {price} Qvant. | Ва он гоҳ фоидаи воқеӣ мебахшад. Ҳозир дидан: {price} Qvant. |  |
| `editorial.tryFirst` | O'zingiz urinib ko'rgach oching. | Пас аз кӯшиши худ кушоед. |  |
| `report.open` | Xato topdingizmi? | Хато ёфтед? |  |
| `report.title` | Masaladagi nuqson haqida xabar | Дар бораи нуқси масъала хабар додан |  |
| `report.commentLabel` | Izoh (ixtiyoriy) — qaysi joyda va nima noto'g'ri? | Шарҳ (ихтиёрӣ) — куҷо ва чӣ нодуруст? |  |
| `report.send` | Yuborish | Фиристодан |  |
| `report.sending` | Yuborilmoqda… | Фиристода мешавад… |  |
| `report.cancel` | Bekor qilish | Бекор кардан |  |
| `report.done` | Xabaringiz yuborildi — rahmat. | Хабари шумо фиристода шуд — ташаккур. |  |
| `report.failed` | Yuborilmadi — qaytadan urinib ko'ring | Фиристода нашуд — боз кӯшиш кунед |  |
| `report.reason.statement` | Matnda xato | Хато дар шарт |  |
| `report.reason.tests` | Testlar noto'g'ri | Тестҳо нодурустанд |  |
| `report.reason.translation` | Tarjima xato | Хатои тарҷума |  |
| `report.reason.duplicate` | Takroriy masala | Масъалаи такрорӣ |  |
| `report.reason.other` | Boshqa | Дигар |  |
| `report.status.open` | Ochiq | Кушода |  |
| `report.status.accepted` | Qabul qilindi | Қабул шуд |  |
| `report.status.rejected` | Rad etildi | Рад шуд |  |
| `error.ground_unreadable` | Fon rangini o'qib bo'lmadi — accent qo'llanmadi. Sahifani yangilab ko'ring. | Ранги замина хонда нашуд — акцент татбиқ нашуд. Саҳифаро аз нав бор кунед. |  |
| `error.contrast_unreachable` | Bu tus bilan yetarli kontrast chiqmadi — boshqa tus tanlang. | Бо ин рангин контрасти кофӣ ба даст наомад — ранги дигар интихоб кунед. |  |
| `style.dashboard.label` | Dashboard | Dashboard |  |
| `style.dashboard.hint` | Hozirgi — yumshoq kartalar | Ҷорӣ — кортҳои мулоим |  |
| `style.swiss.label` | Shveycha | Швейтсарӣ |  |
| `style.swiss.hint` | Chiziq va tipografika | Хатҳо ва типографика |  |
| `style.flat.label` | Flat | Flat |  |
| `style.flat.hint` | Soyasiz, toza ranglar | Бе соя, рангҳои тоза |  |
| `style.material.label` | Material | Material |  |
| `style.material.hint` | Balandlik va soyalar | Баландӣ ва сояҳо |  |
| `style.editorial.label` | Editorial | Editorial |  |
| `style.editorial.hint` | Serif, jurnal ko'rinishi | Serif, намуди маҷалла |  |
| `style.brutal.label` | Neo-brutalizm | Нео-брутализм |  |
| `style.brutal.hint` | Qalin chegara, qattiq soya | Ҳудудҳои ғафс, сояҳои сахт |  |
| `style.terminal.label` | Terminal | Terminal |  |
| `style.terminal.hint` | Monospace, konsol | Моноширин, консол |  |
| `style.glass.label` | Glassmorphism | Glassmorphism |  |
| `style.glass.hint` | Shaffof, xiralashgan | Шаффоф, хира |  |
| `style.neu.label` | Neumorphism | Neumorphism |  |
| `style.neu.hint` | Yumshoq bo'rtma | Барҷастагии мулоим |  |
| `style.clay.label` | Claymorphism | Claymorphism |  |
| `style.clay.hint` | Gil, hajmli | Гил, ҳаҷмдор |  |
| `style.aurora.label` | Aurora | Aurora |  |
| `style.aurora.hint` | Gradient fon | Заминаи градиентӣ |  |
| `style.skeu.label` | Skeuomorfizm | Скевоморфизм |  |
| `style.skeu.hint` | Metall va relyef | Металл ва рельеф |  |
| `external.blog` | Blog | Блог |  |
| `admin.section.problems` | Masalalar | Масъалаҳо |  |
| `admin.section.reports` | Nuqson xabarlari | Хабарҳои нуқсон |  |
| `admin.section.contests` | Musobaqalar | Мусобиқаҳо |  |
| `admin.section.questions` | Savol banki | Бонки саволҳо |  |
| `admin.section.quizzes` | Testlar | Тестҳо |  |
| `admin.section.arena` | Arena | Арена |  |
| `admin.section.tournaments` | Chempionat | Мусобиқаҳо |  |
| `admin.section.hackathons` | Hakaton | Ҳакатонҳо |  |
| `admin.section.duels` | Duel | Дуэлҳо |  |
| `admin.section.articles` | Maqolalar | Мақолаҳо |  |
| `admin.section.roadmaps` | Traektoriya | Траектория |  |
| `admin.section.posts` | Yangiliklar | Хабарҳо |  |
| `admin.section.updates` | O'zgarishlar | Тағйиротҳо |  |
| `admin.section.platformRoadmap` | Yo'l xaritasi | Харитаи роҳ |  |
| `admin.section.roadmapComments` | Reja izohlari | Шарҳҳо ба харита |  |
| `admin.section.quests` | Questlar | Квестҳо |  |
| `admin.section.shop` | Do'kon | Дӯкон |  |
| `admin.section.users` | Foydalanuvchilar | Корбарандагон |  |
| `admin.section.analytics` | Analitika | Таҳлил |  |
| `admin.section.emailQuota` | Email kvota | Квотаи почта |  |
| `admin.quotaProvider` | Provayder | Хизматрасон |  |
| `admin.quotaSent` | Yuborildi | Фиристода шуд |  |
| `admin.quotaLimit` | Shift | Ҳудуд |  |
| `admin.quotaLeft` | Qoldi | Боқӣ монд |  |
| `admin.quotaState` | Holat | Ҳолат |  |
| `admin.quotaExhausted` | Kvota tugadi | Квота тамом шуд |  |
| `admin.quotaWarning` | Tugayapti ({percent}%) | Қариб тамом ({percent}%) |  |
| `admin.quotaInQueue` | Kvota tugadi — qolgani navbatda ({n} gacha, kechikish bilan) | Квота тамом шуд — боқимонда дар навбат (то {n}, бо таъхир) |  |
| `admin.quotaLost` | {n} xat yetkazilmaydi (navbat ham to'ldi) | {n} нома расонида намешавад (навбат низ пур шуд) |  |
| `admin.quotaUnset` | kvota belgilanmagan | квота муқаррар нашуд |  |
| `admin.quotaTodayLeft` | Bugun yana: | Имрӯз монд: |  |
| `admin.quotaWindowLabel` | Qaysi kun | Кадом рӯз |  |
| `admin.quotaWindowToday` | Bugun | Имрӯз |  |
| `admin.quotaWindowYesterday` | Kecha | Дирӯз |  |
| `admin.quotaWindowWeek` | 7 kun | 7 рӯз |  |
| `admin.quotaSpent` | Shu kun sarfi: | Дар он рӯз сарф шуд: |  |
| `admin.quotaWithQueue` | (navbat bilan birga {n} gacha) | (бо навбат то {n}) |  |
| `admin.quotaFailures` | {n} xat yuborilmadi | {n} нома фиристода нашуд |  |
| `admin.quotaUtcNote` | Kun chegarasi — UTC kalendar kuni (Resend va Brevo shunday belgilaydi). Navbatdagi xat yo'qolmaydi, lekin kechikadi. | Сарҳад — рӯзи тақвимии UTC (Resend ва Brevo ин тавр муайян мекунанд). Номаҳои дар навбат таъхир меёбанд, на гум мешаванд. |  |
| `admin.quotaLoadFail` | Kvota ma'lumotini yuklab bo'lmadi. | Маълумоти квотаро боргирӣ карда нашуд. |  |
| `pager.label` | Sahifalar | Саҳифабандӣ |  |
| `pager.entries` | yozuv | сабт |  |
| `pager.previous` | Oldingi | Пешина |  |
| `pager.next` | Keyingi | Баъдӣ |  |
| `problem.one` | masala | масъала |  |
| `admin.label.status.running` | Yurmoqda | Идома дорад |  |
| `admin.label.status.finished` | Tugagan | Анҷом ёфт |  |
| `admin.label.status.pending` | Kutilmoqda | Дар интизор |  |
| `admin.status.sent` | Yuborildi | Фиристода шуд |  |
| `admin.label.status.evaluating` | Baholanmoqda | Баҳо дода мешавад |  |
| `admin.label.status.completed` | Yakunlangan | Анҷомёфта |  |
| `admin.label.status.accepted` | Qabul qilindi | Қабул шуд |  |
| `admin.label.status.rejected` | Rad etilgan | Рад шуд |  |
| `admin.label.status.cancelled` | Bekor qilindi | Бекор шуд |  |
| `admin.label.status.done` | Tugadi | Тамом шуд |  |
| `admin.label.status.doneShort` | Bajarilgan | Иҷро шуд |  |
| `admin.label.status.inReview` | Ko'rib chiqilmoqda | Дар баррасӣ |  |
| `admin.label.status.planned` | Rejalashtirilgan | Банақшагирӣ шуда |  |
| `admin.label.status.inProgress` | Ishlanmoqda | Дар кор |  |
| `admin.label.status.shipped` | Chiqarildi | Бароварда шуд |  |
| `admin.label.status.enabled` | Yoqilgan | Фаъол |  |
| `admin.label.status.busy` | Band | Банд |  |
| `admin.label.date.start` | Boshlanish | Оғоз |  |
| `admin.label.date.startAt` | Boshlanish vaqti | Вақти оғоз |  |
| `admin.label.date.end` | Tugash | Анҷом |  |
| `admin.label.date.deadline` | Topshirish muddati | Мӯҳлати супоридан |  |
| `admin.label.date.publishedAt` | Nashr sanasi | Санаи нашр |  |
| `admin.label.date.releasedAt` | Chiqarilgan sana | Санаи барориш |  |
| `admin.label.date.joined` | Qo'shilgan | Ҳамроҳ шуд |  |
| `admin.label.duration.freezeMin` | Muzlatish (daqiqa) | Муздонӣ (дақиқа) |  |
| `admin.label.duration.secondsPerQuestion` | Savol uchun soniya | Сония барои савол |  |
| `admin.label.duration.readMin` | O'qish (daqiqa) | Хондан (дақиқа) |  |
| `admin.label.flag.public` | Ommaviy | Оммавӣ |  |
| `admin.label.flag.rated` | Reytingli | Рейтингӣ |  |
| `admin.label.flag.virtual` | Virtual | Виртуалӣ |  |
| `admin.label.flag.mirror` | Ko'zgu (asl musobaqa slug'i) | Оина (slug-и мусобиқаи аслӣ) |  |
| `admin.label.flag.repeatable` | Takroriy | Такроршаванда |  |
| `admin.label.flag.repeatPurchase` | Takroriy sotib olinadi | Такроран харида мешавад |  |
| `admin.label.flag.submissionsOpen` | Topshirish ochiq | Супоридан кушода |  |
| `admin.label.flag.resultsAnnounced` | Natijalar e'loni | Эълони натиҷаҳо |  |
| `admin.label.flag.active` | Faol | Фаъол |  |
| `admin.label.flag.activeHint` | Faol (bloklash uchun olib tashlang) | Фаъол (барои бастан гирифтан халонед) |  |
| `admin.label.flag.notifyUsers` | Foydalanuvchilarga xabar berish | Ба корбарон хабар додан |  |
| `admin.label.calc.rating` | Hisoblash | Ҳисоб |  |
| `admin.label.value.freeze` | Hisob | Ҳисоб |  |
| `admin.label.value.rewardQvant` | Mukofot (Qvant) | Мукофот (Qvant) |  |
| `admin.label.value.priceQvant` | Narx (Qvant) | Нарх (Qvant) |  |
| `admin.label.value.analysisPriceQvant` | Tahlilni ochish narxi, Qvant | Нархи кушодани таҳлил, Qvant |  |
| `admin.label.value.difficulty` | Qiyinlik | Мураккабӣ |  |
| `admin.label.value.difficultyRange` | Qiyinlik (800–3500, qadam 100) | Мураккабӣ (800–3500, қадам 100) |  |
| `admin.label.value.scoring` | Skoring (0–100) | Скоринг (0–100) |  |
| `admin.label.value.timeLimit` | Vaqt limiti, ms | Маҳдудияти вақт, мс |  |
| `admin.label.value.memoryLimit` | Xotira limiti, KB | Маҳдудияти хотира, КБ |  |
| `admin.label.text.title` | Sarlavha | Сарлавҳа |  |
| `admin.label.text.summary` | Qisqacha | Мухтасар |  |
| `admin.label.text.markdown` | Matn (Markdown) | Матн (Markdown) |  |
| `admin.label.text.markdownLatex` | Matn (Markdown + LaTeX) | Матн (Markdown + LaTeX) |  |
| `admin.label.text.descriptionMarkdown` | Tavsif (Markdown) | Тавсиф (Markdown) |  |
| `admin.label.text.statementLatex` | Shart (Markdown + LaTeX) | Шарт (Markdown + LaTeX) |  |
| `admin.label.text.articleExample` | Maqoladagi misol | Мисол дар мақола |  |
| `admin.label.text.editorNote` | Muharrir maqolasi | Ёддошти муҳаррир |  |
| `admin.label.text.editorial` | Yechim tahlili | Таҳлил |  |
| `admin.label.text.solutionExplanation` | Yechim tushuntirishi | Шарҳи ҳал |  |
| `admin.label.text.problemExample` | Algoritm | Алгоритм |  |
| `admin.label.text.problemTraining` | Mashq uchun | Барои машқ |  |
| `admin.label.tech.input` | Kiruvchi ma'lumot | Маълумоти вуруд |  |
| `admin.label.tech.output` | Chiquvchi ma'lumot | Маълумоти хуруҷ |  |
| `admin.label.tech.topicsSlug` | Mavzular (slug, vergul bilan) | Мавзӯъҳо (slug, бо вергул) |  |
| `admin.label.tech.parentTopic` | Ota mavzu (slug) | Мавзӯи волид (slug) |  |
| `admin.label.tech.parent` | Ota | Волид |  |
| `admin.label.tech.sourceUrl` | Manba URL | URL-и манба |  |
| `admin.label.tech.sourceLinks` | Manba havolalari | Пайвандҳои манба |  |
| `admin.label.tech.githubUrl` | GitHub havolasi | Пайванди GitHub |  |
| `admin.label.tech.imageUrl` | Rasm havolasi | Пайванди тасвир |  |
| `admin.label.tech.changelogId` | Changelog yozuvi ID | ID-и сабти changelog |  |
| `admin.label.tech.checkerLanguage` | Checker tili (kod, masalan cpp23) | Забони checker (код, мис. cpp23) |  |
| `admin.label.tech.checkerSource` | Checker manbasi | Манбаи checker |  |
| `admin.label.tech.interactorLanguage` | Interactor tili (kod, masalan cpp23) | Забони interactor (код, мис. cpp23) |  |
| `admin.label.tech.interactorSource` | Interactor manbasi | Манбаи interactor |  |
| `admin.label.name.uz` | Nomi (uz) | Ном (uz) |  |
| `admin.label.name.ru` | Nomi (ru) | Ном (ru) |  |
| `admin.label.name.en` | Nomi (en) | Ном (en) |  |
| `admin.label.name.translation` | Tarjima | Тарҷума |  |
| `admin.label.name.language` | Matn tili (uz/ru/en) | Забони шарт (uz/ru/en) |  |
| `admin.label.name.shown` | Ko'rsatiladigan ism | Номи намоишшаванда |  |
| `admin.label.ab.control` | Nazorat (2-qadamda) | Назорат (дар қадами 2) |  |
| `admin.label.ab.variant` | Variant (ro'yxatda) | Вариант (дар рӯйхат) |  |
| `admin.label.misc.participant` | Ishtirokchi | Иштирокчӣ |  |
| `admin.label.misc.challenger` | Chaqiruvchi | Даъваткунанда |  |
| `admin.label.misc.projects` | Loyihalar | Лоиҳаҳо |  |
| `admin.label.misc.news` | Yangilik | Хабар |  |
| `admin.label.misc.announcement` | E'lon | Эълон |  |
| `admin.label.text.slug` | Slug | Слаг |  |
| `admin.label.text.status` | Holat | Ҳолат |  |
| `admin.label.text.name` | Nomi | Ном |  |
| `admin.label.text.kind` | Turi | Навъ |  |
| `admin.label.text.language` | Til | Забон |  |
| `admin.label.flag.published` | Nashr qilingan | Нашр шудааст |  |
| `admin.label.text.description` | Tavsif | Тавсиф |  |
| `admin.label.text.comment` | Izoh | Шарҳ |  |
| `admin.label.text.code` | Kod | Код |  |
| `admin.label.flag.open` | Ochiq | Кушод |  |
| `admin.label.text.deadline` | Muddat | Муҳлат |  |
| `admin.label.text.date` | Sana | Сана |  |
| `admin.label.misc.questions` | Savollar | Саволҳо |  |
| `admin.label.misc.topics` | Mavzular | Мавзӯъҳо |  |
| `admin.label.misc.problems` | Masalalar | Масъалаҳо |  |
| `admin.label.text.author` | Muallif | Муаллиф |  |
| `admin.label.text.flag` | Flag | Парчам |  |
| `admin.label.text.type` | Tur | Навъ |  |
| `admin.label.text.category` | Kategoriya | Гурӯҳ |  |
| `admin.label.text.module` | Modul | Модул |  |
| `admin.label.flag.staff` | Xodim | Корманд |  |
| `admin.label.text.article` | Maqola | Мақола |  |
| `admin.label.text.opponent` | Raqib | Рақиб |  |
| `admin.label.text.result` | Natija | Натиҷа |  |
| `admin.label.text.end` | Yakun | Анҷом |  |
| `admin.label.misc.votes` | Ovoz | Овозҳо |  |
| `admin.label.text.message` | Xabar | Паём |  |
| `admin.label.text.checker` | Checker | Чекер |  |
| `admin.label.text.standard` | Standart | Стандартӣ |  |
| `admin.label.text.special` | Maxsus | Махсус |  |
| `admin.label.text.interactive` | Interactive | Интерактивӣ |  |
| `admin.label.text.source` | Manba | Сарчашма |  |
| `admin.label.misc.tests` | Testlar | Тестҳо |  |
| `admin.label.text.reward` | Mukofot | Мукофот |  |
| `admin.label.text.qvant` | Qvant | Квант |  |
| `admin.label.text.problem` | Masala | Масъала |  |
| `admin.label.text.reason` | Sabab | Сабаб |  |
| `admin.label.text.who` | Kim | Кӣ |  |
| `admin.label.text.order` | Tartib | Тартиб |  |
| `admin.label.misc.steps` | Qadamlar | Қадамҳо |  |
| `admin.label.text.price` | Narx | Нарх |  |
| `admin.label.misc.owners` | Egalari | Соҳибон |  |
| `admin.label.text.asset` | Asset | Ассет |  |
| `admin.label.misc.stages` | Bosqichlar | Марҳилаҳо |  |
| `admin.label.text.version` | Versiya | Нусха |  |
| `admin.label.text.repo` | Repo | Репозиторий |  |
| `admin.label.text.username` | Login | Номи корбар |  |
| `admin.label.text.displayName` | Ism | Ном |  |
| `admin.label.text.email` | Email | Почта |  |
| `admin.label.misc.ratings` | Reytinglar | Рейтингҳо |  |
| `admin.label.text.bio` | Bio | Дар бораи худ |  |
| `admin.label.duration.perQuestion` | s/savol | с/савол |  |
| `admin.label.text.num` | # | # |  |
| `admin.label.text.acmIcpc` | ACM/ICPC | ACM/ICPC |  |
| `admin.label.text.ioi` | IOI | IOI |  |
| `admin.label.lang.uz` | uz | uz |  |
| `admin.label.lang.ru` | ru | ru |  |
| `admin.label.lang.en` | en | en |  |
| `admin.help.topicsSlug` | Topic sluglari, vergul bilan | Слаги мавзӯъҳо, бо вергул |  |
| `admin.help.freezeStandings` | Oxirgi N daqiqada standings yangilanmaydi | Дар N дақиқаи охир ҷадвал навсозӣ намешавад |  |
| `admin.help.submissionClose` | Shu vaqtdan keyin topshirish yopiladi va loyihalar hammaga ochiladi | Баъди ин вақт супоридан баста мешавад ва лоиҳаҳо ба ҳама кушода мешаванд |  |
| `admin.help.rulesAndPrizes` | Shartlar, mezonlar, sovrin | Шартҳо, меъёрҳо, мукофотҳо |  |
| `admin.help.targetQuarter` | Chorak darajasida (2026-Q4). ANIQ SANA YOZILMAYDI — bajarilmasa ishonch buziladi | Дар сатҳи чоряк (2026-Q4). САНАИ АНИҚ НАВИШТА НАМЕШАВАД — иҷро нашавад, эътимод мешиканад |  |
| `admin.help.changelogId` | Chiqarilganda bog'lanadigan yozuv raqami. Batafsil sahifada havola bo'ladi | Рақами сабти тағйирот барои пайваст. Дар саҳифаи муфассал ҳавола мешавад |  |
| `admin.help.softDelete` | O'chirilsa band ko'rinmaydi, lekin ovozlari bilan bazada qoladi | Нест кардан бандро пинҳон мекунад, лекин бо овозҳояш дар база мемонад |  |
| `admin.help.autoPublishAt` | Bo'sh qolsa — birinchi nashrda avtomatik qo'yiladi | Холӣ монад — ҳангоми нашри аввал худкор гузошта мешавад |  |
| `admin.help.notifyOnce` | Nashrdan keyin barcha foydalanuvchiga bir marta bildirishnoma yuboriladi | Баъди нашр ба ҳамаи корбарон як бор огоҳинома меравад |  |
| `admin.help.inputFormatSection` | Sahifada alohida bo'lim bo'lib chiqadi | Дар саҳифа ҳамчун бахши алоҳида бармеояд |  |
| `admin.help.noteExplainsSamples` | Namunalar nega shunday ekanini tushuntiradi | Шарҳ медиҳад, ки чаро намунаҳо чунинанд |  |
| `admin.help.editorialFreeForSolvers` | Masalani yechgan bepul ko'radi (ADR-0013) | Барои ҳалкунандагон ройгон (ADR-0013) |  |
| `admin.help.editorialPrice` | Yechmaganlar uchun. 0 — hammaga bepul | Барои ҳал накардаҳо. 0 — барои ҳама ройгон |  |
| `admin.help.interactorOnlyInteractive` | Faqat Interactive uchun. Bo'sh = yo'q | Танҳо барои Interactive. Холӣ = нест |  |
| `admin.help.checkerRequired` | Maxsus va Skoring uchun. Bo'sh bo'lsa har yuborish IE bo'ladi | Барои «Махсус» ва «Скоринг». Холӣ бошад, ҳар супориш IE мегирад |  |
| `admin.help.testlibInvocation` | testlib chaqiruvi: checker <input> <output> <answer> | Даъвати testlib: checker <input> <output> <answer> |  |
| `admin.help.parentEmptyRoot` | Bo'sh = ildiz | Холӣ = реша |  |
| `admin.help.questCodeMatch` | Hodisaga bog'lanish uchun qvant/quests.py dagi kod bilan mos bo'lishi kerak | Барои пайваст кардани ҳодиса бояд ба коди qvant/quests.py мувофиқ бошад |  |
| `admin.help.cosmeticOnly` | ADR-0002: v1 da faqat kosmetika va qulaylik | ADR-0002: дар v1 танҳо косметика ва қулайӣ |  |
| `admin.help.assetRef` | Ramka/cover fayliga havola yoki kalit | Ҳавола ба файли чаҳорчӯба/муқова ё калиди он |  |
| `admin.help.repeatPerItem` | Streak freeze — ha, ramka — yo'q | Streak freeze — ҳа, чаҳорчӯба — не |  |
| `admin.help.publishedAtAuto` | «Nashrda» qilib qo'yilsa `published_at` avtomatik yoziladi | Агар «Нашр шудааст» гузоред, `published_at` худкор навишта мешавад |  |
| `admin.help.releasedAtReal` | O'zgarishning HAQIQIY sanasi — yozuv kechroq yozilishi mumkin | САНАИ АСЛИИ тағйирот — сабт дертар навишта шуда метавонад |  |
| `admin.help.versionOptional` | Ixtiyoriy, v1.4.0 | Ҳатмӣ нест, v1.4.0 |  |
| `admin.help.refsFormat` | Commit SHA, PR raqami, release tegi — vergul bilan | Commit SHA, рақами PR, теги release — бо вергул |  |
| `admin.help.screenshotWhenNeeded` | Faqat kerak bo'lganda — dizayn o'zgarishlari uchun skrinshot | Танҳо ҳангоми зарурат — скриншот барои тағйироти дизайн |  |
| `admin.help.staffOnlySuperuser` | Faqat superuser o'zgartira oladi. O'z hisobingizni o'zgartira olmaysiz. | Танҳо суперкорбар тағйир дода метавонад. Ҳисоби худро тағйир дода наметавонед. |  |
| `admin.help.languageCodes` | uz / ru / en | uz / ru / en |  |
| `admin.help.zeroAuto` | 0 = avtomatik | 0 = худкор |  |
| `admin.help.upTo300Chars` | 300 belgigacha | То 300 аломат |  |
| `admin.help.twoLetterDefaultUz` | 2 harf, standart: uz | 2 ҳарф, пешфарз: uz |  |
| `admin.help.ownerRepo` | owner/repo | соҳиб/репозиторий |  |
| `admin.text.eventFormStarted` | Forma boshlandi | Форма оғоз шуд |  |
| `admin.text.eventRegisterDone` | Ro'yxatdan o'tdi | Сабтином шуд |  |
| `admin.text.eventSessions` | {name}: {sessions} sessiya, {share}% | {name}: {sessions} сессия, {share}% |  |
| `admin.text.funnelDay` | {date}: {started} boshlandi, {done} tugadi | {date}: {started} оғоз карданд, {done} анҷом доданд |  |
| `admin.text.reasonLoginTaken` | Login band | Номи корбар банд аст |  |
| `admin.text.reasonPasswordMismatch` | Parollar mos emas | Рамзҳо мувофиқ нестанд |  |
| `admin.text.reasonTermsNotAccepted` | Shartlarga rozilik berilmagan | Шартҳо қабул нашудаанд |  |
| `admin.text.reasonEmailTaken` | Email band yoki noto'g'ri | Почта банд ё нодуруст |  |
| `admin.text.reasonServerError` | Server xatosi | Хатои сервер |  |
| `admin.text.reasonNetworkError` | Tarmoq xatosi | Хатои шабака |  |
| `admin.text.reasonUnknown` | Sababsiz | Бесабаб |  |
| `admin.text.reportReasonStatement` | Matnda xato | Хато дар матн |  |
| `admin.text.reportReasonTests` | Testlar noto'g'ri | Тестҳо нодурустанд |  |
| `admin.text.reportReasonTranslation` | Tarjima xato | Хатои тарҷума |  |
| `admin.text.reportReasonDuplicate` | Takroriy masala | Масъалаи такрорӣ |  |
| `admin.text.reportReasonOther` | Boshqa | Дигар |  |
| `admin.label.status.draft` | Qoralama | Лоиҳа |  |
| `admin.label.status.published` | Nashrda | Нашр шудааст |  |
| `admin.label.status.withdrawn` | Nashrdan olingan | Аз нашр гирифта шуд |  |
| `admin.label.status.rejectedShort` | Rad etildi | Рад шуд |  |
| `admin.text.error` | Xato | Хато |  |
| `admin.text.unpublish` | Nashrdan olish | Аз нашр гирифтан |  |
| `admin.text.publishVerb` | Nashr qilish | Нашр кардан |  |
| `admin.label.misc.questDaily` | Kunlik | Ҳаррӯза |  |
| `admin.label.misc.questWeekly` | Haftalik | Ҳафтаина |  |
| `admin.label.misc.questAchievement` | Yutuq | Дастовард |  |
| `admin.label.shopCategory.streakFreeze` | Streak freeze | Яхкунии силсила |  |
| `admin.label.shopCategory.avatarFrame` | Avatar ramka | Чаҳорчӯбаи аватар |  |
| `admin.label.shopCategory.profileCover` | Profil cover | Муқоваи профил |  |
| `admin.label.shopCategory.usernameBadge` | Username badge | Нишони ном |  |
| `admin.title.order` | Tartib | Тартиб |  |
| `admin.title.signupFunnel` | Ro'yxatdan o'tish voronkasi | Қифи сабтином |  |
| `admin.title.abRegion` | A/B: viloyat qachon so'raladi | A/B: вилоят кай вақт пурсида мешавад |  |
| `admin.title.total` | Jami | Ҳамагӣ |  |
| `admin.title.errorReasons` | Xato sabablari | Сабабҳои хатогӣ |  |
| `admin.title.languages` | Tillar | Забонҳо |  |
| `admin.title.countries` | Mamlakatlar | Кишварҳо |  |
| `admin.title.daily` | Kunlik | Ҳаррӯза |  |
| `admin.title.points` | Ball | Холҳо |  |
| `admin.title.duels` | Duellar | Дуэлҳо |  |
| `admin.title.hackathons` | Hakatonlar | Ҳакатонҳо |  |
| `admin.title.topics` | Mavzular | Мавзӯъҳо |  |
| `admin.title.moveUp` | Yuqoriga | Боло |  |
| `admin.title.moveDown` | Pastga | Поён |  |
| `admin.title.remove` | Olib tashlash | Хориҷ кардан |  |
| `admin.title.roadmapComments` | Yo'l xaritasi izohlari | Шарҳҳои нақшаи роҳ |  |
| `admin.title.tournaments` | Chempionatlar | Чемпионатҳо |  |
| `admin.title.broadcast` | Umumiy e'lon | Эълони умумӣ |  |
| `admin.title.page` | Admin | Мудир |  |
| `admin.placeholder.questionId` | Savol ID | ID-и савол |  |
| `admin.placeholder.problemSlug` | masala slug'i | слаги масъала |  |
| `admin.placeholder.title` | Sarlavha | Сарлавҳа |  |
| `admin.placeholder.comment` | Fikr | Фикр |  |
| `admin.placeholder.articleSlug` | maqola slugi | слаги мақола |  |
| `admin.placeholder.amount` | ±miqdor | ±миқдор |  |
| `admin.placeholder.ledgerComment` | Izoh (ledgerga yoziladi) | Шарҳ (ба журнал навишта мешавад) |  |
| `admin.placeholder.text` | Matn | Матн |  |
| `admin.placeholder.textOptional` | Matn (ixtiyoriy) | Матн (ҳатмӣ нест) |  |
| `admin.text.badgeActive` | faol | фаъол |  |
| `admin.text.badgeBlocked` | bloklangan | баста шудааст |  |
| `admin.text.badgeSuperuser` | superuser | суперкорбар |  |
| `admin.text.badgeStaff` | xodim | корманд |  |
| `admin.text.badgeHidden` | yashirin | пинҳон |  |
| `admin.text.badgeRewarded` | mukofotlangan | мукофот гирифта |  |
| `admin.text.badgeLive` | jonli | зинда |  |
| `admin.text.badgeFinished` | tugagan | анҷом ёфтааст |  |
| `admin.text.badgeRated` | reytingli | рейтингӣ |  |
| `admin.text.badgeClosed` | yopiq | пӯшида |  |
| `admin.text.badgeCompleted` | yakunlangan | анҷомёфта |  |
| `admin.text.badgeRepo` | repo | репозиторий |  |
| `admin.text.badgeDemo` | demo | демо |  |
| `admin.text.badgeSample` | namuna | намуна |  |
| `admin.text.badgeOptional` | ixtiyoriy | ҳатмӣ нест |  |
| `admin.text.addProblem` | + Masala | + Масъала |  |
| `admin.text.addVariant` | + Variant | + Вариант |  |
| `admin.text.addStep` | + Qadam | + Қадам |  |
| `admin.text.addStage` | + Bosqich | + Марҳила |  |
| `admin.text.reschedule` | Qayta rejalashtirish | Аз навбат ба нақша гирифтан |  |
| `admin.text.rebuildStandings` | Standings qayta qurish | Ҷадвалро аз нав сохтан |  |
| `admin.text.recalcTable` | Jadvalni qayta hisoblash | Ҷадвалро аз нав ҳисоб кардан |  |
| `admin.text.restoreCatalog` | Katalogni tiklash | Барқарор кардани феҳрист |  |
| `admin.text.sendToAll` | Hammaga yuborish | Ба ҳама фиристодан |  |
| `admin.text.cancel` | Bekor qilish | Бекор кардан |  |
| `admin.text.loading` | yuklanmoqda… | боргирӣ… |  |
| `admin.text.orderNumber` | Tartib raqami * | Рақами тартиб * |  |
| `admin.text.contestSlug` | Contest slug | Слаги озмун |  |
| `admin.text.noErrors` | Xato qayd etilmagan. | Хато сабт нашудааст. |  |
| `admin.text.highSkipRate` | Bu raqam yuqori bo'lsa, 2-qadam odamni charchatyapti. | Агар ин рақам баланд бошад, қадами 2 одамонро хаста мекунад. |  |
| `admin.text.dailyLegend` | Kulrang — boshlangan, rangli — tugagan. Har ustun bir kun. | Хокистарӣ — оғоз карданд, рангин — анҷом доданд. Ҳар сутун — як рӯз. |  |
| `admin.text.publish` | Nashr | Нашр |  |
| `admin.text.finish` | Yakunlash | Анҷом додан |  |
| `admin.text.rollback` | Qaytarish | Баргардондан |  |
| `admin.text.hidden` | Yashirilgan | Пинҳон |  |
| `admin.text.deleteRollback` | O'chirish (rollback) | Нест кардан (баргардондан) |  |
| `admin.text.ratingsAppliedAt` | Yakunlangan: {date} | Анҷом ёфт: {date} |  |
| `admin.text.draw` | Durang ({score}) | Мусовӣ ({score}) |  |
| `admin.text.add` | Qo'shish | Илова кардан |  |
| `admin.text.apply` | Qo'llash | Татбиқ кардан |  |
| `admin.text.linkedProblems` | Bog'langan masalalar | Масъалаҳои алоқаманд |  |
| `admin.text.questionsInOrder` | Savollar (tartib bo'yicha) | Саволҳо (бо тартиб) |  |
| `admin.text.mirrorOf` | ko'zgu: {slug} | оина: {slug} |  |
| `admin.text.variant` | Variant {order} | Вариант {order} |  |
| `admin.text.noStages` | Bosqichlar yo'q — contest qo'shing. | Марҳилаҳо нест — озмун илова кунед. |  |
| `admin.text.forceFinish` | Majburan yakunlash | Маҷбуран анҷом додан |  |
| `admin.text.no` | yo'q | не |  |
| `admin.text.disabled` | O'chirilgan | Хомӯш |  |
| `admin.text.off` | O'chiq | Хомӯш |  |
| `admin.text.enable` | Yoqish | Фаъол кардан |  |
| `admin.text.hide` | Yashirish | Пинҳон кардан |  |
| `admin.text.visible` | Ko'rinadi | Намоён аст |  |
| `admin.text.tableRecalculated` | Jadval qayta hisoblandi — ishtirokchilar: {count} | Ҷадвал аз нав ҳисоб шуд — иштирокчиён: {count} |  |
| `admin.text.yes` | ha | ҳа |  |
| `admin.text.badgePublic` | ommaviy | оммавӣ |  |
| `archive.continue` | Davom ettirish | Идома |  |
| `archive.upcoming` | Yaqin musobaqa | Озмуни наздик |  |
| `archive.roadmaps` | O'quv rejalari | Масирҳои омӯзишӣ |  |
| `archive.community` | Hamjamiyat | Ҷомеа |  |
| `archive.topicStrength` | Mavzu bo'yicha kuch | Қувват аз рӯи мавзӯъ |  |
| `archive.recentAttempts` | Oxirgi urinishlar | Кӯшишҳои охирин |  |
| `contest.notFound` | Musobaqa topilmadi | Озмун ёфт нашуд |  |
| `contest.problems` | Masalalar | Масъалаҳо |  |
| `learn.notFound` | Maqola topilmadi | Мақола ёфт нашуд |  |
| `problem.notFound` | Masala topilmadi | Масъала ёфт нашуд |  |
| `problem.comments` | Izoh | Шарҳ |  |
| `problem.stats.title` | Statistika · {slug} | Омор · {slug} |  |
| `problem.stats.languages` | Tillar | Забонҳо |  |
| `problem.stats.fastest` | Eng tez yechimlar | Суръаттарин ҳалҳо |  |
| `problem.status.title` | Urinishlar · {slug} | Кӯшишҳо · {slug} |  |
| `problem.editorialAvailable` | Yechim tahlili bor | Таҳлил дорад |  |
| `problem.testsNotReady` | Testlar tayyorlanmagan — yechim qabul qilinmaydi | Тестҳо омода нестанд — ҳалҳо қабул намешаванд |  |
| `qvant.marathon` | Haftalik marafon | Марафони ҳафтаина |  |
| `submit.solution` | Yechim | Ҳал |  |
| `contest.ogAlt` | RankWant musobaqasi | Озмуни RankWant |  |
| `problem.ogAlt` | RankWant masalasi | Масъалаи RankWant |  |
| `contest.running` | Davom etmoqda | Идома дорад |  |
| `contest.notStarted` | Boshlanmagan | Оғоз нашудааст |  |
| `problem.solvedCount` | {count} yechilgan | {count} ҳал карданд |  |
| `qvant.marathonFinished` | Yakunlandi | Анҷом ёфт |  |
| `learn.description` | O'zbek tilida sport dasturlash bo'yicha maqolalar va yo'l xaritalari — har bir mavzu mashq masalalari bilan. | Мақолаҳо ва нақшаи роҳ оид ба барномасозии варзишӣ ба забони тоҷикӣ — ҳар мавзӯъ бо масъалаҳои машқ. |  |
| `rating.description` | RankWant reytinglarining to'liq formulalari: Skills, Contests, Activity, Challenges. | Формулаҳои пурраи рейтингҳои RankWant: Skills, Contests, Activity, Challenges. |  |
| `submit.testsNotReadyBody` | Bu masalaning testlari hali tayyorlanmagan, shu sababli yechim qabul qilinmaydi. Matnni o'qib, o'zingiz uchun yechib ko'rishingiz mumkin — testlar qo'shilishi bilan yuborish ochiladi. | Тестҳои ин масъала ҳанӯз омода нестанд, бинобар ин ҳалҳо қабул намешаванд. Шартро хонед ва худатон ҳал кунед — бо илова шудани тестҳо супоридан кушода мешавад. |  |
| `submit.signInToSubmit` | Yuborish uchun kiring | Барои супоридан ворид шавед |  |
| `submit.testOnSamples` | Namunada sinash | Санҷиш дар намунаҳо |  |
| `submit.draftSavedLocally` | Qoralama shu brauzerda saqlanadi | Лоиҳа дар ҳамин браузер нигоҳ дошта мешавад |  |
| `submit.loadFromFile` | Fayldan yuklash | Аз файл бор кардан |  |
| `submit.nothingSubmitted` | Hali yuborilmadi. Kod yozing va «Yuborish» ni bosing. | Ҳанӯз чизе супорида нашудааст. Код нависед ва «Супоридан»-ро пахш кунед. |  |
| `submit.testTooltip` | {index}: {verdict} · {time} ms | {index}: {verdict} · {time} мс |  |
| `submit.addTest` | Test qo'shish | Илова кардани тест |  |
| `submit.removeTest` | Test {index} ni o'chirish | Нест кардани тести {index} |  |
| `submit.run` | Ishga tushirish | Иҷро кардан |  |
| `submit.testsSavedLocally` | Testlar shu brauzerda saqlanadi | Тестҳо дар ҳамин браузер нигоҳ дошта мешаванд |  |
| `submit.runningSamples` | Namunalar yuritilmoqda… | Намунаҳо иҷро мешаванд… |  |
| `submit.samplesHint` | «Namunada sinash» — kodni yuborishdan oldin namunalarda tekshiradi. | «Санҷиш дар намунаҳо» — кодро пеш аз супоридан дар намунаҳо месанҷад. |  |
| `submit.matches` | mos | мувофиқ |  |
| `submit.outputMismatch` | chiqish mos emas | хуруҷ мувофиқ нест |  |
| `submit.running` | yuritilmoqda… | иҷро мешавад… |  |
| `submit.allSamplesPass` | Barcha namunalar mos — yuborishingiz mumkin | Ҳамаи намунаҳо мувофиқ — метавонед супорид |  |
| `submit.yourOutput` | Sizning chiqishingiz | Хуруҷи шумо |  |
| `submit.sample` | Namuna {order} · | Намунаи {order} · |  |
| `submit.expected` | Kutilgan | Интизор |  |
| `admin.text.noEventsInWindow` | Bu oynada hodisa yo'q. Funnel ro'yxatdan o'tish va kirish sahifalarida yig'iladi — trafik bo'lsa paydo bo'ladi. | Дар ин тиреза ҳодиса нест. Қиф дар саҳифаҳои сабтином ва воридшавӣ ҷамъ мешавад — бо пайдо шудани трафик пайдо мешавад. |  |
| `admin.text.funnelNote` | Foizlar birinchi qadamga nisbatan. Sessiya bo'yicha sanaladi — bir odam bir marta hisoblanadi. | Фоизҳо нисбат ба қадами аввал. Аз рӯи сессия ҳисоб мешавад — як шахс як бор ҳисоб меёбад. |  |
| `admin.text.noSignupYet` | Hali tugagan ro'yxatdan o'tish yo'q. Guruh cookie'da saqlanadi va har bir hodisa bilan birga yuboriladi. | Ҳанӯз сабтиноми анҷомёфта нест. Гурӯҳ дар cookie нигоҳ дошта мешавад ва бо ҳар ҳодиса фиристода мешавад. |  |
| `admin.text.skipped` | o'tkazib yubordi | гузаштанд |  |
| `admin.text.noData` | Ma'lumot yo'q. | Маълумот нест. |  |
| `admin.text.noDataCountries` | Ma'lumot yo'q — mamlakat ro'yxatdan o'tgandan keyin ma'lum bo'ladi. | Маълумот нест — кишвар баъди сабтином маълум мешавад. |  |
| `admin.help.testsStoredRemotely` | Judge testlarni DB dan emas, S3 dan o'qiydi: matn yuklanganda tests/{slug}/<order>.in/.out sifatida saqlanadi, bu yerda faqat havola ko'rinadi. Bir xil tartib raqami qayta yuklansa — ustiga yoziladi. | Довар тестҳоро аз S3 мехонад, на аз пойгоҳи дода: матни боршуда ҳамчун tests/{slug}/<order>.in/.out нигоҳ дошта мешавад, дар ин ҷо танҳо ҳавола дида мешавад. Ҳамон рақам боз бор шуда, рӯйи он навишта мешавад. |  |
| `admin.text.noTestsYet` | Hali test yo'q — yechimlar tekshirilmaydi. | Ҳанӯз тест нест — ҳалҳо санҷида намешаванд. |  |
| `admin.text.addTest` | Test qo'shish | Илова кардани тест |  |
| `archive.mostViewed` | Ko'p ko'rilgan | Пурбинанда |  |
| `rating.intro` | Barcha formulalar ochiq. Yashirin og'irlik yoki e'lon qilinmagan bonus yo'q. Har bir o'zgarish sababi bilan profilingizda yozib boriladi. | Ҳамаи формулаҳо кушодаанд. Вазни пинҳонӣ ва бонуси эълоннашуда вуҷуд надорад. Ҳар як тағйирот бо сабабаш дар профили шумо сабт мешавад. |  |
| `rating.skills.summary` | Birinchi marta yechgan masalalaringiz ball bo'yicha kamayish tartibida saralanadi va kamayuvchi koeffitsient bilan qo'shiladi. Ball — masalaning joriy qiyinligi. | Масъалаҳое, ки бори аввал ҳал кардаед, аз рӯи хол ба тартиби камшаванда ҷобаҷо шуда, бо коэффициенти камшаванда ҷамъ мешаванд. Хол — мураккабии ҷории масъала. |  |
| `rating.skills.noDecrease` | Yangi masala yechish reytingni hech qachon kamaytirmaydi. | Ҳалли масъалаи нав рейтинги шуморо ҳеҷ гоҳ паст намекунад. |  |
| `rating.skills.cap` | Natija eng qiyin masalangizdan 20 baravardan oshmaydi. | Натиҷа аз 20 баробари мураккабтарин масъалаи шумо зиёд намешавад. |  |
| `rating.skills.saturation` | Bir xil qiyinlikda ~45 masaladan keyin to'yinadi — undan keyin faqat qiyinroq masala o'stiradi. | Дар мураккабии якхела тақрибан баъди 45 масъала сермешавад — баъд аз он танҳо масъалаи мураккабтар онро баланд мебардорад. |  |
| `rating.skills.revaluation` | Masala qayta baholansa reyting o'zgarishi mumkin. Bu foydalanuvchi harakati emas, platforma qarori — sizga xabar beriladi va sabab tarixda yoziladi. | Агар масъала аз нав баҳо дода шавад, рейтинг тағйир ёфта метавонад. Ин қарори платформа аст, на амали корбар — ба шумо хабар дода мешавад ва сабаб ба таърих навишта мешавад. |  |
| `rating.skills.example` | Misol: 500 ta 800-ball = 16 000 · 20 ta 2500-ball = 32 076. Ya'ni chuqurlik miqdordan ustun. | Мисол: 500 масъала аз 800 хол = 16 000 · 20 масъала аз 2 500 хол = 32 076. Яъне амиқӣ аз шумора бартарӣ дорад. |  |
| `rating.contests.summary` | Codeforces uslubidagi Elo. Faqat reytingli va kamida 10 ishtirokchili musobaqalar hisoblanadi. | Elo ба услуби Codeforces. Танҳо мусобиқаҳои рейтингӣ бо иштирокчиёни на камтар аз 10 ҳисоб мешаванд. |  |
| `rating.contests.start` | Boshlang'ich reyting — 1400. | Рейтинги ибтидоӣ — 1400. |  |
| `rating.contests.provisional` | Birinchi 6 reytingli musobaqada o'zgarish 1.5 baravar tezroq. | Дар 6 мусобиқаи аввалини рейтингӣ тағйирот 1,5 баробар тезтар аст. |  |
| `rating.contests.floor` | Reyting 0 dan pastga tushmaydi. | Рейтинг аз 0 паст намеравад. |  |
| `rating.activity.window` | Oxirgi 30 kunlik siljuvchi oyna. | Тирезаи ҳаракаткунандаи 30 рӯзи охир. |  |
| `rating.activity.qvant` | Qvant balansi ataylab hisobga olinmaydi: aks holda do'konda xarid qilish reytingni tushirardi. | Баланси Qvant қасдан ба назар гирифта намешавад: вагарна хариди мағоза рейтингро паст мекард. |  |
| `rating.challenges.summary` | 1v1 duel uchun klassik Elo. | Elo-и классикӣ барои дуэлҳои 1v1. |  |
| `rating.adr` | Formulani o'zgartirish alohida qaror (ADR) talab qiladi va barcha reytinglar qayta hisoblanishidan oldin e'lon qilinadi. | Тағйири формула қарори алоҳида (ADR) талаб мекунад ва пеш аз аз нав ҳисоб кардани ҳамаи рейтингҳо эълон мешавад. |  |
| `rating.phase.active` | Faol | Фаъол |  |
| `rating.phase.phase3` | 3-bosqich | Марҳилаи 3 |  |
| `problem.difficultyDescription` | {title} — qiyinlik {difficulty}. RankWant masala arxivi. | {title} — мураккабӣ {difficulty}. Бойгонии масъалаҳои RankWant. |  |
| `problem.partialScoring` | Qisman ball | Холи қисмӣ |  |
| `problem.testsPreparing` | Testlar tayyorlanmoqda | Тестҳо омода карда мешаванд |  |
| `problem.backToContest` | Musobaqaga qaytish | Бозгашт ба мусобиқа |  |
| `problem.countedInContest` | Yechim {contest} musobaqasi hisobiga yoziladi. | Ҳал ба мусобиқаи {contest} ҳисоб карда мешавад. |  |
| `problem.inputFormat` | Kiruvchi ma'lumot | Маълумоти вуруд |  |
| `problem.outputFormat` | Chiquvchi ma'lumot | Маълумоти хуруҷ |  |
| `problem.author` | Muallif | Муаллиф |  |
| `problem.solvedAttempts` | {solved} kishi yechdi · {attempts} urinish | {solved} ҳал карданд · {attempts} кӯшиш |  |
| `problem.successRate` | {percent}% muvaffaqiyat | {percent}% бомуваффақият |  |
| `problem.source` | Manba | Манба |  |
| `problem.sourceRating` | asl reyting {rating} | рейтинги аслӣ {rating} |  |
| `contest.finishedNote` | Musobaqa tugagan — uni virtual tarzda o'z vaqtingizda yechishingiz mumkin. Virtual natija reytingga ta'sir qilmaydi va rasmiy jadvalga kirmaydi. | Мусобиқа ба охир расид — онро виртуалӣ дар вақти худ ҳал карда метавонед. Натиҷаи виртуалӣ ба рейтинг таъсир намекунад ва ба ҷадвали расмӣ дохил намешавад. |  |
| `problem.noAttemptMatch` | Bu filtrga mos urinish yo'q. | Ягон кӯшиш ба ин филтр мувофиқ нест. |  |
| `problem.noAttemptsYet` | Hali urinish yo'q. | Ҳанӯз кӯшиш нест. |  |
| `problem.pagination` | Sahifalar | Саҳифаҳо |  |
| `problem.previousPage` | ← Oldingi | ← Қаблӣ |  |
| `problem.nextPage` | Keyingi → | Баъдӣ → |  |
| `home.greeting` | Salom, {name}! | Салом, {name}! |  |
| `home.resumeHint` | To'xtagan joyingizdan davom eting yoki yaqin musobaqaga yoziling. | Аз ҷое ки мондед идома диҳед ё ба мусобиқаи наздик сабти ном кунед. |  |
| `home.ratingHint` | Reyting xohlaganlar uchun: masala yeching, musobaqada qatnashing, darajangizni ko'ring. | Барои онҳое, ки рейтинг мехоҳанд: масъала ҳал кунед, дар мусобиқа иштирок кунед, сатҳи худро бинед. |  |
| `filter.allLanguages` | Hamma til | Ҳамаи забонҳо |  |
| `filter.onlyMine` | Faqat meniki | Танҳо аз они ман |  |
| `duel.startAt` | Boshlanish | Оғоз |  |
| `hackathon.projectName` | Loyiha nomi | Номи лоиҳа |  |
| `hackathon.entriesAfterDeadline` | Loyihalar muddat tugagach ochiladi | Лоиҳаҳо баъди анҷоми муҳлат кушода мешаванд |  |
| `algorithms.intro` | Qisqa ma'lumotnoma: g'oya, murakkablik, kod, mashq masalalari. | Дастури мухтасар: ғоя, мураккабӣ, код ва масъалаҳои машқ. |  |
| `arena.intro` | Jonli raund: hamma bir vaqtda, har savolga bir necha soniya, standings jonli. | Раунди зинда: ҳама дар як вақт, ба ҳар савол чанд сония, ҷадвал зинда. |  |
| `classroom.intro` | O'qituvchi sinf yaratadi, o'quvchilar kod bilan qo'shiladi, uy vazifasi va progress bir joyda. | Муаллим синф месозад, хонандагон бо код ҳамроҳ мешаванд, вазифаи хонагӣ ва пешрафт дар як ҷо. |  |
| `duels.intro` | Chaqiriq tashlang, kimdir qabul qiladi, belgilangan vaqtda bir xil masalalarni yechasiz. G'olib Challenges reytingida Elo oladi. | Даъват фиристед, касе қабул мекунад, дар вақти муайян ҳамон масъалаҳоро ҳал мекунед. Ғолиб дар рейтинги Challenges Elo мегирад. |  |
| `hackathons.intro` | Masala emas — loyiha. Repozitoriy va demo topshirasiz, hakamlar baholaydi. | На масъала — лоиҳа. Репозиторий ва демо супорида, доварон баҳо медиҳанд. |  |
| `learn.intro` | Har bir maqola mashq masalalari bilan bog'langan — o'qish va yechish bir joyda. | Ҳар мақола бо масъалаҳои машқ алоқаманд аст — хондан ва ҳал кардан дар як ҷо. |  |
| `notifications.signIn` | Bildirishnomalarni ko'rish uchun tizimga kiring. | Барои дидани огоҳиномаҳо ворид шавед. |  |
| `qvant.intro` | Vazifalarni bajarib Qvant to'plang. Qvant reytingga ta'sir qilmaydi — u faqat do'kon uchun. | Вазифаҳоро иҷро карда Qvant ҷамъ кунед. Qvant ба рейтинг таъсир намекунад — он танҳо барои мағоза аст. |  |
| `qvant.signIn` | Balansni ko'rish uchun tizimga kiring. | Барои дидани баланс ворид шавед. |  |
| `roadmaps.intro` | Noldan cho'qqigacha bosqichma-bosqich: maqola → masala → maqola. | Қадам ба қадам аз сифр то қулла: мақола → масъала → мақола. |  |
| `team.intro` | RankWant — O'zbekiston va dunyo uchun sport dasturlash platformasi. Ochiq reyting, o'z judge, o'z kontent. Loyiha hozir ochiq preview bosqichida. | RankWant — платформаи барномасозии варзишӣ барои Ӯзбекистон ва ҷаҳон. Рейтинги кушод, judge-и худ, контенти худ. Лоиҳа ҳоло дар марҳилаи preview-и кушод аст. |  |
| `problem.solvers.codeColumn` | Kod, belgi | Код, аломат |  |
| `problem.stats.empty` | Hali urinish yo'q — statistika bo'sh. | Ҳанӯз кӯшиш нест — омор холӣ аст. |  |
| `problems.noTests` | testsiz | бе тест |  |
| `editor.loading` | Muharrir yuklanmoqda… | Муҳаррир бор мешавад… |  |
| `admin.text.step2Funnel` | 2-qadam (joy va maktab) | Қадами 2 (ҷой ва мактаб) |  |
| `admin.text.stepPlaceholder` | 1-bosqich | Марҳилаи 1 |  |
| `customizer.nav` | Navigatsiya | Навигатсия |  |
| `customizer.navShape` | Panel shakli | Шакли панел |  |
| `customizer.sizeHint` | Butun interfeysga ta'sir qiladi — oraliqlar ham moslashadi. | Ба тамоми интерфейс таъсир мерасонад — фосилаҳо низ тағйир меёбанд. |  |
| `customizer.status` | Holat xabarlari | Паёмҳои ҳолат |  |
| `customizer.hex` | Rang kodi | Рамзи ранг |  |
| `customizer.lineHeight` | Qator balandligi | Баландии сатр |  |
| `customizer.loading` | Yuklanish | Боркунӣ |  |
| `customizer.iconPack` | Ikonka to'plami | Маҷмӯи нишонаҳо |  |
| `customizer.iconPackHint` | Tanlangan to'plam navigatsiya, amallar va holat ikonkalarini o'zgartiradi. Verdikt va brend belgilari qat'iy qoladi. | Маҷмӯи интихобшуда нишонаҳои навигатсия, амалҳо ва ҳолатро иваз мекунад. Нишонаҳои вердикт ва бренд бетағйир мемонанд. |  |
| `customizer.iconPackFixed` | Qat'iy — to'plamga bo'ysunmaydi | Собит — ба маҷмӯъ вобаста нест |  |
| `customizer.iconGalleryShow` | Barchasini ko'rsatish ({n}) | Ҳамаро нишон додан ({n}) |  |
| `customizer.iconGalleryHide` | Galereyani yopish | Пӯшидани галерея |  |
| `customizer.tracking` | Harf oralig'i | Фосилаи ҳарфҳо |  |
| `customizer.typeHint` | Qator balandligi va harf oralig'i uzun matnni o'qishga yordam beradi. | Баландии сатр ва фосилаи ҳарфҳо хондани матни дарозро осон мекунанд. |  |
| `customizer.width` | Kontent kengligi | Паҳнои мундариҷа |  |
| `customizer.widthHint` | Tor kenglik o'qishga qulay, keng kenglik jadvalga. | Паҳнои танг барои хондан, паҳнои васеъ барои ҷадвалҳо. |  |
| `customizer.card` | Karta uslubi | Услуби корт |  |
| `customizer.card.default` | Odatiy | Пешфарз |  |
| `customizer.card.outline` | Chegara | Чорчӯба |  |
| `customizer.card.flat` | Tekis | Ҳамвор |  |
| `customizer.card.soft` | Yumshoq soya | Сояи нарм |  |
| `customizer.card.square` | Keskin burchak | Кунҷи рост |  |
| `customizer.cardHint` | Kontent bloklari qanday ajratiladi: chegara, soya yoki burchak. | Блокҳо чӣ гуна ҷудо мешаванд: чорчӯба, соя ё кунҷ. |  |
| `customizer.pattern` | Fon naqshi | Нақши замина |  |
| `customizer.pattern.none` | Yo'q | Нест |  |
| `customizer.pattern.grid` | To'r | Тӯр |  |
| `customizer.pattern.dots` | Nuqtalar | Нуқтаҳо |  |
| `customizer.pattern.diagonal` | Diagonal | Диагонал |  |
| `customizer.pattern.mesh` | Tuman | Думонак |  |
| `customizer.patternHint` | Kontent orqasida turadi va matnni to'smaydi. | Дар қафои мундариҷа меистад ва матнро намепӯшад. |  |
| `customizer.verdict` | Natija ko'rinishi | Result style |  |
| `verdict.style.auto` | Avtomatik | Automatic |  |
| `verdict.style.autoHint` | Shaklni ekranga qarab tanlaydi: telefonda doira, planshetda ikonka, kompyuterda to'liq nom. | Picks the shape by screen: circle on phone, icon on tablet, full name on desktop. |  |
| `verdict.style.badge` | Faqat nishon | Badge only |  |
| `verdict.style.badgeHint` | Rangli nishonda qisqa kod. Ixcham — zich jadvallar uchun. | Short code on a coloured pill. Compact — for dense tables. |  |
| `verdict.style.plain` | Faqat ikonka | Танҳо нишона |  |
| `verdict.style.plainHint` | Faqat ikonka, rangsiz. Eng izchil ko'rinish — lekin holat darhol sezilmaydi. | Танҳо нишона, беранг. Намуди яксонтарин, вале ҳолат дарҳол намоён намешавад. |  |
| `verdict.style.icon` | Ikonka va rang | Icon + colour |  |
| `verdict.style.iconHint` | Ikonka, qisqa kod va natija rangi. Eng tez o'qiladi. | Icon, short code and result colour. Reads fastest. |  |
| `verdict.style.full` | Ikonka, rang va nom | Icon + colour + name |  |
| `verdict.style.fullHint` | To'liq natija nomi izohi bilan. Ko'proq joy egallaydi. | Full result name with an explanation. Takes more room. |  |
| `verdict.style.circle` | Doira va ikonka | Circle + icon |  |
| `verdict.style.circleHint` | To'ldirilgan doirada oq ikonka. Eng kichik — mobil va tor qatorlar uchun. | Filled circle with a white icon. Smallest — for mobile and tight rows. |  |
| `verdict.style.dot` | Nuqta va kod | Нуқта ва рамз |  |
| `verdict.style.dotHint` | Rangli nuqta va qisqa kod. Jadvaldan yengilroq — log ro'yxatlari uchun. | Нуқтаи рангӣ ва рамзи кӯтоҳ. Азтар аз ҷадвал — барои рӯйхати логҳо. |  |
| `verdict.style.box` | Chegara va ikonka | Чорчӯба ва нишона |  |
| `verdict.style.boxHint` | Ramkali kvadrat ichida ikonka. Faqat signal — matnsiz, lekin ajralib turadi. | Нишона дар дохили чорчӯбаи чоркунҷа. Танҳо сигнал — бе матн, вале намоён. |  |
| `verdict.style.bar` | Chap chiziq va nom | Хатти чап ва ном |  |
| `verdict.style.barHint` | Chap tomonda rangli chiziq, yonida ikonka va to'liq nom. Ogohlantirishlar uchun. | Хатти рангӣ дар тарафи чап, дар паҳлӯяш нишона ва номи пурра. Барои огоҳиномаҳо. |  |
| `verdict.style.percent` | Ikonka va foiz | Нишона ва фоиз |  |
| `verdict.style.percentHint` | Ikonka, qisqa kod va natija foizi. Baholash va qisman natijalar uchun. | Нишона, рамзи кӯтоҳ ва фоизи натиҷа. Барои баҳогузорӣ ва натиҷаҳои қисмӣ. |  |
| `verdict.style.card` | Katta karta | Large card |  |
| `verdict.style.cardHint` | Katta ikonka izohi bilan. Masala sahifasidagi natija paneli uchun. | Big icon with a description. For the result panel on a problem page. |  |
| `verdict.hint.AC` | Barcha testlar o'tdi | All tests passed |  |
| `verdict.hint.WA` | Javob kutilganiga mos emas | Output does not match |  |
| `verdict.hint.TLE` | Belgilangan vaqtdan uzoq ishladi | Ran longer than allowed |  |
| `verdict.hint.MLE` | Belgilangan xotiradan ko'p ishlatdi | Used more memory than allowed |  |
| `verdict.hint.RE` | Dastur ishlash paytida to'xtadi | Program crashed while running |  |
| `verdict.hint.CE` | Kod kompilyatsiya bo'lmadi | Code did not compile |  |
| `verdict.hint.PE` | Ortiqcha bo'sh joy yoki qator | Extra spaces or line breaks |  |
| `verdict.hint.HACKED` | Qabul qilingan yechim boshqa ishtirokchining to'g'ri testida yiqildi | Ҳалли қабулшуда дар тести дурусти иштирокчии дигар ноком шуд |  |
| `verdict.hint.OLE` | Juda ko'p ma'lumot chiqardi | Printed too much output |  |
| `verdict.hint.IE` | Tekshiruvchi xatosi — sizda emas | Judge error, not your fault |  |
| `verdict.hint.PD` | Navbatda kutilmoqda | Waiting in the queue |  |
| `customizer.exportFile` | Faylga saqlash | Ба файл нигоҳ доштан |  |
| `customizer.importFile` | Fayldan yuklash | Аз файл бор кардан |  |
| `customizer.importError.parse` | Fayl to'g'ri JSON emas. | Файл JSON-и дуруст нест. |  |
| `customizer.importError.shape` | Faylda ko'rinish sozlamalari yo'q. | Дар файл танзимоти намуд нест. |  |
| `customizer.importError.version` | Fayl yangiroq versiyada yaratilgan. | Файл бо нусхаи навтар сохта шудааст. |  |
| `customizer.a11y.motion.full` | To'liq | Пурра |  |
| `customizer.a11y.motion.mild` | O'rtacha | Миёна |  |
| `customizer.a11y.motion.off` | O'chiq | Хомӯш |  |
| `customizer.a11y.motionHint` | O'rtacha — o'tishlar qoladi, bezak effektlari o'chadi. | Миёна — гузаришҳо мемонанд, эффектҳои ороишӣ хомӯш мешаванд. |  |
| `customizer.scale` | Shkala zichligi | Зичии шкала |  |
| `customizer.scaleHint` | O'lchamlar orasidagi nisbat — katta sarlavhalar tezroq o'sadi. | Таносуби байни андозаҳо — сарлавҳаҳои калон тезтар меафзоянд. |  |
| `navMode.sidenav.label` | Yon panel | Панели паҳлӯ |  |
| `navMode.sidenav.hint` | Menyu chapda; ikonkagacha yig'iladi. | Меню дар тарафи чап; то нишонаҳо ҷамъ мешавад. |  |
| `navMode.topnav.label` | Ustun panel | Панели боло |  |
| `navMode.topnav.hint` | Menyu tepada; guruhlar ochiladigan ro'yxatda. | Меню дар боло; гурӯҳҳо дар рӯйхати кушодашаванда. |  |
| `navShape.default.label` | Odatiy | Пешфарз |  |
| `navShape.default.hint` | To'liq balandlik, yumaloq burchak. | Баландии пурра, кунҷҳои мудаввар. |  |
| `navShape.slim.label` | Yupqa | Борик |  |
| `navShape.slim.hint` | Bitta siqiq qator, keskin burchak. | Як сатри паймон, кунҷҳои рост. |  |
| `navShape.stacked.label` | Qavatma-qavat | Дуқатора |  |
| `navShape.stacked.hint` | Ikki qator: ustida logo, ostida menyu. | Ду сатр: боло логотип, поён меню. |  |
