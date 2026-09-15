// RankWant — ikonka kalitlari katalogi (V3).
//
// Manba: `appearance-comparison/ICON-INVENTORY.md` (20 kategoriya, ~220 nuqta).
//
// ── Format ─────────────────────────────────────────────────────────────
//
//   "domen.ob'ekt": { d: "qisqa tavsif", c: ["nomzod", ...] }
//
// `d` — o'zbekcha tavsif (hisobot va tekshiruv uchun).
// `c` — nomzod ikonka nomlari, **ustuvorlik tartibida**. Har to'plamda
//       birinchi mavjud nom olinadi, ya'ni ro'yxat "eng yaxshi mos" dan
//       "bo'lmasa shu" ga qarab ketadi.
//
// ── Nega nomzodlar ro'yxati ────────────────────────────────────────────
//
// To'plamlar bir tushunchani har xil nomlaydi: `search` (Lucide) ·
// `magnifying-glass` (Phosphor) · `magnifier` (Tabler). 226 kalit × 9
// to'plam = ~2000 nom — qo'lda yozib bo'lmaydi. Nomzodlar ro'yxati bilan
// skript o'zi hal qiladi va faqat **haqiqiy** yetishmovchiliklar qoladi.
//
// ── Domenlar va qamrov (D20 = ①) ───────────────────────────────────────
//
// O'zgaradi : nav · action · status · ranking · user · contest · content ·
//             notification · shop · markdown · locale · stats · system ·
//             device · empty · error · media
// Qat'iy    : verdict · brand
//
// ⚠️ `brand.*` — dasturlash tillari va ijtimoiy tarmoqlar. Ular **logotip**,
// ya'ni brend belgisi; D20 ① bo'yicha qat'iy. Shuning uchun ular interfeys
// to'plamlariga UMUMAN kirmaydi (Phosphor'da Python logotipi yo'q) va
// Simple Icons'dan olinadi.

