# Kazakh (kk) — translation review

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

Regenerate with `python tools/export_i18n_review.py --prefix admin.`.

**319 strings.**

| Key | Uzbek (source) | Kazakh | Review |
| --- | --- | --- | --- |
| `admin.title` | Boshqaruv | Басқару |  |
| `admin.create` | Yaratish | Құру |  |
| `admin.edit` | Tahrirlash | Өңдеу |  |
| `admin.save` | Saqlash | Сақтау |  |
| `admin.delete` | O'chirish | Жою |  |
| `admin.cancel` | Bekor | Бас тарту |  |
| `admin.confirmDelete` | Rostdan o'chirilsinmi? | Шынымен жойылсын ба? |  |
| `admin.forbidden` | Bu bo'lim faqat xodimlar uchun. | Бұл бөлім тек қызметкерлерге арналған. |  |
| `admin.search` | Qidirish… | Іздеу… |  |
| `admin.noRows` | Hech narsa yo'q | Ештеңе жоқ |  |
| `admin.actions` | Amallar | Әрекеттер |  |
| `admin.saved` | Saqlandi | Сақталды |  |
| `admin.section.problems` | Masalalar | Есептер |  |
| `admin.section.reports` | Nuqson xabarlari | Ақаулық хабарламалары |  |
| `admin.section.contests` | Musobaqalar | Жарыстар |  |
| `admin.section.questions` | Savol banki | Сұрақтар банкі |  |
| `admin.section.quizzes` | Testlar | Тесттер |  |
| `admin.section.arena` | Arena | Арена |  |
| `admin.section.tournaments` | Chempionat | Турнирлер |  |
| `admin.section.hackathons` | Hakaton | Хакатондар |  |
| `admin.section.duels` | Duel | Дуэльдер |  |
| `admin.section.articles` | Maqolalar | Мақалалар |  |
| `admin.section.roadmaps` | Traektoriya | Траектория |  |
| `admin.section.posts` | Yangiliklar | Жаңалықтар |  |
| `admin.section.updates` | O'zgarishlar | Өзгерістер |  |
| `admin.section.platformRoadmap` | Yo'l xaritasi | Жол картасы |  |
| `admin.section.roadmapComments` | Reja izohlari | Картаға түсініктемелер |  |
| `admin.section.quests` | Questlar | Квесттер |  |
| `admin.section.shop` | Do'kon | Дүкен |  |
| `admin.section.users` | Foydalanuvchilar | Пайдаланушылар |  |
| `admin.section.analytics` | Analitika | Аналитика |  |
| `admin.label.status.running` | Yurmoqda | Жүріп жатыр |  |
| `admin.label.status.finished` | Tugagan | Аяқталды |  |
| `admin.label.status.pending` | Kutilmoqda | Күтілуде |  |
| `admin.label.status.evaluating` | Baholanmoqda | Бағалануда |  |
| `admin.label.status.completed` | Yakunlangan | Аяқталған |  |
| `admin.label.status.accepted` | Qabul qilindi | Қабылданды |  |
| `admin.label.status.rejected` | Rad etilgan | Қабылданбады |  |
| `admin.label.status.cancelled` | Bekor qilindi | Бас тартылды |  |
| `admin.label.status.done` | Tugadi | Бітті |  |
| `admin.label.status.doneShort` | Bajarilgan | Орындалды |  |
| `admin.label.status.inReview` | Ko'rib chiqilmoqda | Қаралуда |  |
| `admin.label.status.planned` | Rejalashtirilgan | Жоспарланған |  |
| `admin.label.status.inProgress` | Ishlanmoqda | Әзірленуде |  |
| `admin.label.status.shipped` | Chiqarildi | Шығарылды |  |
| `admin.label.status.enabled` | Yoqilgan | Қосылған |  |
| `admin.label.status.busy` | Band | Бос емес |  |
| `admin.label.date.start` | Boshlanish | Басталуы |  |
| `admin.label.date.startAt` | Boshlanish vaqti | Басталу уақыты |  |
| `admin.label.date.end` | Tugash | Аяқталуы |  |
| `admin.label.date.deadline` | Topshirish muddati | Тапсыру мерзімі |  |
| `admin.label.date.publishedAt` | Nashr sanasi | Жарияланған күні |  |
| `admin.label.date.releasedAt` | Chiqarilgan sana | Шығарылған күні |  |
| `admin.label.date.joined` | Qo'shilgan | Қосылды |  |
| `admin.label.duration.freezeMin` | Muzlatish (daqiqa) | Қатыру (минут) |  |
| `admin.label.duration.secondsPerQuestion` | Savol uchun soniya | Сұраққа секунд |  |
| `admin.label.duration.readMin` | O'qish (daqiqa) | Оқу (минут) |  |
| `admin.label.flag.public` | Ommaviy | Жалпыға ашық |  |
| `admin.label.flag.rated` | Reytingli | Рейтингтік |  |
| `admin.label.flag.virtual` | Virtual | Виртуалды |  |
| `admin.label.flag.mirror` | Ko'zgu (asl musobaqa slug'i) | Айна (түпнұсқа жарыс slug) |  |
| `admin.label.flag.repeatable` | Takroriy | Қайталанатын |  |
| `admin.label.flag.repeatPurchase` | Takroriy sotib olinadi | Қайта сатып алынады |  |
| `admin.label.flag.submissionsOpen` | Topshirish ochiq | Тапсыру ашық |  |
| `admin.label.flag.resultsAnnounced` | Natijalar e'loni | Нәтижелер жарияланды |  |
| `admin.label.flag.active` | Faol | Белсенді |  |
| `admin.label.flag.activeHint` | Faol (bloklash uchun olib tashlang) | Белсенді (бұғаттау үшін алып тастаңыз) |  |
| `admin.label.flag.notifyUsers` | Foydalanuvchilarga xabar berish | Пайдаланушыларға хабарлау |  |
| `admin.label.calc.rating` | Hisoblash | Есептеу |  |
| `admin.label.value.freeze` | Hisob | Есеп |  |
| `admin.label.value.rewardQvant` | Mukofot (Qvant) | Сыйлық (Qvant) |  |
| `admin.label.value.priceQvant` | Narx (Qvant) | Бағасы (Qvant) |  |
| `admin.label.value.analysisPriceQvant` | Tahlilni ochish narxi, Qvant | Талдауды ашу бағасы, Qvant |  |
| `admin.label.value.difficulty` | Qiyinlik | Қиындығы |  |
| `admin.label.value.difficultyRange` | Qiyinlik (800–3500, qadam 100) | Қиындық (800–3500, қадам 100) |  |
| `admin.label.value.scoring` | Skoring (0–100) | Скоринг (0–100) |  |
| `admin.label.value.timeLimit` | Vaqt limiti, ms | Уақыт шегі, мс |  |
| `admin.label.value.memoryLimit` | Xotira limiti, KB | Жады шегі, КБ |  |
| `admin.label.text.title` | Sarlavha | Тақырып |  |
| `admin.label.text.summary` | Qisqacha | Қысқаша |  |
| `admin.label.text.markdown` | Matn (Markdown) | Мәтін (Markdown) |  |
| `admin.label.text.markdownLatex` | Matn (Markdown + LaTeX) | Мәтін (Markdown + LaTeX) |  |
| `admin.label.text.descriptionMarkdown` | Tavsif (Markdown) | Сипаттама (Markdown) |  |
| `admin.label.text.statementLatex` | Shart (Markdown + LaTeX) | Шарт (Markdown + LaTeX) |  |
| `admin.label.text.articleExample` | Maqoladagi misol | Мақаладағы мысал |  |
| `admin.label.text.editorNote` | Muharrir maqolasi | Редактор жазбасы |  |
| `admin.label.text.editorial` | Yechim tahlili | Талдау |  |
| `admin.label.text.solutionExplanation` | Yechim tushuntirishi | Шешім түсіндірмесі |  |
| `admin.label.text.problemExample` | Algoritm | Алгоритм |  |
| `admin.label.text.problemTraining` | Mashq uchun | Жаттығу үшін |  |
| `admin.label.tech.input` | Kiruvchi ma'lumot | Кіріс деректері |  |
| `admin.label.tech.output` | Chiquvchi ma'lumot | Шығыс деректері |  |
| `admin.label.tech.topicsSlug` | Mavzular (slug, vergul bilan) | Тақырыптар (slug, үтірмен) |  |
| `admin.label.tech.parentTopic` | Ota mavzu (slug) | Ата-ана тақырып (slug) |  |
| `admin.label.tech.parent` | Ota | Ата-ана |  |
| `admin.label.tech.sourceUrl` | Manba URL | Дереккөз URL |  |
| `admin.label.tech.sourceLinks` | Manba havolalari | Дереккөз сілтемелері |  |
| `admin.label.tech.githubUrl` | GitHub havolasi | GitHub сілтемесі |  |
| `admin.label.tech.imageUrl` | Rasm havolasi | Сурет сілтемесі |  |
| `admin.label.tech.changelogId` | Changelog yozuvi ID | Changelog жазба ID |  |
| `admin.label.tech.checkerLanguage` | Checker tili (kod, masalan cpp23) | Checker тілі (код, мыс. cpp23) |  |
| `admin.label.tech.checkerSource` | Checker manbasi | Checker бастапқы коды |  |
| `admin.label.tech.interactorLanguage` | Interactor tili (kod, masalan cpp23) | Interactor тілі (код, мыс. cpp23) |  |
| `admin.label.tech.interactorSource` | Interactor manbasi | Interactor бастапқы коды |  |
| `admin.label.name.uz` | Nomi (uz) | Атауы (uz) |  |
| `admin.label.name.ru` | Nomi (ru) | Атауы (ru) |  |
| `admin.label.name.en` | Nomi (en) | Атауы (en) |  |
| `admin.label.name.translation` | Tarjima | Аударма |  |
| `admin.label.name.language` | Matn tili (uz/ru/en) | Шарт тілі (uz/ru/en) |  |
| `admin.label.name.shown` | Ko'rsatiladigan ism | Көрсетілетін атау |  |
| `admin.label.ab.control` | Nazorat (2-qadamda) | Бақылау (2-қадамда) |  |
| `admin.label.ab.variant` | Variant (ro'yxatda) | Нұсқа (тізімде) |  |
| `admin.label.misc.participant` | Ishtirokchi | Қатысушы |  |
| `admin.label.misc.challenger` | Chaqiruvchi | Шақырушы |  |
| `admin.label.misc.projects` | Loyihalar | Жобалар |  |
| `admin.label.misc.news` | Yangilik | Жаңалық |  |
| `admin.label.misc.announcement` | E'lon | Хабарландыру |  |
| `admin.label.text.slug` | Slug | Слаг |  |
| `admin.label.text.status` | Holat | Күйі |  |
| `admin.label.text.name` | Nomi | Атауы |  |
| `admin.label.text.kind` | Turi | Түрі |  |
| `admin.label.text.language` | Til | Тілі |  |
| `admin.label.flag.published` | Nashr qilingan | Жарияланған |  |
| `admin.label.text.description` | Tavsif | Сипаттама |  |
| `admin.label.text.comment` | Izoh | Түсініктеме |  |
| `admin.label.text.code` | Kod | Код |  |
| `admin.label.flag.open` | Ochiq | Ашық |  |
| `admin.label.text.deadline` | Muddat | Мерзім |  |
| `admin.label.text.date` | Sana | Күні |  |
| `admin.label.misc.questions` | Savollar | Сұрақтар |  |
| `admin.label.misc.topics` | Mavzular | Тақырыптар |  |
| `admin.label.misc.problems` | Masalalar | Есептер |  |
| `admin.label.text.author` | Muallif | Авторы |  |
| `admin.label.text.flag` | Flag | Жалауша |  |
| `admin.label.text.type` | Tur | Түрі |  |
| `admin.label.text.category` | Kategoriya | Санат |  |
| `admin.label.text.module` | Modul | Модуль |  |
| `admin.label.flag.staff` | Xodim | Қызметкер |  |
| `admin.label.text.article` | Maqola | Мақала |  |
| `admin.label.text.opponent` | Raqib | Қарсылас |  |
| `admin.label.text.result` | Natija | Нәтиже |  |
| `admin.label.text.end` | Yakun | Аяқталуы |  |
| `admin.label.misc.votes` | Ovoz | Дауыстар |  |
| `admin.label.text.message` | Xabar | Хабарлама |  |
| `admin.label.text.checker` | Checker | Чекер |  |
| `admin.label.text.standard` | Standart | Стандартты |  |
| `admin.label.text.special` | Maxsus | Арнайы |  |
| `admin.label.text.interactive` | Interactive | Интерактивті |  |
| `admin.label.text.source` | Manba | Дереккөз |  |
| `admin.label.misc.tests` | Testlar | Тесттер |  |
| `admin.label.text.reward` | Mukofot | Сыйлық |  |
| `admin.label.text.qvant` | Qvant | Квант |  |
| `admin.label.text.problem` | Masala | Есеп |  |
| `admin.label.text.reason` | Sabab | Себебі |  |
| `admin.label.text.who` | Kim | Кім |  |
| `admin.label.text.order` | Tartib | Тәртібі |  |
| `admin.label.misc.steps` | Qadamlar | Қадамдар |  |
| `admin.label.text.price` | Narx | Бағасы |  |
| `admin.label.misc.owners` | Egalari | Иелері |  |
| `admin.label.text.asset` | Asset | Ассет |  |
| `admin.label.misc.stages` | Bosqichlar | Кезеңдер |  |
| `admin.label.text.version` | Versiya | Нұсқасы |  |
| `admin.label.text.repo` | Repo | Репозиторий |  |
| `admin.label.text.username` | Login | Логин |  |
| `admin.label.text.displayName` | Ism | Аты |  |
| `admin.label.text.email` | Email | Пошта |  |
| `admin.label.misc.ratings` | Reytinglar | Рейтингтер |  |
| `admin.label.text.bio` | Bio | Өзі туралы |  |
| `admin.label.duration.perQuestion` | s/savol | с/сұрақ |  |
| `admin.label.text.num` | # | # |  |
| `admin.label.text.acmIcpc` | ACM/ICPC | ACM/ICPC |  |
| `admin.label.text.ioi` | IOI | IOI |  |
| `admin.label.lang.uz` | uz | uz |  |
| `admin.label.lang.ru` | ru | ru |  |
| `admin.label.lang.en` | en | en |  |
| `admin.help.topicsSlug` | Topic sluglari, vergul bilan | Тақырып слагтары, үтір арқылы |  |
| `admin.help.freezeStandings` | Oxirgi N daqiqada standings yangilanmaydi | Соңғы N минутта кесте жаңартылмайды |  |
| `admin.help.submissionClose` | Shu vaqtdan keyin topshirish yopiladi va loyihalar hammaga ochiladi | Осы уақыттан кейін тапсыру жабылады, жобалар барлығына ашылады |  |
| `admin.help.rulesAndPrizes` | Shartlar, mezonlar, sovrin | Шарттар, критерийлер, жүлделер |  |
| `admin.help.targetQuarter` | Chorak darajasida (2026-Q4). ANIQ SANA YOZILMAYDI — bajarilmasa ishonch buziladi | Тоқсан деңгейінде (2026-Q4). НАҚТЫ КҮН ЖАЗЫЛМАЙДЫ — орындалмаса сенім бұзылады |  |
| `admin.help.changelogId` | Chiqarilganda bog'lanadigan yozuv raqami. Batafsil sahifada havola bo'ladi | Шығарылым байланысатын жазба нөмірі. Толық бетте сілтеме болады |  |
| `admin.help.softDelete` | O'chirilsa band ko'rinmaydi, lekin ovozlari bilan bazada qoladi | Өшірілсе жазба көрінбейді, бірақ дауыстарымен базада қалады |  |
| `admin.help.autoPublishAt` | Bo'sh qolsa — birinchi nashrda avtomatik qo'yiladi | Бос қалса — бірінші жариялауда автоматты қойылады |  |
| `admin.help.notifyOnce` | Nashrdan keyin barcha foydalanuvchiga bir marta bildirishnoma yuboriladi | Жариялағаннан кейін барлық пайдаланушыға бір рет хабарлама жіберіледі |  |
| `admin.help.inputFormatSection` | Sahifada alohida bo'lim bo'lib chiqadi | Бетте жеке бөлім болып шығады |  |
| `admin.help.noteExplainsSamples` | Namunalar nega shunday ekanini tushuntiradi | Мысалдардың неге осылай екенін түсіндіреді |  |
| `admin.help.editorialFreeForSolvers` | Masalani yechgan bepul ko'radi (ADR-0013) | Есепті шешкендерге тегін (ADR-0013) |  |
| `admin.help.editorialPrice` | Yechmaganlar uchun. 0 — hammaga bepul | Шешпегендер үшін. 0 — барлығына тегін |  |
| `admin.help.interactorOnlyInteractive` | Faqat Interactive uchun. Bo'sh = yo'q | Тек Interactive үшін. Бос = жоқ |  |
| `admin.help.checkerRequired` | Maxsus va Skoring uchun. Bo'sh bo'lsa har yuborish IE bo'ladi | «Арнайы» және «Скоринг» үшін. Бос болса, әр жіберу IE болады |  |
| `admin.help.testlibInvocation` | testlib chaqiruvi: checker <input> <output> <answer> | testlib шақыруы: checker <input> <output> <answer> |  |
| `admin.help.parentEmptyRoot` | Bo'sh = ildiz | Бос = түбір |  |
| `admin.help.questCodeMatch` | Hodisaga bog'lanish uchun qvant/quests.py dagi kod bilan mos bo'lishi kerak | Оқиғаны байланыстыру үшін qvant/quests.py кодымен сәйкес болуы керек |  |
| `admin.help.cosmeticOnly` | ADR-0002: v1 da faqat kosmetika va qulaylik | ADR-0002: v1-де тек косметика және қолайлық |  |
| `admin.help.assetRef` | Ramka/cover fayliga havola yoki kalit | Жақтау/мұқаба файлына сілтеме немесе кілті |  |
| `admin.help.repeatPerItem` | Streak freeze — ha, ramka — yo'q | Streak freeze — иә, жақтау — жоқ |  |
| `admin.help.publishedAtAuto` | «Nashrda» qilib qo'yilsa `published_at` avtomatik yoziladi | «Жарияланған» қойылса, `published_at` автоматты жазылады |  |
| `admin.help.releasedAtReal` | O'zgarishning HAQIQIY sanasi — yozuv kechroq yozilishi mumkin | Өзгерістің НАҚТЫ күні — жазба кейінірек жазылуы мүмкін |  |
| `admin.help.versionOptional` | Ixtiyoriy, v1.4.0 | Міндетті емес, v1.4.0 |  |
| `admin.help.refsFormat` | Commit SHA, PR raqami, release tegi — vergul bilan | Commit SHA, PR нөмірі, release тегі — үтір арқылы |  |
| `admin.help.screenshotWhenNeeded` | Faqat kerak bo'lganda — dizayn o'zgarishlari uchun skrinshot | Тек қажет болғанда — дизайн өзгерістері үшін скриншот |  |
| `admin.help.staffOnlySuperuser` | Faqat superuser o'zgartira oladi. O'z hisobingizni o'zgartira olmaysiz. | Тек суперпайдаланушы өзгерте алады. Өз тіркелгіңізді өзгерте алмайсыз. |  |
| `admin.help.languageCodes` | uz / ru / en | uz / ru / en |  |
| `admin.help.zeroAuto` | 0 = avtomatik | 0 = автоматты |  |
| `admin.help.upTo300Chars` | 300 belgigacha | 300 таңбаға дейін |  |
| `admin.help.twoLetterDefaultUz` | 2 harf, standart: uz | 2 әріп, әдепкі: uz |  |
| `admin.help.ownerRepo` | owner/repo | иесі/репозиторий |  |
| `admin.text.eventFormStarted` | Forma boshlandi | Пішін басталды |  |
| `admin.text.eventRegisterDone` | Ro'yxatdan o'tdi | Тіркелді |  |
| `admin.text.eventSessions` | {name}: {sessions} sessiya, {share}% | {name}: {sessions} сессия, {share}% |  |
| `admin.text.funnelDay` | {date}: {started} boshlandi, {done} tugadi | {date}: {started} бастады, {done} аяқтады |  |
| `admin.text.reasonLoginTaken` | Login band | Логин бос емес |  |
| `admin.text.reasonPasswordMismatch` | Parollar mos emas | Құпия сөздер сәйкес емес |  |
| `admin.text.reasonTermsNotAccepted` | Shartlarga rozilik berilmagan | Шарттар қабылданбаған |  |
| `admin.text.reasonEmailTaken` | Email band yoki noto'g'ri | Пошта бос емес немесе қате |  |
| `admin.text.reasonServerError` | Server xatosi | Сервер қатесі |  |
| `admin.text.reasonNetworkError` | Tarmoq xatosi | Желі қатесі |  |
| `admin.text.reasonUnknown` | Sababsiz | Себепсіз |  |
| `admin.text.reportReasonStatement` | Matnda xato | Мәтінде қате |  |
| `admin.text.reportReasonTests` | Testlar noto'g'ri | Тесттер дұрыс емес |  |
| `admin.text.reportReasonTranslation` | Tarjima xato | Аударма қате |  |
| `admin.text.reportReasonDuplicate` | Takroriy masala | Қайталанатын есеп |  |
| `admin.text.reportReasonOther` | Boshqa | Басқа |  |
| `admin.label.status.draft` | Qoralama | Жоба |  |
| `admin.label.status.published` | Nashrda | Жарияланған |  |
| `admin.label.status.withdrawn` | Nashrdan olingan | Жариялаудан алынды |  |
| `admin.label.status.rejectedShort` | Rad etildi | Қабылданбады |  |
| `admin.text.error` | Xato | Қате |  |
| `admin.text.unpublish` | Nashrdan olish | Жариялаудан алу |  |
| `admin.text.publishVerb` | Nashr qilish | Жариялау |  |
| `admin.label.misc.questDaily` | Kunlik | Күнделікті |  |
| `admin.label.misc.questWeekly` | Haftalik | Апталық |  |
| `admin.label.misc.questAchievement` | Yutuq | Жетістік |  |
| `admin.label.shopCategory.streakFreeze` | Streak freeze | Серияны тоқтату |  |
| `admin.label.shopCategory.avatarFrame` | Avatar ramka | Аватар жақтауы |  |
| `admin.label.shopCategory.profileCover` | Profil cover | Профиль мұқабасы |  |
| `admin.label.shopCategory.usernameBadge` | Username badge | Логин белгісі |  |
| `admin.title.order` | Tartib | Тәртібі |  |
| `admin.title.signupFunnel` | Ro'yxatdan o'tish voronkasi | Тіркелу воронкасы |  |
| `admin.title.abRegion` | A/B: viloyat qachon so'raladi | A/B: облыс қашан сұралады |  |
| `admin.title.total` | Jami | Барлығы |  |
| `admin.title.errorReasons` | Xato sabablari | Қате себептері |  |
| `admin.title.languages` | Tillar | Тілдер |  |
| `admin.title.countries` | Mamlakatlar | Елдер |  |
| `admin.title.daily` | Kunlik | Күнделікті |  |
| `admin.title.points` | Ball | Ұпайлар |  |
| `admin.title.duels` | Duellar | Дуэльдер |  |
| `admin.title.hackathons` | Hakatonlar | Хакатондар |  |
| `admin.title.topics` | Mavzular | Тақырыптар |  |
| `admin.title.moveUp` | Yuqoriga | Жоғары |  |
| `admin.title.moveDown` | Pastga | Төмен |  |
| `admin.title.remove` | Olib tashlash | Алып тастау |  |
| `admin.title.roadmapComments` | Yo'l xaritasi izohlari | Жол картасы түсініктемелері |  |
| `admin.title.tournaments` | Chempionatlar | Чемпионаттар |  |
| `admin.title.broadcast` | Umumiy e'lon | Жалпы хабарлама |  |
| `admin.title.page` | Admin | Әкімші |  |
| `admin.placeholder.questionId` | Savol ID | Сұрақ ID |  |
| `admin.placeholder.problemSlug` | masala slug'i | есеп слагі |  |
| `admin.placeholder.title` | Sarlavha | Тақырып |  |
| `admin.placeholder.comment` | Fikr | Пікір |  |
| `admin.placeholder.articleSlug` | maqola slugi | мақала слагі |  |
| `admin.placeholder.amount` | ±miqdor | ±сома |  |
| `admin.placeholder.ledgerComment` | Izoh (ledgerga yoziladi) | Түсініктеме (журналға жазылады) |  |
| `admin.placeholder.text` | Matn | Мәтін |  |
| `admin.placeholder.textOptional` | Matn (ixtiyoriy) | Мәтін (міндетті емес) |  |
| `admin.text.badgeActive` | faol | белсенді |  |
| `admin.text.badgeBlocked` | bloklangan | бұғатталған |  |
| `admin.text.badgeSuperuser` | superuser | суперпайдаланушы |  |
| `admin.text.badgeStaff` | xodim | қызметкер |  |
| `admin.text.badgeHidden` | yashirin | жасырын |  |
| `admin.text.badgeRewarded` | mukofotlangan | марапатталған |  |
| `admin.text.badgeLive` | jonli | тікелей |  |
| `admin.text.badgeFinished` | tugagan | аяқталған |  |
| `admin.text.badgeRated` | reytingli | рейтингтік |  |
| `admin.text.badgeClosed` | yopiq | жабық |  |
| `admin.text.badgeCompleted` | yakunlangan | аяқталған |  |
| `admin.text.badgeRepo` | repo | репозиторий |  |
| `admin.text.badgeDemo` | demo | демо |  |
| `admin.text.badgeSample` | namuna | үлгі |  |
| `admin.text.badgeOptional` | ixtiyoriy | міндетті емес |  |
| `admin.text.addProblem` | + Masala | + Есеп |  |
| `admin.text.addVariant` | + Variant | + Нұсқа |  |
| `admin.text.addStep` | + Qadam | + Қадам |  |
| `admin.text.addStage` | + Bosqich | + Кезең |  |
| `admin.text.reschedule` | Qayta rejalashtirish | Қайта жоспарлау |  |
| `admin.text.rebuildStandings` | Standings qayta qurish | Кестені қайта құру |  |
| `admin.text.recalcTable` | Jadvalni qayta hisoblash | Кестені қайта есептеу |  |
| `admin.text.restoreCatalog` | Katalogni tiklash | Каталогты қалпына келтіру |  |
| `admin.text.sendToAll` | Hammaga yuborish | Барлығына жіберу |  |
| `admin.text.cancel` | Bekor qilish | Болдырмау |  |
| `admin.text.loading` | yuklanmoqda… | жүктелуде… |  |
| `admin.text.orderNumber` | Tartib raqami * | Реттік нөмірі * |  |
| `admin.text.contestSlug` | Contest slug | Контест слагі |  |
| `admin.text.noErrors` | Xato qayd etilmagan. | Қате тіркелмеген. |  |
| `admin.text.highSkipRate` | Bu raqam yuqori bo'lsa, 2-qadam odamni charchatyapti. | Бұл сан жоғары болса, 2-қадам адамды шаршатады. |  |
| `admin.text.dailyLegend` | Kulrang — boshlangan, rangli — tugagan. Har ustun bir kun. | Сұр — бастады, түсті — аяқтады. Әр баған — бір күн. |  |
| `admin.text.publish` | Nashr | Жариялау |  |
| `admin.text.finish` | Yakunlash | Аяқтау |  |
| `admin.text.rollback` | Qaytarish | Қайтару |  |
| `admin.text.hidden` | Yashirilgan | Жасырылған |  |
| `admin.text.deleteRollback` | O'chirish (rollback) | Жою (қайтару) |  |
| `admin.text.ratingsAppliedAt` | Yakunlangan: {date} | Аяқталды: {date} |  |
| `admin.text.draw` | Durang ({score}) | Тең ({score}) |  |
| `admin.text.add` | Qo'shish | Қосу |  |
| `admin.text.apply` | Qo'llash | Қолдану |  |
| `admin.text.linkedProblems` | Bog'langan masalalar | Байланысқан есептер |  |
| `admin.text.questionsInOrder` | Savollar (tartib bo'yicha) | Сұрақтар (ретімен) |  |
| `admin.text.mirrorOf` | ko'zgu: {slug} | айна: {slug} |  |
| `admin.text.variant` | Variant {order} | Нұсқа {order} |  |
| `admin.text.noStages` | Bosqichlar yo'q — contest qo'shing. | Кезеңдер жоқ — контест қосыңыз. |  |
| `admin.text.forceFinish` | Majburan yakunlash | Мәжбүрлеп аяқтау |  |
| `admin.text.no` | yo'q | жоқ |  |
| `admin.text.disabled` | O'chirilgan | Өшірілген |  |
| `admin.text.off` | O'chiq | Өшірулі |  |
| `admin.text.enable` | Yoqish | Қосу |  |
| `admin.text.hide` | Yashirish | Жасыру |  |
| `admin.text.visible` | Ko'rinadi | Көрінеді |  |
| `admin.text.tableRecalculated` | Jadval qayta hisoblandi — ishtirokchilar: {count} | Кесте қайта есептелді — қатысушылар: {count} |  |
| `admin.text.yes` | ha | иә |  |
