# Kyrgyz (ky) — translation review

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

Regenerate with `python tools/export_i18n_review.py --prefix "admin."`.

**353 strings.**

| Key | Uzbek (source) | Kyrgyz | Review |
| --- | --- | --- | --- |
| `admin.title` | Boshqaruv | Башкаруу |  |
| `admin.create` | Yaratish | Түзүү |  |
| `admin.edit` | Tahrirlash | Түзөтүү |  |
| `admin.save` | Saqlash | Сактоо |  |
| `admin.delete` | O'chirish | Өчүрүү |  |
| `admin.cancel` | Bekor | Жокко чыгаруу |  |
| `admin.confirmDelete` | Rostdan o'chirilsinmi? | Чын эле өчүрүлсүнбү? |  |
| `admin.forbidden` | Bu bo'lim faqat xodimlar uchun. | Бул бөлүм кызматкерлер үчүн гана. |  |
| `admin.search` | Qidirish… | Издөө… |  |
| `admin.noRows` | Hech narsa yo'q | Эч нерсе жок |  |
| `admin.actions` | Amallar | Аракеттер |  |
| `admin.saved` | Saqlandi | Сакталды |  |
| `admin.section.problems` | Masalalar | Маселелер |  |
| `admin.section.reports` | Nuqson xabarlari | Кемчилик кабарлары |  |
| `admin.section.contests` | Musobaqalar | Мелдештер |  |
| `admin.section.questions` | Savol banki | Суроолор банкы |  |
| `admin.section.quizzes` | Testlar | Тесттер |  |
| `admin.section.arena` | Arena | Арена |  |
| `admin.section.tournaments` | Chempionat | Турнирлер |  |
| `admin.section.hackathons` | Hakaton | Хакатондор |  |
| `admin.section.duels` | Duel | Дуэлдер |  |
| `admin.section.articles` | Maqolalar | Макалалар |  |
| `admin.section.roadmaps` | Traektoriya | Траектория |  |
| `admin.section.posts` | Yangiliklar | Жаңылыктар |  |
| `admin.section.updates` | O'zgarishlar | Өзгөрүүлөр |  |
| `admin.section.platformRoadmap` | Yo'l xaritasi | Жол картасы |  |
| `admin.section.roadmapComments` | Reja izohlari | Картага комментарийлер |  |
| `admin.section.quests` | Questlar | Квесттер |  |
| `admin.section.shop` | Do'kon | Дүкөн |  |
| `admin.section.users` | Foydalanuvchilar | Колдонуучулар |  |
| `admin.section.analytics` | Analitika | Аналитика |  |
| `admin.section.emailQuota` | Email kvota | Email квотасы |  |
| `admin.quotaProvider` | Provayder | Кызмат |  |
| `admin.quotaSent` | Yuborildi | Жиберілди |  |
| `admin.quotaLimit` | Shift | Чектөө |  |
| `admin.quotaLeft` | Qoldi | Калды |  |
| `admin.quotaState` | Holat | Абалы |  |
| `admin.quotaExhausted` | Kvota tugadi | Квота түгөндү |  |
| `admin.quotaWarning` | Tugayapti ({percent}%) | Түгөнүп баратат ({percent}%) |  |
| `admin.quotaInQueue` | Kvota tugadi — qolgani navbatda ({n} gacha, kechikish bilan) | Квота түгөндү — калганы кезекте ({n} чейин, кечигүү менен) |  |
| `admin.quotaLost` | {n} xat yetkazilmaydi (navbat ham to'ldi) | {n} кат жеткирилбейт (кезек да толду) |  |
| `admin.quotaUnset` | kvota belgilanmagan | квота белгиленген эмес |  |
| `admin.quotaTodayLeft` | Bugun yana: | Бүгүн калды: |  |
| `admin.quotaWindowLabel` | Qaysi kun | Кайсы күн |  |
| `admin.quotaWindowToday` | Bugun | Бүгүн |  |
| `admin.quotaWindowYesterday` | Kecha | Кечээ |  |
| `admin.quotaWindowWeek` | 7 kun | 7 күн |  |
| `admin.quotaSpent` | Shu kun sarfi: | Ошол күнкү сарпталганы: |  |
| `admin.quotaWithQueue` | (navbat bilan birga {n} gacha) | (кезек менен {n} чейин) |  |
| `admin.quotaFailures` | {n} xat yuborilmadi | {n} кат жиберилген жок |  |
| `admin.quotaUtcNote` | Kun chegarasi — UTC kalendar kuni (Resend va Brevo shunday belgilaydi). Navbatdagi xat yo'qolmaydi, lekin kechikadi. | Чек — UTC күнү. Кезектеги кат жоголбойт, бирок кечигет. |  |
| `admin.quotaLoadFail` | Kvota ma'lumotini yuklab bo'lmadi. | Квота маалыматын жүктөө мүмкүн болбоду. |  |
| `admin.label.status.running` | Yurmoqda | Жүрүп жатат |  |
| `admin.label.status.finished` | Tugagan | Аяктады |  |
| `admin.label.status.pending` | Kutilmoqda | Күтүлүүдө |  |
| `admin.status.sent` | Yuborildi | Жөнөтүлдү |  |
| `admin.label.status.evaluating` | Baholanmoqda | Бааланууда |  |
| `admin.label.status.completed` | Yakunlangan | Аякталган |  |
| `admin.label.status.accepted` | Qabul qilindi | Кабыл алынды |  |
| `admin.label.status.rejected` | Rad etilgan | Четке кагылды |  |
| `admin.label.status.cancelled` | Bekor qilindi | Жокко чыгарылды |  |
| `admin.label.status.done` | Tugadi | Бүттү |  |
| `admin.label.status.doneShort` | Bajarilgan | Аткарылды |  |
| `admin.label.status.inReview` | Ko'rib chiqilmoqda | Каралууда |  |
| `admin.label.status.planned` | Rejalashtirilgan | Пландалган |  |
| `admin.label.status.inProgress` | Ishlanmoqda | Иштелүүдө |  |
| `admin.label.status.shipped` | Chiqarildi | Чыгарылды |  |
| `admin.label.status.enabled` | Yoqilgan | Күйгүзүлгөн |  |
| `admin.label.status.busy` | Band | Бош эмес |  |
| `admin.label.date.start` | Boshlanish | Башталышы |  |
| `admin.label.date.startAt` | Boshlanish vaqti | Башталуу убактысы |  |
| `admin.label.date.end` | Tugash | Аяктоо |  |
| `admin.label.date.deadline` | Topshirish muddati | Тапшыруу мөөнөтү |  |
| `admin.label.date.publishedAt` | Nashr sanasi | Жарыяланган күнү |  |
| `admin.label.date.releasedAt` | Chiqarilgan sana | Чыгарылган күнү |  |
| `admin.label.date.joined` | Qo'shilgan | Кошулду |  |
| `admin.label.duration.freezeMin` | Muzlatish (daqiqa) | Тоңдуруу (мүнөт) |  |
| `admin.label.duration.secondsPerQuestion` | Savol uchun soniya | Суроого секунд |  |
| `admin.label.duration.readMin` | O'qish (daqiqa) | Окуу (мүнөт) |  |
| `admin.label.flag.public` | Ommaviy | Жалпыга ачык |  |
| `admin.label.flag.rated` | Reytingli | Рейтингдик |  |
| `admin.label.flag.virtual` | Virtual | Виртуалдык |  |
| `admin.label.flag.mirror` | Ko'zgu (asl musobaqa slug'i) | Күзгү (түпнуска мелдеш slug) |  |
| `admin.label.flag.repeatable` | Takroriy | Кайталануучу |  |
| `admin.label.flag.repeatPurchase` | Takroriy sotib olinadi | Кайра сатып алынат |  |
| `admin.label.flag.submissionsOpen` | Topshirish ochiq | Тапшыруу ачык |  |
| `admin.label.flag.resultsAnnounced` | Natijalar e'loni | Жыйынтыктар жарыяланды |  |
| `admin.label.flag.active` | Faol | Активдүү |  |
| `admin.label.flag.activeHint` | Faol (bloklash uchun olib tashlang) | Активдүү (бөгөттөө үчүн алып салыңыз) |  |
| `admin.label.flag.notifyUsers` | Foydalanuvchilarga xabar berish | Колдонуучуларга кабарлоо |  |
| `admin.label.calc.rating` | Hisoblash | Эсептөө |  |
| `admin.label.value.freeze` | Hisob | Эсеп |  |
| `admin.label.value.rewardQvant` | Mukofot (Qvant) | Сыйлык (Qvant) |  |
| `admin.label.value.priceQvant` | Narx (Qvant) | Баасы (Qvant) |  |
| `admin.label.value.analysisPriceQvant` | Tahlilni ochish narxi, Qvant | Талдоону ачуу баасы, Qvant |  |
| `admin.label.value.difficulty` | Qiyinlik | Кыйындыгы |  |
| `admin.label.value.difficultyRange` | Qiyinlik (800–3500, qadam 100) | Кыйындык (800–3500, кадам 100) |  |
| `admin.label.value.scoring` | Skoring (0–100) | Скоринг (0–100) |  |
| `admin.label.value.timeLimit` | Vaqt limiti, ms | Убакыт чеги, мс |  |
| `admin.label.value.memoryLimit` | Xotira limiti, KB | Эс чеги, КБ |  |
| `admin.label.text.title` | Sarlavha | Аталыш |  |
| `admin.label.text.summary` | Qisqacha | Кыскача |  |
| `admin.label.text.markdown` | Matn (Markdown) | Текст (Markdown) |  |
| `admin.label.text.markdownLatex` | Matn (Markdown + LaTeX) | Текст (Markdown + LaTeX) |  |
| `admin.label.text.descriptionMarkdown` | Tavsif (Markdown) | Сүрөттөмө (Markdown) |  |
| `admin.label.text.statementLatex` | Shart (Markdown + LaTeX) | Шарт (Markdown + LaTeX) |  |
| `admin.label.text.articleExample` | Maqoladagi misol | Макаладагы мисал |  |
| `admin.label.text.editorNote` | Muharrir maqolasi | Редактор жазуусу |  |
| `admin.label.text.editorial` | Yechim tahlili | Талдоо |  |
| `admin.label.text.solutionExplanation` | Yechim tushuntirishi | Чечим түшүндүрмөсү |  |
| `admin.label.text.problemExample` | Algoritm | Алгоритм |  |
| `admin.label.text.problemTraining` | Mashq uchun | Машыгуу үчүн |  |
| `admin.label.tech.input` | Kiruvchi ma'lumot | Кирүү маалыматтары |  |
| `admin.label.tech.output` | Chiquvchi ma'lumot | Чыгуу маалыматтары |  |
| `admin.label.tech.topicsSlug` | Mavzular (slug, vergul bilan) | Темалар (slug, үтүр менен) |  |
| `admin.label.tech.parentTopic` | Ota mavzu (slug) | Аталык тема (slug) |  |
| `admin.label.tech.parent` | Ota | Аталык |  |
| `admin.label.tech.sourceUrl` | Manba URL | Булак URL |  |
| `admin.label.tech.sourceLinks` | Manba havolalari | Булак шилтемелери |  |
| `admin.label.tech.githubUrl` | GitHub havolasi | GitHub шилтемеси |  |
| `admin.label.tech.imageUrl` | Rasm havolasi | Сүрөт шилтемеси |  |
| `admin.label.tech.changelogId` | Changelog yozuvi ID | Changelog жазуу ID |  |
| `admin.label.tech.checkerLanguage` | Checker tili (kod, masalan cpp23) | Checker тили (код, мис. cpp23) |  |
| `admin.label.tech.checkerSource` | Checker manbasi | Checker булагы |  |
| `admin.label.tech.interactorLanguage` | Interactor tili (kod, masalan cpp23) | Interactor тили (код, мис. cpp23) |  |
| `admin.label.tech.interactorSource` | Interactor manbasi | Interactor булагы |  |
| `admin.label.name.uz` | Nomi (uz) | Аталышы (uz) |  |
| `admin.label.name.ru` | Nomi (ru) | Аталышы (ru) |  |
| `admin.label.name.en` | Nomi (en) | Аталышы (en) |  |
| `admin.label.name.translation` | Tarjima | Котормо |  |
| `admin.label.name.language` | Matn tili (uz/ru/en) | Шарт тили (uz/ru/en) |  |
| `admin.label.name.shown` | Ko'rsatiladigan ism | Көрсөтүлүүчү ат |  |
| `admin.label.ab.control` | Nazorat (2-qadamda) | Көзөмөл (2-кадамда) |  |
| `admin.label.ab.variant` | Variant (ro'yxatda) | Вариант (тизмеде) |  |
| `admin.label.misc.participant` | Ishtirokchi | Катышуучу |  |
| `admin.label.misc.challenger` | Chaqiruvchi | Чакыруучу |  |
| `admin.label.misc.projects` | Loyihalar | Долбоорлор |  |
| `admin.label.misc.news` | Yangilik | Жаңылык |  |
| `admin.label.misc.announcement` | E'lon | Жарыялоо |  |
| `admin.label.text.slug` | Slug | Слаг |  |
| `admin.label.text.status` | Holat | Абалы |  |
| `admin.label.text.name` | Nomi | Аталышы |  |
| `admin.label.text.kind` | Turi | Түрү |  |
| `admin.label.text.language` | Til | Тили |  |
| `admin.label.flag.published` | Nashr qilingan | Жарыяланган |  |
| `admin.label.text.description` | Tavsif | Сүрөттөмө |  |
| `admin.label.text.comment` | Izoh | Комментарий |  |
| `admin.label.text.code` | Kod | Код |  |
| `admin.label.flag.open` | Ochiq | Ачык |  |
| `admin.label.text.deadline` | Muddat | Мөөнөт |  |
| `admin.label.text.date` | Sana | Күнү |  |
| `admin.label.misc.questions` | Savollar | Суроолор |  |
| `admin.label.misc.topics` | Mavzular | Темалар |  |
| `admin.label.misc.problems` | Masalalar | Маселелер |  |
| `admin.label.text.author` | Muallif | Автору |  |
| `admin.label.text.flag` | Flag | Желекче |  |
| `admin.label.text.type` | Tur | Түрү |  |
| `admin.label.text.category` | Kategoriya | Категория |  |
| `admin.label.text.module` | Modul | Модуль |  |
| `admin.label.flag.staff` | Xodim | Кызматкер |  |
| `admin.label.text.article` | Maqola | Макала |  |
| `admin.label.text.opponent` | Raqib | Атаандаш |  |
| `admin.label.text.result` | Natija | Натыйжа |  |
| `admin.label.text.end` | Yakun | Аякталышы |  |
| `admin.label.misc.votes` | Ovoz | Добуштар |  |
| `admin.label.text.message` | Xabar | Билдирүү |  |
| `admin.label.text.checker` | Checker | Чекер |  |
| `admin.label.text.standard` | Standart | Стандарттык |  |
| `admin.label.text.special` | Maxsus | Атайын |  |
| `admin.label.text.interactive` | Interactive | Интерактивдүү |  |
| `admin.label.text.source` | Manba | Булак |  |
| `admin.label.misc.tests` | Testlar | Тесттер |  |
| `admin.label.text.reward` | Mukofot | Сыйлык |  |
| `admin.label.text.qvant` | Qvant | Квант |  |
| `admin.label.text.problem` | Masala | Маселе |  |
| `admin.label.text.reason` | Sabab | Себеби |  |
| `admin.label.text.who` | Kim | Ким |  |
| `admin.label.text.order` | Tartib | Тартиби |  |
| `admin.label.misc.steps` | Qadamlar | Кадамдар |  |
| `admin.label.text.price` | Narx | Баасы |  |
| `admin.label.misc.owners` | Egalari | Ээлери |  |
| `admin.label.text.asset` | Asset | Ассет |  |
| `admin.label.misc.stages` | Bosqichlar | Баскычтар |  |
| `admin.label.text.version` | Versiya | Версиясы |  |
| `admin.label.text.repo` | Repo | Репозиторий |  |
| `admin.label.text.username` | Login | Логин |  |
| `admin.label.text.displayName` | Ism | Аты |  |
| `admin.label.text.email` | Email | Почта |  |
| `admin.label.misc.ratings` | Reytinglar | Рейтингдер |  |
| `admin.label.text.bio` | Bio | Өзү жөнүндө |  |
| `admin.label.duration.perQuestion` | s/savol | с/суроо |  |
| `admin.label.text.num` | # | # |  |
| `admin.label.text.acmIcpc` | ACM/ICPC | ACM/ICPC |  |
| `admin.label.text.ioi` | IOI | IOI |  |
| `admin.label.lang.uz` | uz | uz |  |
| `admin.label.lang.ru` | ru | ru |  |
| `admin.label.lang.en` | en | en |  |
| `admin.help.topicsSlug` | Topic sluglari, vergul bilan | Тема слагтары, үтүр менен |  |
| `admin.help.freezeStandings` | Oxirgi N daqiqada standings yangilanmaydi | Акыркы N мүнөттө таблица жаңыртылбайт |  |
| `admin.help.submissionClose` | Shu vaqtdan keyin topshirish yopiladi va loyihalar hammaga ochiladi | Бул убакыттан кийин тапшыруу жабылат, долбоорлор баарына ачылат |  |
| `admin.help.rulesAndPrizes` | Shartlar, mezonlar, sovrin | Шарттар, критерийлер, байгелер |  |
| `admin.help.targetQuarter` | Chorak darajasida (2026-Q4). ANIQ SANA YOZILMAYDI — bajarilmasa ishonch buziladi | Чейрек деңгээлинде (2026-Q4). ТАК КҮН ЖАЗЫЛБАЙТ — аткарылбаса ишеним бузулат |  |
| `admin.help.changelogId` | Chiqarilganda bog'lanadigan yozuv raqami. Batafsil sahifada havola bo'ladi | Чыгарылыш байланышкан жазуу номери. Толук бетте шилтеме болот |  |
| `admin.help.softDelete` | O'chirilsa band ko'rinmaydi, lekin ovozlari bilan bazada qoladi | Өчүрүлсө жазуу көрүнбөйт, бирок добуштары менен базада калат |  |
| `admin.help.autoPublishAt` | Bo'sh qolsa — birinchi nashrda avtomatik qo'yiladi | Бош калса — биринчи жарыялоодо автоматтык коюлат |  |
| `admin.help.notifyOnce` | Nashrdan keyin barcha foydalanuvchiga bir marta bildirishnoma yuboriladi | Жарыялангандан кийин бардык колдонуучуга бир жолу билдирүү жөнөтүлөт |  |
| `admin.help.inputFormatSection` | Sahifada alohida bo'lim bo'lib chiqadi | Баракта өзүнчө бөлүм болуп чыгат |  |
| `admin.help.noteExplainsSamples` | Namunalar nega shunday ekanini tushuntiradi | Мисалдардын эмне үчүн мындай экенин түшүндүрөт |  |
| `admin.help.editorialFreeForSolvers` | Masalani yechgan bepul ko'radi (ADR-0013) | Маселени чечкендерге акысыз (ADR-0013) |  |
| `admin.help.editorialPrice` | Yechmaganlar uchun. 0 — hammaga bepul | Чечпегендер үчүн. 0 — баарына акысыз |  |
| `admin.help.interactorOnlyInteractive` | Faqat Interactive uchun. Bo'sh = yo'q | Interactive үчүн гана. Бош = жок |  |
| `admin.help.checkerRequired` | Maxsus va Skoring uchun. Bo'sh bo'lsa har yuborish IE bo'ladi | «Атайын» жана «Скоринг» үчүн. Бош болсо, ар бир жөнөтүү IE болот |  |
| `admin.help.testlibInvocation` | testlib chaqiruvi: checker <input> <output> <answer> | testlib чакыруусу: checker <input> <output> <answer> |  |
| `admin.help.parentEmptyRoot` | Bo'sh = ildiz | Бош = тамыр |  |
| `admin.help.questCodeMatch` | Hodisaga bog'lanish uchun qvant/quests.py dagi kod bilan mos bo'lishi kerak | Окуяны байлоо үчүн qvant/quests.py коду менен дал келиши керек |  |
| `admin.help.cosmeticOnly` | ADR-0002: v1 da faqat kosmetika va qulaylik | ADR-0002: v1де косметика жана ыңгайлуулук гана |  |
| `admin.help.assetRef` | Ramka/cover fayliga havola yoki kalit | Алкак/мукаба файлына шилтеме же ачкычы |  |
| `admin.help.repeatPerItem` | Streak freeze — ha, ramka — yo'q | Streak freeze — ооба, алкак — жок |  |
| `admin.help.publishedAtAuto` | «Nashrda» qilib qo'yilsa `published_at` avtomatik yoziladi | «Жарыяланган» койсо, `published_at` автоматтык жазылат |  |
| `admin.help.releasedAtReal` | O'zgarishning HAQIQIY sanasi — yozuv kechroq yozilishi mumkin | Өзгөрүүнүн ТАК күнү — жазуу кечирээк жазылышы мүмкүн |  |
| `admin.help.versionOptional` | Ixtiyoriy, v1.4.0 | Милдеттүү эмес, v1.4.0 |  |
| `admin.help.refsFormat` | Commit SHA, PR raqami, release tegi — vergul bilan | Commit SHA, PR номери, release теги — үтүр менен |  |
| `admin.help.screenshotWhenNeeded` | Faqat kerak bo'lganda — dizayn o'zgarishlari uchun skrinshot | Керек болгондо гана — дизайн өзгөрүүлөрү үчүн скриншот |  |
| `admin.help.staffOnlySuperuser` | Faqat superuser o'zgartira oladi. O'z hisobingizni o'zgartira olmaysiz. | Суперколдонуучу гана өзгөртө алат. Өз каттоо эсебиңизди өзгөртө албайсыз. |  |
| `admin.help.languageCodes` | uz / ru / en | uz / ru / en |  |
| `admin.help.zeroAuto` | 0 = avtomatik | 0 = автоматтык |  |
| `admin.help.upTo300Chars` | 300 belgigacha | 300 белгиге чейин |  |
| `admin.help.twoLetterDefaultUz` | 2 harf, standart: uz | 2 тамга, демейки: uz |  |
| `admin.help.ownerRepo` | owner/repo | ээси/репозиторий |  |
| `admin.text.eventFormStarted` | Forma boshlandi | Форма башталды |  |
| `admin.text.eventRegisterDone` | Ro'yxatdan o'tdi | Катталды |  |
| `admin.text.eventSessions` | {name}: {sessions} sessiya, {share}% | {name}: {sessions} сессия, {share}% |  |
| `admin.text.funnelDay` | {date}: {started} boshlandi, {done} tugadi | {date}: {started} баштады, {done} бүтүрдү |  |
| `admin.text.reasonLoginTaken` | Login band | Логин бош эмес |  |
| `admin.text.reasonPasswordMismatch` | Parollar mos emas | Сырсөздөр дал келбейт |  |
| `admin.text.reasonTermsNotAccepted` | Shartlarga rozilik berilmagan | Шарттар кабыл алынбаган |  |
| `admin.text.reasonEmailTaken` | Email band yoki noto'g'ri | Почта бош эмес же ката |  |
| `admin.text.reasonServerError` | Server xatosi | Сервер катасы |  |
| `admin.text.reasonNetworkError` | Tarmoq xatosi | Тармак катасы |  |
| `admin.text.reasonUnknown` | Sababsiz | Себепсиз |  |
| `admin.text.reportReasonStatement` | Matnda xato | Текстте ката |  |
| `admin.text.reportReasonTests` | Testlar noto'g'ri | Тесттер туура эмес |  |
| `admin.text.reportReasonTranslation` | Tarjima xato | Котормо ката |  |
| `admin.text.reportReasonDuplicate` | Takroriy masala | Кайталанган маселе |  |
| `admin.text.reportReasonOther` | Boshqa | Башка |  |
| `admin.label.status.draft` | Qoralama | Долбоор |  |
| `admin.label.status.published` | Nashrda | Жарыяланган |  |
| `admin.label.status.withdrawn` | Nashrdan olingan | Жарыялоодон алынды |  |
| `admin.label.status.rejectedShort` | Rad etildi | Четке кагылды |  |
| `admin.text.error` | Xato | Ката |  |
| `admin.text.unpublish` | Nashrdan olish | Жарыялоодон алуу |  |
| `admin.text.publishVerb` | Nashr qilish | Жарыялоо |  |
| `admin.label.misc.questDaily` | Kunlik | Күнүмдүк |  |
| `admin.label.misc.questWeekly` | Haftalik | Жумалык |  |
| `admin.label.misc.questAchievement` | Yutuq | Жетишкендик |  |
| `admin.label.shopCategory.streakFreeze` | Streak freeze | Серияны тоңдуруу |  |
| `admin.label.shopCategory.avatarFrame` | Avatar ramka | Аватар алкагы |  |
| `admin.label.shopCategory.profileCover` | Profil cover | Профиль мукабасы |  |
| `admin.label.shopCategory.usernameBadge` | Username badge | Логин белгиси |  |
| `admin.title.order` | Tartib | Тартиби |  |
| `admin.title.signupFunnel` | Ro'yxatdan o'tish voronkasi | Каттоо воронкасы |  |
| `admin.title.abRegion` | A/B: viloyat qachon so'raladi | A/B: облус качан суралат |  |
| `admin.title.total` | Jami | Бардыгы |  |
| `admin.title.errorReasons` | Xato sabablari | Ката себептери |  |
| `admin.title.languages` | Tillar | Тилдер |  |
| `admin.title.countries` | Mamlakatlar | Өлкөлөр |  |
| `admin.title.daily` | Kunlik | Күнүмдүк |  |
| `admin.title.points` | Ball | Упайлар |  |
| `admin.title.duels` | Duellar | Дуэлдер |  |
| `admin.title.hackathons` | Hakatonlar | Хакатондар |  |
| `admin.title.topics` | Mavzular | Темалар |  |
| `admin.title.moveUp` | Yuqoriga | Жогору |  |
| `admin.title.moveDown` | Pastga | Төмөн |  |
| `admin.title.remove` | Olib tashlash | Алып салуу |  |
| `admin.title.roadmapComments` | Yo'l xaritasi izohlari | Жол картасы комментарийлери |  |
| `admin.title.tournaments` | Chempionatlar | Чемпионаттар |  |
| `admin.title.broadcast` | Umumiy e'lon | Жалпы жарыя |  |
| `admin.title.page` | Admin | Админ |  |
| `admin.placeholder.questionId` | Savol ID | Суроо ID |  |
| `admin.placeholder.problemSlug` | masala slug'i | маселе слагы |  |
| `admin.placeholder.title` | Sarlavha | Аталыш |  |
| `admin.placeholder.comment` | Fikr | Пикир |  |
| `admin.placeholder.articleSlug` | maqola slugi | макала слагы |  |
| `admin.placeholder.amount` | ±miqdor | ±сумма |  |
| `admin.placeholder.ledgerComment` | Izoh (ledgerga yoziladi) | Комментарий (журналга жазылат) |  |
| `admin.placeholder.text` | Matn | Текст |  |
| `admin.placeholder.textOptional` | Matn (ixtiyoriy) | Текст (милдеттүү эмес) |  |
| `admin.text.badgeActive` | faol | активдүү |  |
| `admin.text.badgeBlocked` | bloklangan | бөгөттөлгөн |  |
| `admin.text.badgeSuperuser` | superuser | суперколдонуучу |  |
| `admin.text.badgeStaff` | xodim | кызматкер |  |
| `admin.text.badgeHidden` | yashirin | жашыруун |  |
| `admin.text.badgeRewarded` | mukofotlangan | сыйланган |  |
| `admin.text.badgeLive` | jonli | түз эфирде |  |
| `admin.text.badgeFinished` | tugagan | бүткөн |  |
| `admin.text.badgeRated` | reytingli | рейтингдик |  |
| `admin.text.badgeClosed` | yopiq | жабык |  |
| `admin.text.badgeCompleted` | yakunlangan | аякталган |  |
| `admin.text.badgeRepo` | repo | репозиторий |  |
| `admin.text.badgeDemo` | demo | демо |  |
| `admin.text.badgeSample` | namuna | үлгү |  |
| `admin.text.badgeOptional` | ixtiyoriy | милдеттүү эмес |  |
| `admin.text.addProblem` | + Masala | + Маселе |  |
| `admin.text.addVariant` | + Variant | + Вариант |  |
| `admin.text.addStep` | + Qadam | + Кадам |  |
| `admin.text.addStage` | + Bosqich | + Баскыч |  |
| `admin.text.reschedule` | Qayta rejalashtirish | Кайра пландоо |  |
| `admin.text.rebuildStandings` | Standings qayta qurish | Таблицаны кайра куруу |  |
| `admin.text.recalcTable` | Jadvalni qayta hisoblash | Таблицаны кайра эсептөө |  |
| `admin.text.restoreCatalog` | Katalogni tiklash | Каталогду калыбына келтирүү |  |
| `admin.text.sendToAll` | Hammaga yuborish | Баарына жөнөтүү |  |
| `admin.text.cancel` | Bekor qilish | Жокко чыгаруу |  |
| `admin.text.loading` | yuklanmoqda… | жүктөлүүдө… |  |
| `admin.text.orderNumber` | Tartib raqami * | Тартип номери * |  |
| `admin.text.contestSlug` | Contest slug | Контест слагы |  |
| `admin.text.noErrors` | Xato qayd etilmagan. | Ката катталган эмес. |  |
| `admin.text.highSkipRate` | Bu raqam yuqori bo'lsa, 2-qadam odamni charchatyapti. | Бул сан жогору болсо, 2-кадам адамды чарчатат. |  |
| `admin.text.dailyLegend` | Kulrang — boshlangan, rangli — tugagan. Har ustun bir kun. | Боз — баштады, түстүү — бүтүрдү. Ар бир мамыча — бир күн. |  |
| `admin.text.publish` | Nashr | Жарыялоо |  |
| `admin.text.finish` | Yakunlash | Аяктоо |  |
| `admin.text.rollback` | Qaytarish | Кайтаруу |  |
| `admin.text.hidden` | Yashirilgan | Жашырылган |  |
| `admin.text.deleteRollback` | O'chirish (rollback) | Жок кылуу (кайтаруу) |  |
| `admin.text.ratingsAppliedAt` | Yakunlangan: {date} | Аякталды: {date} |  |
| `admin.text.draw` | Durang ({score}) | Тең ({score}) |  |
| `admin.text.add` | Qo'shish | Кошуу |  |
| `admin.text.apply` | Qo'llash | Колдонуу |  |
| `admin.text.linkedProblems` | Bog'langan masalalar | Байланган маселелер |  |
| `admin.text.questionsInOrder` | Savollar (tartib bo'yicha) | Суроолор (тартиби менен) |  |
| `admin.text.mirrorOf` | ko'zgu: {slug} | күзгү: {slug} |  |
| `admin.text.variant` | Variant {order} | Вариант {order} |  |
| `admin.text.noStages` | Bosqichlar yo'q — contest qo'shing. | Баскычтар жок — контест кошуңуз. |  |
| `admin.text.forceFinish` | Majburan yakunlash | Мажбурлап аяктоо |  |
| `admin.text.no` | yo'q | жок |  |
| `admin.text.disabled` | O'chirilgan | Өчүрүлгөн |  |
| `admin.text.off` | O'chiq | Өчүк |  |
| `admin.text.enable` | Yoqish | Күйгүзүү |  |
| `admin.text.hide` | Yashirish | Жашыруу |  |
| `admin.text.visible` | Ko'rinadi | Көрүнөт |  |
| `admin.text.tableRecalculated` | Jadval qayta hisoblandi — ishtirokchilar: {count} | Таблица кайра эсептелди — катышуучулар: {count} |  |
| `admin.text.yes` | ha | ооба |  |
| `admin.text.badgePublic` | ommaviy | ачык |  |
| `admin.text.noEventsInWindow` | Bu oynada hodisa yo'q. Funnel ro'yxatdan o'tish va kirish sahifalarida yig'iladi — trafik bo'lsa paydo bo'ladi. | Бул терезеде окуя жок. Воронка каттоо жана кирүү барактарында жыйналат — трафик болсо пайда болот. |  |
| `admin.text.funnelNote` | Foizlar birinchi qadamga nisbatan. Sessiya bo'yicha sanaladi — bir odam bir marta hisoblanadi. | Пайыздар биринчи кадамга салыштырмалуу. Сессия боюнча саналат — бир адам бир жолу эсептелет. |  |
| `admin.text.noSignupYet` | Hali tugagan ro'yxatdan o'tish yo'q. Guruh cookie'da saqlanadi va har bir hodisa bilan birga yuboriladi. | Азырынча аякталган каттоо жок. Топ cookieде сакталат жана ар бир окуя менен жөнөтүлөт. |  |
| `admin.text.skipped` | o'tkazib yubordi | өткөрүп жиберди |  |
| `admin.text.noData` | Ma'lumot yo'q. | Маалымат жок. |  |
| `admin.text.noDataCountries` | Ma'lumot yo'q — mamlakat ro'yxatdan o'tgandan keyin ma'lum bo'ladi. | Маалымат жок — өлкө катталгандан кийин белгилүү болот. |  |
| `admin.help.testsStoredRemotely` | Judge testlarni DB dan emas, S3 dan o'qiydi: matn yuklanganda tests/{slug}/<order>.in/.out sifatida saqlanadi, bu yerda faqat havola ko'rinadi. Bir xil tartib raqami qayta yuklansa — ustiga yoziladi. | Каттоочу тесттерди БДдан эмес, S3тен окуйт: жүктөлгөн текст tests/{slug}/<order>.in/.out түрүндө сакталат, бул жерде шилтеме гана көрүнөт. Ошол номер кайра жүктөлсө — үстүнө жазылат. |  |
| `admin.text.noTestsYet` | Hali test yo'q — yechimlar tekshirilmaydi. | Азырынча тест жок — чечимдер текшерилбейт. |  |
| `admin.text.addTest` | Test qo'shish | Тест кошуу |  |
| `admin.text.step2Funnel` | 2-qadam (joy va maktab) | 2-кадам (орун жана мектеп) |  |
| `admin.text.stepPlaceholder` | 1-bosqich | 1-баскыч |  |