export const KEYS = {
  // ═══ 1. Navigatsiya (18) ════════════════════════════════════════════
  "nav.home": { d: "Uy / bosh sahifa", c: ["house", "home", "house-chimney"] },
  "nav.menu": { d: "Menyu (burger)", c: ["menu", "bars-3", "bars", "list", "hamburger"] },
  "nav.close": { d: "Yopish", c: ["x", "x-mark", "x-lg", "close", "xmark", "multiply"] },
  "nav.back": { d: "Orqaga (chapga)", c: ["arrow-left", "chevron-left", "caret-left", "angle-left"] },
  "nav.forward": { d: "Oldinga (o'ngga)", c: ["arrow-right", "chevron-right", "caret-right", "angle-right"] },
  "nav.up": { d: "Yuqoriga (scroll-to-top)", c: ["arrow-up", "arrow-up-right", "chevron-up", "caret-up", "angle-up"] },
  "nav.expandDown": { d: "Pastga ochish", c: ["chevron-down", "arrow-down-s", "caret-down", "angle-down"] },
  "nav.expandUp": { d: "Yuqoriga yig'ish", c: ["chevron-up", "arrow-up-s", "caret-up", "angle-up"] },
  "nav.external": { d: "Tashqi havola", c: ["external-link", "arrow-up-right-from-square", "arrow-top-right-on-square", "external-link-alt", "share-boxed"] },
  "nav.collapse": { d: "Panelni yig'ish", c: ["panel-left-close", "sidebar-simple", "layout-sidebar-left-collapse", "indent-decrease", "chevron-double-left"] },
  "nav.more": { d: "Ko'proq (…)", c: ["ellipsis", "dots-three", "more-horizontal", "ellipsis-horizontal", "more-2"] },
  "nav.grid": { d: "Panjara ko'rinishi", c: ["layout-grid", "squares-four", "grid", "squares-2x2", "grid-fill"] },
  "nav.list": { d: "Ro'yxat ko'rinishi", c: ["list", "list-bullet", "rows", "list-ul", "unordered-list"] },
  "nav.filterPanel": { d: "Filtr panelini ochish", c: ["sliders-horizontal", "funnel", "filter", "options", "filter-list"] },
  "nav.problems": { d: "Masalalar bo'limi", c: ["book-open", "book", "notebook", "file-text", "books"] },
  "nav.leaderboard": { d: "Reyting jadvali", c: ["chart-no-axes-column", "bar-chart", "chart-bar", "ranking", "podium"] },
  "nav.quiz": { d: "Testlar / quiz", c: ["circle-help", "question-mark-circle", "question-circle", "help-circle", "question"] },
  "nav.separator": { d: "Breadcrumb ajratgich", c: ["chevron-right", "caret-right", "angle-right", "arrow-right-s"] },

  // ═══ 2. Tugma va amallar (26) ═══════════════════════════════════════
  "action.search": { d: "Qidiruv", c: ["search", "magnifying-glass", "magnifier"] },
  "action.filter": { d: "Filtr", c: ["funnel", "filter", "filter-list", "line-3"] },
  "action.sortAsc": { d: "O'sish bo'yicha saralash", c: ["arrow-up-narrow-wide", "sort-ascending", "arrow-up-a-z", "sort-up"] },
  "action.sortDesc": { d: "Kamayish bo'yicha saralash", c: ["arrow-down-wide-narrow", "sort-descending", "arrow-down-z-a", "sort-down"] },
  "action.add": { d: "Qo'shish (+)", c: ["plus", "add", "plus-lg"] },
  "action.edit": { d: "Tahrirlash (qalam)", c: ["pencil", "edit", "pen", "pencil-simple", "edit-2"] },
  "action.delete": { d: "O'chirish (savat)", c: ["trash-2", "trash", "delete", "bin", "trash-3"] },
  "action.copy": { d: "Nusxa olish", c: ["copy", "duplicate", "files", "file-copy"] },
  "action.download": { d: "Yuklab olish", c: ["download", "arrow-down-to-line", "download-simple", "arrow-down-tray", "file-download"] },
  "action.upload": { d: "Yuklash", c: ["upload", "arrow-up-from-line", "upload-simple", "arrow-up-tray", "file-upload"] },
  "action.share": { d: "Ulashish", c: ["share-2", "share", "share-network", "share-nodes", "share-3"] },
  "action.print": { d: "Chop etish", c: ["printer", "print"] },
  "action.save": { d: "Saqlash", c: ["save", "floppy-disk", "device-floppy", "bookmark-check"] },
  "action.cancel": { d: "Bekor qilish", c: ["ban", "circle-x", "close-circle", "cancel"] },
  "action.retry": { d: "Qayta urinish", c: ["refresh-cw", "arrow-clockwise", "refresh", "rotate-right", "redo"] },
  "action.eye": { d: "Ko'z (parolni ko'rsatish)", c: ["eye", "eye-open"] },
  "action.eyeOff": { d: "Ko'z yopiq (parolni berkitish)", c: ["eye-off", "eye-closed", "eye-slash", "eye-close"] },
  "action.pin": { d: "Mahkamlash", c: ["pin", "map-pin", "pin-angle", "push-pin"] },
  "action.bookmark": { d: "Belgi (bookmark)", c: ["bookmark", "bookmark-simple", "star", "flag"] },
  "action.sliders": { d: "Sozlash (sliders)", c: ["sliders-horizontal", "sliders", "adjustments-horizontal", "settings-2", "equalizer"] },
  "action.clear": { d: "Tozalash", c: ["x-circle", "circle-x", "close-circle", "eraser"] },
  "action.clipboard": { d: "Nusxa (clipboard)", c: ["clipboard", "clipboard-text", "clipboard-list", "paste"] },
  "action.sound": { d: "Ovoz / tovush", c: ["volume-2", "speaker-high", "volume", "volume-up", "sound"] },
  "action.fullscreen": { d: "To'liq ekran", c: ["maximize", "arrows-out", "fullscreen", "expand", "arrows-maximize"] },
  "action.format": { d: "Formatlash", c: ["wand-2", "magic-wand", "wand", "sparkles", "broom"] },
  "action.help": { d: "Yordam (?)", c: ["circle-help", "question-mark-circle", "help-circle", "question"] },

  // ═══ 3. Status va holat (16) ════════════════════════════════════════
  "status.ok": { d: "Tasdiq / muvaffaqiyat", c: ["circle-check", "checkbox-circle", "check-circle", "check-circle-2", "check"] },
  "status.bad": { d: "Xato", c: ["circle-x", "close-circle", "x-circle", "circle-xmark", "forbid"] },
  "status.warning": { d: "Ogohlantirish", c: ["triangle-alert", "error-warning", "alert-triangle", "alert", "warning"] },
  "status.info": { d: "Ma'lumot", c: ["circle-info", "information", "info-circle", "information-circle", "info"] },
  "status.locked": { d: "Qulf (yopiq)", c: ["lock", "lock-closed", "padlock"] },
  "status.unlocked": { d: "Qulf ochiq", c: ["lock-open", "unlock", "lock-open-1", "padlock-open"] },
  "status.watching": { d: "Kuzatilmoqda", c: ["eye", "eye-open", "binoculars"] },
  "status.clock": { d: "Soat", c: ["clock", "time", "clock-3", "watch"] },
  "status.timer": { d: "Taymer", c: ["timer", "stopwatch", "clock-countdown", "hourglass", "time"] },
  "status.online": { d: "Onlayn (yashil nuqta)", c: ["circle", "circle-fill", "record-fill", "dot"] },
  "status.offline": { d: "Oflayn (qizil nuqta)", c: ["circle", "circle-fill", "record-fill", "dot"] },
  "status.live": { d: "Jonli (live)", c: ["radio", "broadcast", "signal", "dot-circle", "live"] },
  "status.finished": { d: "Tugagan", c: ["circle-check-big", "check-check", "flag-checkered", "circle-check"] },
  "status.pending": { d: "Kutilmoqda", c: ["hourglass", "clock", "hourglass-medium", "ellipsis", "time"] },
  "status.verified": { d: "Tasdiqlangan", c: ["badge-check", "seal-check", "verified", "rosette-discount-check", "check-badge"] },
  "status.blocked": { d: "Bloklangan", c: ["ban", "circle-slash", "block", "prohibited", "user-forbid"] },

  // ═══ 4. Reyting va yutuq (20) ═══════════════════════════════════════
  "ranking.streak": { d: "Olov (streak)", c: ["flame", "fire", "flame-fill"] },
  "ranking.star": { d: "Yulduz", c: ["star", "star-fill"] },
  "ranking.trophy": { d: "Kubok", c: ["trophy", "award", "trophy-fill"] },
  "ranking.medalGold": { d: "Oltin medal", c: ["medal", "medal-1", "award", "ranking"] },
  "ranking.medalSilver": { d: "Kumush medal", c: ["medal", "medal-2", "award", "ranking"] },
  "ranking.medalBronze": { d: "Bronza medal", c: ["medal", "medal-3", "award", "ranking"] },
  "ranking.diamond": { d: "Olmos", c: ["gem", "diamond", "diamond-fill", "sparkle"] },
  "ranking.crown": { d: "Toj", c: ["crown", "crown-simple", "crown-fill"] },
  "ranking.shield": { d: "Qalqon", c: ["shield", "shield-check", "shield-fill", "security"] },
  "ranking.badge": { d: "Nishon (yutuq)", c: ["badge", "award", "rosette", "ribbon"] },
  "ranking.certificate": { d: "Sertifikat", c: ["scroll", "file-badge", "certificate", "file-certificate", "award"] },
  "ranking.chartBar": { d: "Ustunli grafik", c: ["chart-no-axes-column", "chart-bar", "bar-chart", "chart-column"] },
  "ranking.chartLine": { d: "Chiziqli grafik", c: ["chart-line", "chart-spline", "line-chart", "chart-line-up"] },
  "ranking.chartPie": { d: "Doira diagramma", c: ["chart-pie", "pie-chart", "chart-donut", "chart-pie-slice"] },
  "ranking.trendUp": { d: "O'sish (trend up)", c: ["trending-up", "arrow-trend-up", "trend-up", "chart-line-up"] },
  "ranking.trendDown": { d: "Pasayish (trend down)", c: ["trending-down", "arrow-trend-down", "trend-down", "chart-line-down"] },
  "ranking.rank": { d: "O'rin / rank nishonchasi", c: ["hash", "number-sign", "list-ordered", "ranking", "trophy"] },
  "ranking.thumbUp": { d: "Bosh barmoq yuqori", c: ["thumbs-up", "thumb-up", "hand-thumbs-up", "like"] },
  "ranking.thumbDown": { d: "Bosh barmoq past", c: ["thumbs-down", "thumb-down", "hand-thumbs-down", "dislike"] },
  "ranking.podium": { d: "Sovrin (podium)", c: ["podium", "chart-no-axes-column", "ranking", "trophy"] },

  // ═══ 5. Foydalanuvchi va jamoa (16) ════════════════════════════════
  "user.profile": { d: "Foydalanuvchi profili", c: ["user", "person", "user-circle", "circle-user", "profile"] },
  "user.group": { d: "Jamoa / guruh", c: ["users", "group", "team", "user-group", "people"] },
  "user.avatar": { d: "Avatar joy egallovchi", c: ["user", "user-circle", "person", "circle-user"] },
  "user.follow": { d: "Obuna bo'lish", c: ["user-plus", "person-add", "user-add", "user-follow"] },
  "user.unfollow": { d: "Obunani bekor qilish", c: ["user-minus", "person-remove", "user-remove", "user-unfollow"] },
  "user.followers": { d: "Obunachilar", c: ["users", "group", "users-three", "people"] },
  "user.block": { d: "Bloklash", c: ["user-x", "user-block", "person-x", "user-forbid", "ban"] },
  "user.logout": { d: "Chiqish", c: ["log-out", "arrow-right-on-rectangle", "box-arrow-right", "logout-box", "sign-out"] },
  "user.invite": { d: "Taklif qilish", c: ["user-plus", "mail-plus", "envelope-plus", "share-2", "send"] },
  "user.roleAdmin": { d: "Rol: administrator", c: ["shield-check", "user-cog", "user-shield", "admin", "crown"] },
  "user.roleTeacher": { d: "Rol: o'qituvchi", c: ["presentation", "chalkboard-teacher", "academic-cap", "school", "person-chalkboard"] },
  "user.roleStudent": { d: "Rol: o'quvchi", c: ["graduation-cap", "student", "backpack", "book-open"] },
  "user.work": { d: "Ish joyi", c: ["briefcase", "bag-briefcase", "business", "suitcase"] },
  "user.education": { d: "Ta'lim", c: ["graduation-cap", "school", "academic-cap", "book-open"] },
  "user.location": { d: "Joylashuv", c: ["map-pin", "location", "map-marker", "marker"] },
  "user.link": { d: "Havola", c: ["link", "link-2", "chain", "link-simple"] },

  // ═══ 6. Musobaqa (14) ═══════════════════════════════════════════════
  "contest.calendar": { d: "Kalendar", c: ["calendar", "calendar-days", "calendar-event"] },
  "contest.clock": { d: "Boshlanish vaqti", c: ["clock", "time", "clock-3", "watch"] },
  "contest.flag": { d: "Bayroq (finish)", c: ["flag", "flag-checkered", "flag-fill", "flag-2"] },
  "contest.lock": { d: "Kontest yopiq", c: ["lock", "lock-closed", "padlock"] },
  "contest.live": { d: "Davom etmoqda (jonli)", c: ["radio", "broadcast", "signal", "live", "dot-circle"] },
  "contest.register": { d: "Ro'yxatdan o'tish", c: ["clipboard-check", "user-check", "check-square", "square-check", "edit"] },
  "contest.standings": { d: "Natijalar jadvali", c: ["list-ordered", "table", "ranking", "table-list", "hash"] },
  "contest.formatAcm": { d: "ACM formati belgisi", c: ["circle-x", "circle-check", "scale", "trophy"] },
  "contest.formatIoi": { d: "IOI formati belgisi", c: ["chart-bar", "chart-no-axes-column", "award", "trophy"] },
  "contest.rated": { d: "Reytingli (Rated)", c: ["trending-up", "arrow-trend-up", "star", "chart-line-up"] },
  "contest.team": { d: "Jamoaviy", c: ["users", "group", "team", "user-group"] },
  "contest.duel": { d: "Duel (qilich)", c: ["swords", "sword", "crosshair", "crosshair-2", "bolt"] },
  "contest.arena": { d: "Arena", c: ["target", "crosshair", "crosshair-2", "bolt", "swords"] },
  "contest.hackathon": { d: "Hackathon", c: ["code", "code-bracket", "terminal", "rocket", "rocket-launch"] },

  // ═══ 7. Kontent (18) ════════════════════════════════════════════════
  "content.problem": { d: "Masala (kitob)", c: ["book-open", "book", "notebook", "file-text", "books"] },
  "content.article": { d: "Maqola", c: ["newspaper", "news", "article", "file-text", "document"] },
  "content.course": { d: "Kurs", c: ["graduation-cap", "academic-cap", "school", "book-open", "presentation"] },
  "content.video": { d: "Video dars", c: ["video", "play-circle", "video-camera", "circle-play", "film"] },
  "content.audio": { d: "Audio / podkast", c: ["headphones", "headphones-simple", "music", "microphone", "audio"] },
  "content.image": { d: "Rasm", c: ["image", "photo", "picture", "image-2", "photo-fill"] },
  "content.file": { d: "Fayl", c: ["file", "file-text", "document", "files", "file-earmark"] },
  "content.pdf": { d: "PDF hujjat", c: ["file-text", "file-pdf", "file-earmark-pdf", "document", "book"] },
  "content.code": { d: "Kod", c: ["code", "code-2", "code-bracket", "code-xml", "source-code"] },
  "content.terminal": { d: "Terminal / konsol", c: ["terminal", "terminal-window", "command", "console"] },
  "content.roadmap": { d: "Yo'l xaritasi", c: ["map", "route", "signpost", "map-pin", "waypoints"] },
  "content.algorithm": { d: "Algoritmlar", c: ["route", "git-branch", "network", "share-2", "waypoints", "sitemap"] },
  "content.test": { d: "Testlar", c: ["flask", "beaker", "test-tube", "vial", "clipboard-check"] },
  "content.quiz": { d: "Quiz", c: ["circle-help", "question-mark-circle", "question-circle", "help-circle", "question"] },
  "content.level": { d: "Daraja (level)", c: ["layers", "stack", "layer-group", "stairs", "chart-bar"] },
  "content.step": { d: "Qadam (onboarding)", c: ["footprints", "shoe-prints", "steps", "list-ordered", "signpost"] },
  "content.tag": { d: "Yorliq (teg)", c: ["tag", "hash", "price-tag", "tags", "label"] },
  "content.category": { d: "Toifa", c: ["folder", "folder-open", "grid", "squares-four", "collection"] },

  // ═══ 8. Bildirishnoma (10) ══════════════════════════════════════════
  "notification.bell": { d: "Qo'ng'iroq", c: ["bell", "bell-fill"] },
  "notification.bellRead": { d: "O'qilgan bildirishnoma", c: ["bell", "bell-slash", "bell-off", "bell-fill"] },
  "notification.email": { d: "Xat (envelope)", c: ["mail", "envelope", "envelope-simple", "email"] },
  "notification.chat": { d: "Xabar (chat)", c: ["message-circle", "chat", "chat-circle", "message-square", "chat-round"] },
  "notification.comment": { d: "Izoh", c: ["message-square", "chat", "comment", "message", "chat-text"] },
  "notification.reply": { d: "Javob berish", c: ["reply", "arrow-back-up", "arrow-left", "corner-up-left", "reply-all"] },
  "notification.badgeNew": { d: "Yangi (badge)", c: ["badge", "circle", "record-fill", "sparkle", "dot"] },
  "notification.muted": { d: "O'chirilgan bildirishnoma", c: ["bell-off", "bell-slash", "bell-minus", "notification-off"] },
  "notification.changelog": { d: "Yangilanishlar", c: ["megaphone", "sparkles", "rocket", "bell", "newspaper"] },
  "notification.announce": { d: "E'lon (megafon)", c: ["megaphone", "speakerphone", "bullhorn", "campaign"] },

  // ═══ 9. Do'kon va valyuta (10) ══════════════════════════════════════
  "shop.coin": { d: "Tanga (qvant)", c: ["coins", "coin", "wallet", "currency-dollar", "money"] },
  "shop.store": { d: "Do'kon", c: ["store", "shopping-bag", "shop", "storefront", "bag"] },
  "shop.cart": { d: "Savat", c: ["shopping-cart", "cart", "shopping-cart-simple", "cart-3"] },
  "shop.gift": { d: "Sovg'a", c: ["gift", "gift-fill", "present"] },
  "shop.discount": { d: "Chegirma (%)", c: ["percent", "badge-percent", "discount", "sale", "tag"] },
  "shop.price": { d: "Narx yulduzchasi", c: ["star", "tag", "price-tag", "sparkle", "diamond"] },
  "shop.buy": { d: "Sotib olish", c: ["shopping-bag", "credit-card", "cart", "bag-check", "checkout"] },
  "shop.history": { d: "Xaridlar tarixi", c: ["history", "clock-rotate-left", "clock-history", "receipt", "file-text"] },
  "shop.wallet": { d: "Hamyon / balans", c: ["wallet", "wallet-minimal", "purse", "credit-card", "coins"] },
  "shop.card": { d: "To'lov kartasi", c: ["credit-card", "card", "bank-card", "payment"] },

  // ═══ 10. Markdown muharriri (14) ════════════════════════════════════
  "markdown.bold": { d: "Qalin (B)", c: ["bold", "text-bold", "format-bold", "type-bold"] },
  "markdown.italic": { d: "Kursiv (I)", c: ["italic", "text-italic", "format-italic", "type-italic"] },
  "markdown.heading": { d: "Sarlavha (H)", c: ["heading", "text-h", "format-header", "type-h1", "heading-1"] },
  "markdown.list": { d: "Belgili ro'yxat", c: ["list", "list-bullet", "list-ul", "unordered-list", "list-2"] },
  "markdown.orderedList": { d: "Raqamli ro'yxat", c: ["list-ordered", "ordered-list", "list-ol", "list-numbers", "number-list"] },
  "markdown.link": { d: "Havola", c: ["link", "link-2", "chain", "link-simple"] },
  "markdown.image": { d: "Rasm", c: ["image", "photo", "picture", "image-2"] },
  "markdown.code": { d: "Kod (inline)", c: ["code", "code-2", "code-xml", "source-code"] },
  "markdown.codeBlock": { d: "Kod bloki", c: ["code-square", "code-block", "square-code", "file-code", "terminal"] },
  "markdown.quote": { d: "Iqtibos", c: ["quote", "text-quote", "blockquote", "quote-2", "format-quote"] },
  "markdown.table": { d: "Jadval", c: ["table", "table-2", "grid", "table-cells", "layout-grid"] },
  "markdown.hr": { d: "Ajratuvchi chiziq", c: ["minus", "remove", "line", "horizontal-rule", "separator"] },
  "markdown.preview": { d: "Ko'rib chiqish (preview)", c: ["eye", "eye-open", "preview", "visibility"] },
  "markdown.formula": { d: "LaTeX / formula", c: ["function", "sigma", "square-function", "square-root", "calculator"] },

  // ═══ 11. Til va davlat (6) ══════════════════════════════════════════
  "locale.globe": { d: "Globus", c: ["globe", "language", "translate", "world"] },
  "locale.flag": { d: "Bayroq (davlat)", c: ["flag", "flag-fill", "flag-2", "flag-banner"] },
  "locale.switch": { d: "Til almashtirish", c: ["languages", "language", "translate", "globe", "arrows-repeat"] },
  "locale.translate": { d: "Tarjima", c: ["languages", "translate", "language", "translate-2"] },
  "locale.region": { d: "Mintaqa", c: ["map", "map-pin", "globe", "compass"] },
  "locale.timezone": { d: "Vaqt mintaqasi", c: ["clock", "globe", "time", "earth", "world"] },

  // ═══ 12. Statistika va ma'lumot (12) ════════════════════════════════
  "stats.chartBar": { d: "Ustunli grafik", c: ["chart-no-axes-column", "chart-bar", "bar-chart", "chart-column"] },
  "stats.chartLine": { d: "Chiziqli grafik", c: ["chart-line", "chart-spline", "line-chart", "chart-line-up"] },
  "stats.chartPie": { d: "Doira diagramma", c: ["chart-pie", "pie-chart", "chart-donut", "chart-pie-slice"] },
  "stats.table": { d: "Jadval", c: ["table", "table-2", "grid", "table-cells", "layout-grid"] },
  "stats.funnel": { d: "Filtr (funnel)", c: ["funnel", "filter", "filter-list"] },
  "stats.percent": { d: "Foiz (%)", c: ["percent", "badge-percent", "percentage"] },
  "stats.calculator": { d: "Kalkulyator", c: ["calculator", "calculator-simple", "math"] },
  "stats.database": { d: "Ma'lumotlar bazasi", c: ["database", "cylinder", "storage", "data"] },
  "stats.server": { d: "Server", c: ["server", "hard-drives", "cloud", "server-2", "hdd"] },
  "stats.speed": { d: "Tezlik (performance)", c: ["gauge", "speedometer", "dashboard", "tachometer", "activity"] },
  "stats.load": { d: "Yuklanish", c: ["activity", "pulse", "chart-line-up", "cpu", "gauge"] },
  "stats.memory": { d: "Xotira", c: ["cpu", "memory", "microchip", "hard-drive", "server"] },

  // ═══ 13. Tizim va sozlama (12) ══════════════════════════════════════
  "system.settings": { d: "Tishli (sozlama)", c: ["settings", "cog", "gear", "settings-2"] },
  "system.palette": { d: "Palitra", c: ["palette", "paint-brush", "paintbrush", "swatch", "brush"] },
  "system.light": { d: "Yorug' rejim", c: ["sun", "sun-bright", "sun-medium", "brightness"] },
  "system.dark": { d: "Qorong'i rejim", c: ["moon", "moon-stars", "moon-fill"] },
  "system.monitor": { d: "Monitor (tizim)", c: ["monitor", "desktop-computer", "display", "computer", "screen"] },
  "system.security": { d: "Xavfsizlik", c: ["shield", "shield-check", "security", "shield-fill"] },
  "system.key": { d: "Kalit (parol)", c: ["key", "key-round", "key-fill", "password", "lock-key"] },
  "system.device": { d: "Qurilma", c: ["cpu", "device-desktop", "laptop", "hard-drive", "chip"] },
  "system.sessions": { d: "Sessiyalar", c: ["monitor-smartphone", "devices", "laptop-mobile", "layout-grid", "list"] },
  "system.log": { d: "Jurnal (log)", c: ["file-text", "scroll-text", "file-lines", "journal", "clipboard-list"] },
  "system.backup": { d: "Zaxira nusxa", c: ["database-backup", "cloud-arrow-up", "archive", "save", "download"] },
  "system.apiKey": { d: "API kalit", c: ["key", "braces", "code", "terminal", "key-round"] },

  // ═══ 14. Mobil va qurilma (8) ═══════════════════════════════════════
  "device.phone": { d: "Telefon", c: ["smartphone", "device-mobile", "phone", "mobile"] },
  "device.tablet": { d: "Planshet", c: ["tablet", "device-tablet", "tablet-button", "ipad"] },
  "device.laptop": { d: "Noutbuk", c: ["laptop", "device-laptop", "laptop-minimal", "computer-laptop"] },
  "device.desktop": { d: "Ish stoli", c: ["monitor", "desktop-computer", "device-desktop", "computer", "display"] },
  "device.browser": { d: "Brauzer", c: ["globe", "browser", "window", "app-window", "layout"] },
  "device.qr": { d: "QR kod", c: ["qr-code", "qrcode", "qr"] },
  "device.appStore": { d: "Ilova yuklab olish", c: ["download", "device-mobile-down", "arrow-down-to-line", "app-store"] },
  "device.touch": { d: "Sensor (touch)", c: ["pointer", "hand", "cursor-click", "hand-pointing", "touch"] },

  // ═══ 15. Bo'sh holatlar (8) ═════════════════════════════════════════
  "empty.search": { d: "Qidiruv natijasi yo'q", c: ["search-x", "magnifying-glass", "search", "magnifier"] },
  "empty.attempts": { d: "Urinishlar yo'q", c: ["clipboard-list", "list", "history", "file-text", "clipboard-text"] },
  "empty.notifications": { d: "Bildirishnoma yo'q", c: ["bell-off", "bell-slash", "bell", "notification-off"] },
  "empty.team": { d: "Jamoa yo'q", c: ["users", "group", "team", "user-group"] },
  "empty.messages": { d: "Xabar yo'q", c: ["message-circle", "chat", "chat-circle", "message-square"] },
  "empty.files": { d: "Fayl yo'q", c: ["folder-open", "folder", "file", "files"] },
  "empty.notFound": { d: "404 — topilmadi", c: ["compass", "map", "search", "question", "circle-help"] },
  "empty.serverError": { d: "500 — server xatosi", c: ["settings", "cog", "server", "triangle-alert", "gear"] },

  // ═══ 16. Xatolik holatlari (6) ══════════════════════════════════════
  "error.network": { d: "Tarmoq xatosi", c: ["wifi-off", "signal-slash", "wifi", "plug", "cloud-off"] },
  "error.server": { d: "Server xatosi", c: ["flame", "fire", "server", "triangle-alert", "alert"] },
  "error.forbidden": { d: "Ruxsat yo'q", c: ["ban", "circle-slash", "block", "prohibited", "lock"] },
  "error.notFound": { d: "Topilmadi", c: ["search-x", "search", "circle-help", "magnifying-glass"] },
  "error.timeout": { d: "Muddat tugadi", c: ["timer-off", "clock-x", "timer", "alarm", "hourglass"] },
  "error.invalid": { d: "Noto'g'ri ma'lumot", c: ["triangle-alert", "alert-triangle", "warning", "circle-alert"] },

  // ═══ 17. Fayl va media (12) ═════════════════════════════════════════
  "media.clip": { d: "Biriktirish (clip)", c: ["paperclip", "attachment", "clip", "attach"] },
  "media.folder": { d: "Papka", c: ["folder", "folder-open", "folder-simple", "directory"] },
  "media.play": { d: "O'ynatish", c: ["play", "circle-play", "play-circle", "play-fill"] },
  "media.pause": { d: "To'xtatish (pauza)", c: ["pause", "circle-pause", "pause-circle", "player-pause"] },
  "media.next": { d: "Keyingi", c: ["skip-forward", "player-skip-forward", "chevron-right", "next"] },
  "media.prev": { d: "Oldingi", c: ["skip-back", "player-skip-back", "chevron-left", "previous"] },
  "media.volume": { d: "Ovoz balandligi", c: ["volume-2", "speaker-high", "volume", "volume-up"] },
  "media.fullscreen": { d: "To'liq ekran", c: ["maximize", "arrows-out", "fullscreen", "arrows-maximize"] },
  "media.zoomIn": { d: "Kattalashtirish", c: ["zoom-in", "magnifying-glass-plus", "search-plus", "zoom-in-area"] },
  "media.zoomOut": { d: "Kichraytirish", c: ["zoom-out", "magnifying-glass-minus", "search-minus", "zoom-out-area"] },
  "media.rotate": { d: "Aylantirish", c: ["rotate-cw", "rotate-right", "refresh", "arrow-clockwise", "rotate"] },
  "media.crop": { d: "Kesish (crop)", c: ["crop", "crop-simple", "scissors", "cut"] },

  // ═══ 18. Brend: dasturlash tillari (12) — QAT'IY ════════════════════
  // ⚠️ Logotiplar. Phosphor/Tabler/Lucide'da YO'Q — Simple Icons'dan.
  "brand.langPython": { d: "Python tili", c: ["python"] },
  "brand.langCpp": { d: "C++ tili", c: ["cplusplus"] },
  "brand.langC": { d: "C tili", c: ["c"] },
  "brand.langJava": { d: "Java tili", c: ["java", "openjdk"] },
  "brand.langJavascript": { d: "JavaScript tili", c: ["javascript"] },
  "brand.langTypescript": { d: "TypeScript tili", c: ["typescript"] },
  "brand.langGo": { d: "Go tili", c: ["go"] },
  "brand.langRust": { d: "Rust tili", c: ["rust"] },
  "brand.langKotlin": { d: "Kotlin tili", c: ["kotlin"] },
  "brand.langCsharp": { d: "C# tili", c: ["csharp", "dotnet"] },
  "brand.langPhp": { d: "PHP tili", c: ["php"] },
  "brand.langSql": { d: "SQL", c: ["mysql", "postgresql", "sqlite", "databricks"] },

  // ═══ 19. Brend: ijtimoiy tarmoqlar (10) — QAT'IY ════════════════════
  "brand.socialTelegram": { d: "Telegram", c: ["telegram"] },
  "brand.socialGithub": { d: "GitHub", c: ["github"] },
  "brand.socialGoogle": { d: "Google", c: ["google"] },
  "brand.socialInstagram": { d: "Instagram", c: ["instagram"] },
  "brand.socialYoutube": { d: "YouTube", c: ["youtube"] },
  "brand.socialLinkedin": { d: "LinkedIn", c: ["linkedin"] },
  "brand.socialX": { d: "X (Twitter)", c: ["x", "twitter"] },
  "brand.socialFacebook": { d: "Facebook", c: ["facebook"] },
  "brand.socialDiscord": { d: "Discord", c: ["discord"] },
  "brand.socialWebsite": { d: "Veb-sayt", c: ["googlechrome", "firefox", "safari"] },
};

