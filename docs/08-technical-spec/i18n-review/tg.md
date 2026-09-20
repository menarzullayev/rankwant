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

Regenerate with `python tools/export_i18n_review.py --prefix "admin."`.

**353 strings.**

| Key | Uzbek (source) | Tajik | Review |
| --- | --- | --- | --- |
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
| `admin.text.noEventsInWindow` | Bu oynada hodisa yo'q. Funnel ro'yxatdan o'tish va kirish sahifalarida yig'iladi — trafik bo'lsa paydo bo'ladi. | Дар ин тиреза ҳодиса нест. Қиф дар саҳифаҳои сабтином ва воридшавӣ ҷамъ мешавад — бо пайдо шудани трафик пайдо мешавад. |  |
| `admin.text.funnelNote` | Foizlar birinchi qadamga nisbatan. Sessiya bo'yicha sanaladi — bir odam bir marta hisoblanadi. | Фоизҳо нисбат ба қадами аввал. Аз рӯи сессия ҳисоб мешавад — як шахс як бор ҳисоб меёбад. |  |
| `admin.text.noSignupYet` | Hali tugagan ro'yxatdan o'tish yo'q. Guruh cookie'da saqlanadi va har bir hodisa bilan birga yuboriladi. | Ҳанӯз сабтиноми анҷомёфта нест. Гурӯҳ дар cookie нигоҳ дошта мешавад ва бо ҳар ҳодиса фиристода мешавад. |  |
| `admin.text.skipped` | o'tkazib yubordi | гузаштанд |  |
| `admin.text.noData` | Ma'lumot yo'q. | Маълумот нест. |  |
| `admin.text.noDataCountries` | Ma'lumot yo'q — mamlakat ro'yxatdan o'tgandan keyin ma'lum bo'ladi. | Маълумот нест — кишвар баъди сабтином маълум мешавад. |  |
| `admin.help.testsStoredRemotely` | Judge testlarni DB dan emas, S3 dan o'qiydi: matn yuklanganda tests/{slug}/<order>.in/.out sifatida saqlanadi, bu yerda faqat havola ko'rinadi. Bir xil tartib raqami qayta yuklansa — ustiga yoziladi. | Довар тестҳоро аз S3 мехонад, на аз пойгоҳи дода: матни боршуда ҳамчун tests/{slug}/<order>.in/.out нигоҳ дошта мешавад, дар ин ҷо танҳо ҳавола дида мешавад. Ҳамон рақам боз бор шуда, рӯйи он навишта мешавад. |  |
| `admin.text.noTestsYet` | Hali test yo'q — yechimlar tekshirilmaydi. | Ҳанӯз тест нест — ҳалҳо санҷида намешаванд. |  |
| `admin.text.addTest` | Test qo'shish | Илова кардани тест |  |
| `admin.text.step2Funnel` | 2-qadam (joy va maktab) | Қадами 2 (ҷой ва мактаб) |  |
| `admin.text.stepPlaceholder` | 1-bosqich | Марҳилаи 1 |  |
