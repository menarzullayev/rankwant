# Karakalpak (kaa) — translation review

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

| Key | Uzbek (source) | Karakalpak | Review |
| --- | --- | --- | --- |
| `admin.title` | Boshqaruv | Basqarıw |  |
| `admin.create` | Yaratish | Jaratıw |  |
| `admin.edit` | Tahrirlash | Redaktorlaw |  |
| `admin.save` | Saqlash | Saqlaw |  |
| `admin.delete` | O'chirish | Óshiriw |  |
| `admin.cancel` | Bekor | Biykar |  |
| `admin.confirmDelete` | Rostdan o'chirilsinmi? | Rasında óshirilsin be? |  |
| `admin.forbidden` | Bu bo'lim faqat xodimlar uchun. | Bul bólim tek xızmetkerler ushın. |  |
| `admin.search` | Qidirish… | Izlew… |  |
| `admin.noRows` | Hech narsa yo'q | Hesh nárse joq |  |
| `admin.actions` | Amallar | Ámeller |  |
| `admin.saved` | Saqlandi | Saqlandı |  |
| `admin.section.problems` | Masalalar | Máseleler |  |
| `admin.section.reports` | Nuqson xabarlari | Nuqsan xabarları |  |
| `admin.section.contests` | Musobaqalar | Jarıslar |  |
| `admin.section.questions` | Savol banki | Sorawlar banki |  |
| `admin.section.quizzes` | Testlar | Testler |  |
| `admin.section.arena` | Arena | Arena |  |
| `admin.section.tournaments` | Chempionat | Turnirler |  |
| `admin.section.hackathons` | Hakaton | Hakatonlar |  |
| `admin.section.duels` | Duel | Duyeller |  |
| `admin.section.articles` | Maqolalar | Maqalalar |  |
| `admin.section.roadmaps` | Traektoriya | Traektoriya |  |
| `admin.section.posts` | Yangiliklar | Jańalıqlar |  |
| `admin.section.updates` | O'zgarishlar | Ózgerisler |  |
| `admin.section.platformRoadmap` | Yo'l xaritasi | Jol kartası |  |
| `admin.section.roadmapComments` | Reja izohlari | Karta pikirleri |  |
| `admin.section.quests` | Questlar | Kvestler |  |
| `admin.section.shop` | Do'kon | Dúkan |  |
| `admin.section.users` | Foydalanuvchilar | Paydalanıwshılar |  |
| `admin.section.analytics` | Analitika | Analitika |  |
| `admin.section.emailQuota` | Email kvota | Email kvotası |  |
| `admin.quotaProvider` | Provayder | Xızmet |  |
| `admin.quotaSent` | Yuborildi | Jiberildi |  |
| `admin.quotaLimit` | Shift | Sheklew |  |
| `admin.quotaLeft` | Qoldi | Qaldı |  |
| `admin.quotaState` | Holat | Halatı |  |
| `admin.quotaExhausted` | Kvota tugadi | Kvota tawsıldı |  |
| `admin.quotaWarning` | Tugayapti ({percent}%) | Tawsılıp baradı ({percent}%) |  |
| `admin.quotaInQueue` | Kvota tugadi — qolgani navbatda ({n} gacha, kechikish bilan) | Kvota tawsıldı — qalǵanı nawbatta ({n} ǵa shekem, keshigiw menen) |  |
| `admin.quotaLost` | {n} xat yetkazilmaydi (navbat ham to'ldi) | {n} xat jetkerilmeydi (nawbat ta tolı) |  |
| `admin.quotaUnset` | kvota belgilanmagan | kvota belgilenbegen |  |
| `admin.quotaTodayLeft` | Bugun yana: | Búgin qaldı: |  |
| `admin.quotaWindowLabel` | Qaysi kun | Qaysı kún |  |
| `admin.quotaWindowToday` | Bugun | Búgin |  |
| `admin.quotaWindowYesterday` | Kecha | Keshe |  |
| `admin.quotaWindowWeek` | 7 kun | 7 kún |  |
| `admin.quotaSpent` | Shu kun sarfi: | Sol kún sarplanǵanı: |  |
| `admin.quotaWithQueue` | (navbat bilan birga {n} gacha) | (nawbat penen {n} ǵa shekem) |  |
| `admin.quotaFailures` | {n} xat yuborilmadi | {n} xat jiberilmadi |  |
| `admin.quotaUtcNote` | Kun chegarasi — UTC kalendar kuni (Resend va Brevo shunday belgilaydi). Navbatdagi xat yo'qolmaydi, lekin kechikadi. | Shegara — UTC kún. Nawbattaǵı xat joǵalmaydı, biraq keshigedi. |  |
| `admin.quotaLoadFail` | Kvota ma'lumotini yuklab bo'lmadi. | Kvota maǵlıwmatın júklew múmkin bolmadı. |  |
| `admin.label.status.running` | Yurmoqda | Júrmeqte |  |
| `admin.label.status.finished` | Tugagan | Tamamlandı |  |
| `admin.label.status.pending` | Kutilmoqda | Kútilmekte |  |
| `admin.status.sent` | Yuborildi | Jiberildi |  |
| `admin.label.status.evaluating` | Baholanmoqda | Bahalanbaqta |  |
| `admin.label.status.completed` | Yakunlangan | Tamamlanǵan |  |
| `admin.label.status.accepted` | Qabul qilindi | Qabıl etildi |  |
| `admin.label.status.rejected` | Rad etilgan | Rad etildi |  |
| `admin.label.status.cancelled` | Bekor qilindi | Biykar etildi |  |
| `admin.label.status.done` | Tugadi | Tawsıldı |  |
| `admin.label.status.doneShort` | Bajarilgan | Orınlandı |  |
| `admin.label.status.inReview` | Ko'rib chiqilmoqda | Kórip shıǵılmaqta |  |
| `admin.label.status.planned` | Rejalashtirilgan | Jobalandı |  |
| `admin.label.status.inProgress` | Ishlanmoqda | Islenbekte |  |
| `admin.label.status.shipped` | Chiqarildi | Shıǵarıldı |  |
| `admin.label.status.enabled` | Yoqilgan | Qosılǵan |  |
| `admin.label.status.busy` | Band | Bánt |  |
| `admin.label.date.start` | Boshlanish | Baslanıwı |  |
| `admin.label.date.startAt` | Boshlanish vaqti | Baslanıw waqtı |  |
| `admin.label.date.end` | Tugash | Tawsılıwı |  |
| `admin.label.date.deadline` | Topshirish muddati | Tapsırıw múddeti |  |
| `admin.label.date.publishedAt` | Nashr sanasi | Járiyalanǵan kúni |  |
| `admin.label.date.releasedAt` | Chiqarilgan sana | Shıǵarılǵan kúni |  |
| `admin.label.date.joined` | Qo'shilgan | Qosıldı |  |
| `admin.label.duration.freezeMin` | Muzlatish (daqiqa) | Muzlatıw (minut) |  |
| `admin.label.duration.secondsPerQuestion` | Savol uchun soniya | Sorawǵa sekund |  |
| `admin.label.duration.readMin` | O'qish (daqiqa) | Oqıw (minut) |  |
| `admin.label.flag.public` | Ommaviy | Ommavıy |  |
| `admin.label.flag.rated` | Reytingli | Reytinglik |  |
| `admin.label.flag.virtual` | Virtual | Virtual |  |
| `admin.label.flag.mirror` | Ko'zgu (asl musobaqa slug'i) | Ayna (asıl jarıs slug) |  |
| `admin.label.flag.repeatable` | Takroriy | Tákirarlanıwshı |  |
| `admin.label.flag.repeatPurchase` | Takroriy sotib olinadi | Tákirar satıp alınadı |  |
| `admin.label.flag.submissionsOpen` | Topshirish ochiq | Tapsırıw ashıq |  |
| `admin.label.flag.resultsAnnounced` | Natijalar e'loni | Nátiyjeler járiyalandı |  |
| `admin.label.flag.active` | Faol | Belsendi |  |
| `admin.label.flag.activeHint` | Faol (bloklash uchun olib tashlang) | Belsendi (bloklaw ushın belgini alıp taslań) |  |
| `admin.label.flag.notifyUsers` | Foydalanuvchilarga xabar berish | Paydalanıwshılarǵa xabarlaw |  |
| `admin.label.calc.rating` | Hisoblash | Esaplaw |  |
| `admin.label.value.freeze` | Hisob | Esep |  |
| `admin.label.value.rewardQvant` | Mukofot (Qvant) | Sıylıq (Qvant) |  |
| `admin.label.value.priceQvant` | Narx (Qvant) | Bahası (Qvant) |  |
| `admin.label.value.analysisPriceQvant` | Tahlilni ochish narxi, Qvant | Tahlildi ashıw bahası, Qvant |  |
| `admin.label.value.difficulty` | Qiyinlik | Qıyınlıǵı |  |
| `admin.label.value.difficultyRange` | Qiyinlik (800–3500, qadam 100) | Qıyınlıq (800–3500, qádem 100) |  |
| `admin.label.value.scoring` | Skoring (0–100) | Ball (0–100) |  |
| `admin.label.value.timeLimit` | Vaqt limiti, ms | Waqıt shegi, ms |  |
| `admin.label.value.memoryLimit` | Xotira limiti, KB | Yad shegi, KB |  |
| `admin.label.text.title` | Sarlavha | Ataması |  |
| `admin.label.text.summary` | Qisqacha | Qısqasha |  |
| `admin.label.text.markdown` | Matn (Markdown) | Tekst (Markdown) |  |
| `admin.label.text.markdownLatex` | Matn (Markdown + LaTeX) | Tekst (Markdown + LaTeX) |  |
| `admin.label.text.descriptionMarkdown` | Tavsif (Markdown) | Sıpatlama (Markdown) |  |
| `admin.label.text.statementLatex` | Shart (Markdown + LaTeX) | Shárt (Markdown + LaTeX) |  |
| `admin.label.text.articleExample` | Maqoladagi misol | Maqaladaǵı mısal |  |
| `admin.label.text.editorNote` | Muharrir maqolasi | Redaktor jazbası |  |
| `admin.label.text.editorial` | Yechim tahlili | Tahlil |  |
| `admin.label.text.solutionExplanation` | Yechim tushuntirishi | Sheshim túsindirmesi |  |
| `admin.label.text.problemExample` | Algoritm | Algoritm |  |
| `admin.label.text.problemTraining` | Mashq uchun | Shınıǵıw ushın |  |
| `admin.label.tech.input` | Kiruvchi ma'lumot | Kiriw maǵlıwmatı |  |
| `admin.label.tech.output` | Chiquvchi ma'lumot | Shıǵıw maǵlıwmatı |  |
| `admin.label.tech.topicsSlug` | Mavzular (slug, vergul bilan) | Temalar (slug, útir menen) |  |
| `admin.label.tech.parentTopic` | Ota mavzu (slug) | Ata tema (slug) |  |
| `admin.label.tech.parent` | Ota | Ata |  |
| `admin.label.tech.sourceUrl` | Manba URL | Derek URL |  |
| `admin.label.tech.sourceLinks` | Manba havolalari | Derek siltemeleri |  |
| `admin.label.tech.githubUrl` | GitHub havolasi | GitHub siltemesi |  |
| `admin.label.tech.imageUrl` | Rasm havolasi | Súwret siltemesi |  |
| `admin.label.tech.changelogId` | Changelog yozuvi ID | Changelog jazba ID |  |
| `admin.label.tech.checkerLanguage` | Checker tili (kod, masalan cpp23) | Checker tili (kod, mısalı cpp23) |  |
| `admin.label.tech.checkerSource` | Checker manbasi | Checker manbası |  |
| `admin.label.tech.interactorLanguage` | Interactor tili (kod, masalan cpp23) | Interactor tili (kod, mısalı cpp23) |  |
| `admin.label.tech.interactorSource` | Interactor manbasi | Interactor manbası |  |
| `admin.label.name.uz` | Nomi (uz) | Atı (uz) |  |
| `admin.label.name.ru` | Nomi (ru) | Atı (ru) |  |
| `admin.label.name.en` | Nomi (en) | Atı (en) |  |
| `admin.label.name.translation` | Tarjima | Awılma |  |
| `admin.label.name.language` | Matn tili (uz/ru/en) | Shárt tili (uz/ru/en) |  |
| `admin.label.name.shown` | Ko'rsatiladigan ism | Kórsetiletuǵın atı |  |
| `admin.label.ab.control` | Nazorat (2-qadamda) | Baqlaw (2-qádemde) |  |
| `admin.label.ab.variant` | Variant (ro'yxatda) | Variant (dizimde) |  |
| `admin.label.misc.participant` | Ishtirokchi | Qatnasıwshı |  |
| `admin.label.misc.challenger` | Chaqiruvchi | Shaqırıwshı |  |
| `admin.label.misc.projects` | Loyihalar | Joybarlar |  |
| `admin.label.misc.news` | Yangilik | Jańalıq |  |
| `admin.label.misc.announcement` | E'lon | Járiyalaw |  |
| `admin.label.text.slug` | Slug | Slug |  |
| `admin.label.text.status` | Holat | Halat |  |
| `admin.label.text.name` | Nomi | Atı |  |
| `admin.label.text.kind` | Turi | Túri |  |
| `admin.label.text.language` | Til | Til |  |
| `admin.label.flag.published` | Nashr qilingan | Járiyalanǵan |  |
| `admin.label.text.description` | Tavsif | Sıpatlama |  |
| `admin.label.text.comment` | Izoh | Túsindirme |  |
| `admin.label.text.code` | Kod | Kod |  |
| `admin.label.flag.open` | Ochiq | Ashıq |  |
| `admin.label.text.deadline` | Muddat | Múddet |  |
| `admin.label.text.date` | Sana | Sáne |  |
| `admin.label.misc.questions` | Savollar | Sorawlar |  |
| `admin.label.misc.topics` | Mavzular | Temalar |  |
| `admin.label.misc.problems` | Masalalar | Máseleler |  |
| `admin.label.text.author` | Muallif | Avtor |  |
| `admin.label.text.flag` | Flag | Belgi |  |
| `admin.label.text.type` | Tur | Túr |  |
| `admin.label.text.category` | Kategoriya | Kategoriya |  |
| `admin.label.text.module` | Modul | Modul |  |
| `admin.label.flag.staff` | Xodim | Xızmetker |  |
| `admin.label.text.article` | Maqola | Maqala |  |
| `admin.label.text.opponent` | Raqib | Qarsılas |  |
| `admin.label.text.result` | Natija | Nátiyje |  |
| `admin.label.text.end` | Yakun | Aqırı |  |
| `admin.label.misc.votes` | Ovoz | Dawıslar |  |
| `admin.label.text.message` | Xabar | Xabar |  |
| `admin.label.text.checker` | Checker | Checker |  |
| `admin.label.text.standard` | Standart | Standart |  |
| `admin.label.text.special` | Maxsus | Arnawlı |  |
| `admin.label.text.interactive` | Interactive | Interaktiv |  |
| `admin.label.text.source` | Manba | Derek |  |
| `admin.label.misc.tests` | Testlar | Testler |  |
| `admin.label.text.reward` | Mukofot | Sıylıq |  |
| `admin.label.text.qvant` | Qvant | Qvant |  |
| `admin.label.text.problem` | Masala | Másele |  |
| `admin.label.text.reason` | Sabab | Sebebi |  |
| `admin.label.text.who` | Kim | Kim |  |
| `admin.label.text.order` | Tartib | Tártip |  |
| `admin.label.misc.steps` | Qadamlar | Qádemler |  |
| `admin.label.text.price` | Narx | Bahası |  |
| `admin.label.misc.owners` | Egalari | İyeleri |  |
| `admin.label.text.asset` | Asset | Asset |  |
| `admin.label.misc.stages` | Bosqichlar | Basqıshlar |  |
| `admin.label.text.version` | Versiya | Versiya |  |
| `admin.label.text.repo` | Repo | Repo |  |
| `admin.label.text.username` | Login | Login |  |
| `admin.label.text.displayName` | Ism | Atı |  |
| `admin.label.text.email` | Email | Email |  |
| `admin.label.misc.ratings` | Reytinglar | Reytingler |  |
| `admin.label.text.bio` | Bio | Bio |  |
| `admin.label.duration.perQuestion` | s/savol | s/soraw |  |
| `admin.label.text.num` | # | # |  |
| `admin.label.text.acmIcpc` | ACM/ICPC | ACM/ICPC |  |
| `admin.label.text.ioi` | IOI | IOI |  |
| `admin.label.lang.uz` | uz | uz |  |
| `admin.label.lang.ru` | ru | ru |  |
| `admin.label.lang.en` | en | en |  |
| `admin.help.topicsSlug` | Topic sluglari, vergul bilan | Tema slugları, vergul menen |  |
| `admin.help.freezeStandings` | Oxirgi N daqiqada standings yangilanmaydi | Aqırǵı N minutta keste jańalanbaydı |  |
| `admin.help.submissionClose` | Shu vaqtdan keyin topshirish yopiladi va loyihalar hammaga ochiladi | Bul waqıttan keyin tapsırıw jabıladı hám joybarlar hámmege ashıladı |  |
| `admin.help.rulesAndPrizes` | Shartlar, mezonlar, sovrin | Shártler, kriteriyalar, sıylıqlar |  |
| `admin.help.targetQuarter` | Chorak darajasida (2026-Q4). ANIQ SANA YOZILMAYDI — bajarilmasa ishonch buziladi | Sherek dárejesinde (2026-Q4). ANIQ SÁNE JAZILMAYDI — orınlanbasa isenim buzıladı |  |
| `admin.help.changelogId` | Chiqarilganda bog'lanadigan yozuv raqami. Batafsil sahifada havola bo'ladi | Shıǵarılıw baylanısatın jazıw nomeri. Tolıq bette silteme boladı |  |
| `admin.help.softDelete` | O'chirilsa band ko'rinmaydi, lekin ovozlari bilan bazada qoladi | Óshirilse bánt kórinbeydi, biraq dawısları menen bazada qaladı |  |
| `admin.help.autoPublishAt` | Bo'sh qolsa — birinchi nashrda avtomatik qo'yiladi | Bos qalsa — birinshi járiyalawda avtomat túrde qoyıladı |  |
| `admin.help.notifyOnce` | Nashrdan keyin barcha foydalanuvchiga bir marta bildirishnoma yuboriladi | Járiyalaǵannan keyin barlıq paydalanıwshıǵa bir márte bildiriw jiberiledi |  |
| `admin.help.inputFormatSection` | Sahifada alohida bo'lim bo'lib chiqadi | Bette bólek bólim bolıp shıǵadı |  |
| `admin.help.noteExplainsSamples` | Namunalar nega shunday ekanini tushuntiradi | Mısallardıń nege bunday ekenin túsindiredi |  |
| `admin.help.editorialFreeForSolvers` | Masalani yechgan bepul ko'radi (ADR-0013) | Máseleni sheshkenlerge tegin (ADR-0013) |  |
| `admin.help.editorialPrice` | Yechmaganlar uchun. 0 — hammaga bepul | Sheshpegenler ushın. 0 — hámmege tegin |  |
| `admin.help.interactorOnlyInteractive` | Faqat Interactive uchun. Bo'sh = yo'q | Tek Interactive ushın. Bos = joq |  |
| `admin.help.checkerRequired` | Maxsus va Skoring uchun. Bo'sh bo'lsa har yuborish IE bo'ladi | «Arnawlı» hám «Skoring» ushın. Bos bolsa, hár jiberiw IE boladı |  |
| `admin.help.testlibInvocation` | testlib chaqiruvi: checker <input> <output> <answer> | testlib shaqırıwı: checker <input> <output> <answer> |  |
| `admin.help.parentEmptyRoot` | Bo'sh = ildiz | Bos = tamır |  |
| `admin.help.questCodeMatch` | Hodisaga bog'lanish uchun qvant/quests.py dagi kod bilan mos bo'lishi kerak | Waqıyanı baylaw ushın qvant/quests.py dagi kod menen sáykes keliwi kerek |  |
| `admin.help.cosmeticOnly` | ADR-0002: v1 da faqat kosmetika va qulaylik | ADR-0002: v1 de tek kosmetika hám qolaylıq |  |
| `admin.help.assetRef` | Ramka/cover fayliga havola yoki kalit | Ramka/muqaba faylına silteme yamasa onıń gilti |  |
| `admin.help.repeatPerItem` | Streak freeze — ha, ramka — yo'q | Streak freeze — awa, ramka — joq |  |
| `admin.help.publishedAtAuto` | «Nashrda» qilib qo'yilsa `published_at` avtomatik yoziladi | «Járiyalanǵan» etip qoyılsa, `published_at` avtomat jazıladı |  |
| `admin.help.releasedAtReal` | O'zgarishning HAQIQIY sanasi — yozuv kechroq yozilishi mumkin | Ózgeristiń HAQIQIY sánesi — jazıw keshirek jazılıwı múmkin |  |
| `admin.help.versionOptional` | Ixtiyoriy, v1.4.0 | Miltetsiz, v1.4.0 |  |
| `admin.help.refsFormat` | Commit SHA, PR raqami, release tegi — vergul bilan | Commit SHA, PR nomeri, release tegi — vergul menen |  |
| `admin.help.screenshotWhenNeeded` | Faqat kerak bo'lganda — dizayn o'zgarishlari uchun skrinshot | Tek kerek bolǵanda — dizayn ózgerisleri ushın skrinshot |  |
| `admin.help.staffOnlySuperuser` | Faqat superuser o'zgartira oladi. O'z hisobingizni o'zgartira olmaysiz. | Tek superpaydalanıwshı ózgertire aladı. Óz esabıńızdı ózgertire almaysız. |  |
| `admin.help.languageCodes` | uz / ru / en | uz / ru / en |  |
| `admin.help.zeroAuto` | 0 = avtomatik | 0 = avtomat |  |
| `admin.help.upTo300Chars` | 300 belgigacha | 300 belgige shekem |  |
| `admin.help.twoLetterDefaultUz` | 2 harf, standart: uz | 2 hárip, standart: uz |  |
| `admin.help.ownerRepo` | owner/repo | iyesi/repozitoriy |  |
| `admin.text.eventFormStarted` | Forma boshlandi | Forma baslandı |  |
| `admin.text.eventRegisterDone` | Ro'yxatdan o'tdi | Dizimnen ótti |  |
| `admin.text.eventSessions` | {name}: {sessions} sessiya, {share}% | {name}: {sessions} sessiya, {share}% |  |
| `admin.text.funnelDay` | {date}: {started} boshlandi, {done} tugadi | {date}: {started} basladı, {done} tamamladı |  |
| `admin.text.reasonLoginTaken` | Login band | Login bánt |  |
| `admin.text.reasonPasswordMismatch` | Parollar mos emas | Parollar sáykes emes |  |
| `admin.text.reasonTermsNotAccepted` | Shartlarga rozilik berilmagan | Shártler qabıl etilmegen |  |
| `admin.text.reasonEmailTaken` | Email band yoki noto'g'ri | Email bánt yamasa nadurıs |  |
| `admin.text.reasonServerError` | Server xatosi | Server qáteligi |  |
| `admin.text.reasonNetworkError` | Tarmoq xatosi | Tarmaq qáteligi |  |
| `admin.text.reasonUnknown` | Sababsiz | Sebepsiz |  |
| `admin.text.reportReasonStatement` | Matnda xato | Mátnde qáte |  |
| `admin.text.reportReasonTests` | Testlar noto'g'ri | Testler nadurıs |  |
| `admin.text.reportReasonTranslation` | Tarjima xato | Awdarma qáte |  |
| `admin.text.reportReasonDuplicate` | Takroriy masala | Tákirarlanatuǵın másele |  |
| `admin.text.reportReasonOther` | Boshqa | Basqa |  |
| `admin.label.status.draft` | Qoralama | Qaralama |  |
| `admin.label.status.published` | Nashrda | Járiyada |  |
| `admin.label.status.withdrawn` | Nashrdan olingan | Járiyadan alınǵan |  |
| `admin.label.status.rejectedShort` | Rad etildi | Rad etildi |  |
| `admin.text.error` | Xato | Qáte |  |
| `admin.text.unpublish` | Nashrdan olish | Járiyadan alıw |  |
| `admin.text.publishVerb` | Nashr qilish | Járiyalaw |  |
| `admin.label.misc.questDaily` | Kunlik | Kúnlik |  |
| `admin.label.misc.questWeekly` | Haftalik | Háptelik |  |
| `admin.label.misc.questAchievement` | Yutuq | Jetiskenlik |  |
| `admin.label.shopCategory.streakFreeze` | Streak freeze | Seriyanı muzlatıw |  |
| `admin.label.shopCategory.avatarFrame` | Avatar ramka | Avatar ramkası |  |
| `admin.label.shopCategory.profileCover` | Profil cover | Profil muqabası |  |
| `admin.label.shopCategory.usernameBadge` | Username badge | Login belgisi |  |
| `admin.title.order` | Tartib | Tártip |  |
| `admin.title.signupFunnel` | Ro'yxatdan o'tish voronkasi | Dizimnen ótiw woronkası |  |
| `admin.title.abRegion` | A/B: viloyat qachon so'raladi | A/B: wálayat qashan soraladı |  |
| `admin.title.total` | Jami | Jámi |  |
| `admin.title.errorReasons` | Xato sabablari | Qátelik sebebleri |  |
| `admin.title.languages` | Tillar | Tiller |  |
| `admin.title.countries` | Mamlakatlar | Mámleketler |  |
| `admin.title.daily` | Kunlik | Kúnlik |  |
| `admin.title.points` | Ball | Ballar |  |
| `admin.title.duels` | Duellar | Duellar |  |
| `admin.title.hackathons` | Hakatonlar | Hakatonlar |  |
| `admin.title.topics` | Mavzular | Temalar |  |
| `admin.title.moveUp` | Yuqoriga | Joqarıǵa |  |
| `admin.title.moveDown` | Pastga | Tómenge |  |
| `admin.title.remove` | Olib tashlash | Alıp taslaw |  |
| `admin.title.roadmapComments` | Yo'l xaritasi izohlari | Jol kartası túsindirmeleri |  |
| `admin.title.tournaments` | Chempionatlar | Chempionatlar |  |
| `admin.title.broadcast` | Umumiy e'lon | Ulıwma xabarlama |  |
| `admin.title.page` | Admin | Administrator |  |
| `admin.placeholder.questionId` | Savol ID | Soraw ID |  |
| `admin.placeholder.problemSlug` | masala slug'i | másele slugı |  |
| `admin.placeholder.title` | Sarlavha | Sarlawha |  |
| `admin.placeholder.comment` | Fikr | Pikir |  |
| `admin.placeholder.articleSlug` | maqola slugi | maqala slugı |  |
| `admin.placeholder.amount` | ±miqdor | ±muǵdar |  |
| `admin.placeholder.ledgerComment` | Izoh (ledgerga yoziladi) | Túsindirme (jurnalǵa jazıladı) |  |
| `admin.placeholder.text` | Matn | Mátn |  |
| `admin.placeholder.textOptional` | Matn (ixtiyoriy) | Mátn (miltetsiz) |  |
| `admin.text.badgeActive` | faol | belendi |  |
| `admin.text.badgeBlocked` | bloklangan | bloklanǵan |  |
| `admin.text.badgeSuperuser` | superuser | superpaydalanıwshı |  |
| `admin.text.badgeStaff` | xodim | xızmetker |  |
| `admin.text.badgeHidden` | yashirin | jasırın |  |
| `admin.text.badgeRewarded` | mukofotlangan | sıylıqlanǵan |  |
| `admin.text.badgeLive` | jonli | tikeley |  |
| `admin.text.badgeFinished` | tugagan | tamamlanǵan |  |
| `admin.text.badgeRated` | reytingli | reytingli |  |
| `admin.text.badgeClosed` | yopiq | jabıq |  |
| `admin.text.badgeCompleted` | yakunlangan | juwmaqlanǵan |  |
| `admin.text.badgeRepo` | repo | repo |  |
| `admin.text.badgeDemo` | demo | demo |  |
| `admin.text.badgeSample` | namuna | úlgi |  |
| `admin.text.badgeOptional` | ixtiyoriy | miltetsiz |  |
| `admin.text.addProblem` | + Masala | + Másele |  |
| `admin.text.addVariant` | + Variant | + Variant |  |
| `admin.text.addStep` | + Qadam | + Qádem |  |
| `admin.text.addStage` | + Bosqich | + Basqısh |  |
| `admin.text.reschedule` | Qayta rejalashtirish | Qayta rejelestiriw |  |
| `admin.text.rebuildStandings` | Standings qayta qurish | Kesteni qayta qurıw |  |
| `admin.text.recalcTable` | Jadvalni qayta hisoblash | Kesteni qayta esaplaw |  |
| `admin.text.restoreCatalog` | Katalogni tiklash | Katalogtı tiklew |  |
| `admin.text.sendToAll` | Hammaga yuborish | Hámmege jiberiw |  |
| `admin.text.cancel` | Bekor qilish | Biykarlaw |  |
| `admin.text.loading` | yuklanmoqda… | júklenip atır… |  |
| `admin.text.orderNumber` | Tartib raqami * | Tártip nomeri * |  |
| `admin.text.contestSlug` | Contest slug | Kontest slugı |  |
| `admin.text.noErrors` | Xato qayd etilmagan. | Qáte jazılmaǵan. |  |
| `admin.text.highSkipRate` | Bu raqam yuqori bo'lsa, 2-qadam odamni charchatyapti. | Bul san joqarı bolsa, 2-qádem adamlardı sharshatadı. |  |
| `admin.text.dailyLegend` | Kulrang — boshlangan, rangli — tugagan. Har ustun bir kun. | Kúlgin — basladı, reńli — tamamladı. Hár baǵana — bir kún. |  |
| `admin.text.publish` | Nashr | Járiyalaw |  |
| `admin.text.finish` | Yakunlash | Tamamlaw |  |
| `admin.text.rollback` | Qaytarish | Qaytarıw |  |
| `admin.text.hidden` | Yashirilgan | Jasırılǵan |  |
| `admin.text.deleteRollback` | O'chirish (rollback) | Óshiriw (qaytarıw) |  |
| `admin.text.ratingsAppliedAt` | Yakunlangan: {date} | Tamamlandı: {date} |  |
| `admin.text.draw` | Durang ({score}) | Teń ({score}) |  |
| `admin.text.add` | Qo'shish | Qosıw |  |
| `admin.text.apply` | Qo'llash | Qollanıw |  |
| `admin.text.linkedProblems` | Bog'langan masalalar | Baylanısqan máseleler |  |
| `admin.text.questionsInOrder` | Savollar (tartib bo'yicha) | Sorawlar (tártip boyınsha) |  |
| `admin.text.mirrorOf` | ko'zgu: {slug} | ayna: {slug} |  |
| `admin.text.variant` | Variant {order} | Variant {order} |  |
| `admin.text.noStages` | Bosqichlar yo'q — contest qo'shing. | Basqıshlar joq — kontest qosıń. |  |
| `admin.text.forceFinish` | Majburan yakunlash | Májbúriy tamamlaw |  |
| `admin.text.no` | yo'q | joq |  |
| `admin.text.disabled` | O'chirilgan | Óshirilgen |  |
| `admin.text.off` | O'chiq | Óshik |  |
| `admin.text.enable` | Yoqish | Qosıw |  |
| `admin.text.hide` | Yashirish | Jasırıw |  |
| `admin.text.visible` | Ko'rinadi | Kórinedi |  |
| `admin.text.tableRecalculated` | Jadval qayta hisoblandi — ishtirokchilar: {count} | Keste qayta esaplandı — qatnasıwshılar: {count} |  |
| `admin.text.yes` | ha | awa |  |
| `admin.text.badgePublic` | ommaviy | ommawiy |  |
| `admin.text.noEventsInWindow` | Bu oynada hodisa yo'q. Funnel ro'yxatdan o'tish va kirish sahifalarida yig'iladi — trafik bo'lsa paydo bo'ladi. | Bul áynada waqıya joq. Woronka dizimnen ótiw hám kiriw betlerinde jıynaladı — trafik bolsa payda boladı. |  |
| `admin.text.funnelNote` | Foizlar birinchi qadamga nisbatan. Sessiya bo'yicha sanaladi — bir odam bir marta hisoblanadi. | Protsentler birinshi qádemge salıstırǵanda. Sessiya boyınsha sanaladı — bir adam bir márte esaplanadı. |  |
| `admin.text.noSignupYet` | Hali tugagan ro'yxatdan o'tish yo'q. Guruh cookie'da saqlanadi va har bir hodisa bilan birga yuboriladi. | Ele juwmaqlanǵan dizimnen ótiw joq. Top cookie de saqlanadı hám hár waqıya menen birge jiberiledi. |  |
| `admin.text.skipped` | o'tkazib yubordi | ótkerip jiberdi |  |
| `admin.text.noData` | Ma'lumot yo'q. | Maǵlıwmat joq. |  |
| `admin.text.noDataCountries` | Ma'lumot yo'q — mamlakat ro'yxatdan o'tgandan keyin ma'lum bo'ladi. | Maǵlıwmat joq — mámleket dizimnen ótkennen keyin belgili boladı. |  |
| `admin.help.testsStoredRemotely` | Judge testlarni DB dan emas, S3 dan o'qiydi: matn yuklanganda tests/{slug}/<order>.in/.out sifatida saqlanadi, bu yerda faqat havola ko'rinadi. Bir xil tartib raqami qayta yuklansa — ustiga yoziladi. | Sudya testlerdi DB den emes, S3 ten oqıydı: júklengen mátn tests/{slug}/<order>.in/.out túrinde saqlanadı, bul jerde tek silteme kórinedi. Sol tártip nomeri qayta júklense — ústine jazıladı. |  |
| `admin.text.noTestsYet` | Hali test yo'q — yechimlar tekshirilmaydi. | Ele test joq — sheshimler tekserilmeydi. |  |
| `admin.text.addTest` | Test qo'shish | Test qosıw |  |
| `admin.text.step2Funnel` | 2-qadam (joy va maktab) | 2-qádem (orın hám mektep) |  |
| `admin.text.stepPlaceholder` | 1-bosqich | 1-basqısh |  |