/** Qat'iy domenlar (D20 ①) — to'plam almashganda o'zgarmaydi. */
export const FIXED_DOMAINS = ["verdict", "brand"];

/** Kategoriyalar — hisobot va tekshiruv uchun tartib. */
export const CATEGORIES = [
  { id: "nav", name: "Navigatsiya" },
  { id: "action", name: "Tugma va amallar" },
  { id: "status", name: "Status va holat" },
  { id: "ranking", name: "Reyting va yutuq" },
  { id: "user", name: "Foydalanuvchi va jamoa" },
  { id: "contest", name: "Musobaqa" },
  { id: "content", name: "Kontent" },
  { id: "notification", name: "Bildirishnoma" },
  { id: "shop", name: "Do'kon va valyuta" },
  { id: "markdown", name: "Markdown muharriri" },
  { id: "locale", name: "Til va davlat" },
  { id: "stats", name: "Statistika va ma'lumot" },
  { id: "system", name: "Tizim va sozlama" },
  { id: "device", name: "Mobil va qurilma" },
  { id: "empty", name: "Bo'sh holatlar" },
  { id: "error", name: "Xatolik holatlari" },
  { id: "media", name: "Fayl va media" },
  { id: "brand", name: "Brend (tillar + ijtimoiy)" },
];

/** To'plam manbalari. */
export const PACK_SOURCES = {
  lucide: {
    list: "https://data.jsdelivr.com/v1/packages/npm/lucide-static@0.544.0?structure=flat",
    prefix: "/icons/",
    url: (n) => `https://cdn.jsdelivr.net/npm/lucide-static@0.544.0/icons/${n}.svg`,
  },
  tabler: {
    list: "https://data.jsdelivr.com/v1/packages/npm/@tabler/icons@3.34.1?structure=flat",
    prefix: "/icons/outline/",
    url: (n) => `https://cdn.jsdelivr.net/npm/@tabler/icons@3.34.1/icons/outline/${n}.svg`,
  },
  heroicons: {
    list: "https://data.jsdelivr.com/v1/packages/npm/heroicons@2.2.0?structure=flat",
    prefix: "/24/outline/",
    url: (n) => `https://cdn.jsdelivr.net/npm/heroicons@2.2.0/24/outline/${n}.svg`,
  },
  heroiconsSolid: {
    list: "https://data.jsdelivr.com/v1/packages/npm/heroicons@2.2.0?structure=flat",
    prefix: "/24/solid/",
    url: (n) => `https://cdn.jsdelivr.net/npm/heroicons@2.2.0/24/solid/${n}.svg`,
  },
  bootstrap: {
    list: "https://data.jsdelivr.com/v1/packages/npm/bootstrap-icons@1.13.1?structure=flat",
    prefix: "/icons/",
    url: (n) => `https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/icons/${n}.svg`,
  },
  remix: {
    list: "https://data.jsdelivr.com/v1/packages/npm/remixicon@4.6.0?structure=flat",
    prefix: "/icons/",
    url: (n) => `https://cdn.jsdelivr.net/npm/remixicon@4.6.0/icons/${n}.svg`,
  },
};

/** ⚠️ Phosphorning uch uslubi — haqiqiy uch xil fayl to'plami. */
const PHOSPHOR_LIST =
  "https://data.jsdelivr.com/v1/packages/npm/@phosphor-icons/core@2.1.1?structure=flat";
const phosphorUrl = (style, n) =>
  `https://cdn.jsdelivr.net/npm/@phosphor-icons/core@2.1.1/assets/${style}/${n}${
    style === "regular" ? "" : "-" + style
  }.svg`;

PACK_SOURCES.phosphor = {
  list: PHOSPHOR_LIST,
  prefix: "/assets/regular/",
  url: (n) => phosphorUrl("regular", n),
};
PACK_SOURCES.phosphorSolid = {
  list: PHOSPHOR_LIST,
  prefix: "/assets/fill/",
  url: (n) => phosphorUrl("fill", n),
};
PACK_SOURCES.phosphorDuotone = {
  list: PHOSPHOR_LIST,
  prefix: "/assets/duotone/",
  url: (n) => phosphorUrl("duotone", n),
};

/** Brend to'plami — Simple Icons (npm paketi allaqachon o'rnatilgan). */
export const BRAND_SOURCE = "simple-icons";
