/** The team page's text — content, like the legal pages (`content/legal.ts`).
 *
 *  The page is a joke with a true line under it: every department and every
 *  title is held by the one person who builds the platform. It is written
 *  as data in Uzbek, Russian and English; the other seven locales read the
 *  Uzbek text, as they do on the legal pages. A joke translated by key into
 *  languages nobody on the project can review would not be a joke.
 */

export type TeamLocale = "uz" | "ru" | "en";

export function pickTeam(locale: string): TeamLocale {
  return locale === "ru" || locale === "en" ? locale : "uz";
}

/** The one member. The links are the project's public addresses. */
export const TEAM_MEMBER = {
  name: "Saidakbar Narzullayev",
  initials: "SN",
  links: [
    { label: "Telegram", href: "https://t.me/rankwant" },
    { label: "GitHub", href: "https://github.com/menarzullayev" },
  ],
} as const;

export type TeamRole = {
  /** Index into `depts`. */
  dept: number;
  /** A short mark on the avatar — not translated. */
  badge: string;
  /** Avatar hue, so twenty-four copies of one person can be told apart. */
  hue: number;
  tone: "ok" | "warn";
};

export const TEAM_ROLES: TeamRole[] = [
  { dept: 0, badge: "CEO", hue: 262, tone: "ok" },
  { dept: 0, badge: "x1", hue: 250, tone: "ok" },
  { dept: 1, badge: "CTO", hue: 215, tone: "warn" },
  { dept: 1, badge: "API", hue: 200, tone: "ok" },
  { dept: 1, badge: "</>", hue: 190, tone: "ok" },
  { dept: 1, badge: "AC", hue: 140, tone: "ok" },
  { dept: 1, badge: "LGTM", hue: 170, tone: "ok" },
  { dept: 2, badge: "UI", hue: 320, tone: "warn" },
  { dept: 2, badge: "UX", hue: 300, tone: "ok" },
  { dept: 3, badge: "QA", hue: 20, tone: "warn" },
  { dept: 3, badge: "!ok", hue: 0, tone: "ok" },
  { dept: 4, badge: "CI", hue: 95, tone: "ok" },
  { dept: 4, badge: "02:00", hue: 240, tone: "warn" },
  { dept: 4, badge: "SQL", hue: 205, tone: "ok" },
  { dept: 5, badge: "A+B", hue: 38, tone: "ok" },
  { dept: 5, badge: "Aa", hue: 52, tone: "warn" },
  { dept: 5, badge: "10", hue: 170, tone: "warn" },
  { dept: 6, badge: "24/7", hue: 345, tone: "ok" },
  { dept: 7, badge: "CMO", hue: 290, tone: "ok" },
  { dept: 7, badge: "@", hue: 330, tone: "ok" },
  { dept: 8, badge: "CFO", hue: 150, tone: "ok" },
  { dept: 9, badge: "§", hue: 225, tone: "ok" },
  { dept: 10, badge: "HR", hue: 310, tone: "ok" },
  { dept: 11, badge: "tea", hue: 30, tone: "ok" },
];

/** `[title, what they do, reports to, status]`, in the order of `TEAM_ROLES`. */
type RoleText = readonly [string, string, string, string];

export type TeamText = {
  eyebrow: string;
  heading: string;
  lede: string;
  stats: readonly [string, string, string, string];
  filterLabel: string;
  all: string;
  search: string;
  serious: string;
  /** `{roles}` and `{people}` are replaced. */
  count: string;
  empty: string;
  more: string;
  less: string;
  detail: readonly [string, string][];
  reportsTo: string;
  soloRole: string;
  soloText: string;
  soloCount: string;
  hireTitle: string;
  hireText: string;
  hireCta: string;
  /** `{name}` is replaced. */
  photoAlt: string;
  depts: readonly string[];
  roles: readonly RoleText[];
};

export const TEAM_TEXT: Record<TeamLocale, TeamText> = {
  uz: {
    eyebrow: "Biz haqimizda · jamoa",
    heading: "RankWant ortidagi katta, ahil jamoa",
    lede: "O'n ikki bo'lim, yigirma to'rt lavozim va bitta umumiy maqsad. Jamoamiz shu qadar ahilki, majlislar bir daqiqada tugaydi va hech kim hech qachon bir-birining gapini bo'lmaydi.",
    stats: ["lavozim", "bo'lim", "inson", "kelishmovchilik"],
    filterLabel: "Bo'lim bo'yicha saralash",
    all: "Hammasi",
    search: "Lavozim qidirish",
    serious: "Jiddiy rejim",
    count: "{roles} ta lavozim ko'rsatilmoqda · ularni egallagan odamlar soni: {people}",
    empty: "Bunday lavozim hali ochilmagan. Ochilsa, kim egallashi ma'lum.",
    more: "Batafsil",
    less: "Yopish",
    detail: [
      ["Jamoadagi hamkasblari", "o'zi"],
      ["Ta'til", "rejalashtirilmoqda (har yili)"],
      ["Sevimli majlis", "bekor qilingani"],
    ],
    reportsTo: "Hisobot beradi",
    soloRole: "Asoschi va yagona ishlab chiquvchi",
    soloText:
      "RankWant — bir kishi tomonidan qurilayotgan platforma: backend, frontend, judge, dizayn va kontent bitta qo'lda. Yuqoridagi yigirma to'rt lavozim hazil, ish esa haqiqiy.",
    soloCount: "1 kishi, hazilsiz.",
    hireTitle: "Bo'sh o'rinlar",
    hireText:
      "Hozircha barcha lavozimlar band — bitta nomzod hammasiga mos keldi. Lekin haqiqiy hissa qo'shmoqchi bo'lsangiz, eshik ochiq.",
    hireCta: "Telegram'da yozish",
    photoAlt: "{name} rasmi",
    depts: [
      "Rahbariyat",
      "Muhandislik",
      "Dizayn",
      "Sifat",
      "Infratuzilma",
      "Kontent",
      "Qo'llab-quvvatlash",
      "Marketing",
      "Moliya",
      "Huquq",
      "Kadrlar",
      "Xo'jalik",
    ],
    roles: [
      ["Asoschi va bosh direktor", "Strategiyani belgilaydi. Strategiya: «bugun ham ishlaymiz».", "Vijdoniga", "Ofisda"],
      ["Direktorlar kengashi raisi", "Kengash yig'ilishlarida yagona ovoz bilan qaror qabul qiladi.", "Bosh direktorga", "Kvorum bor"],
      ["Bosh texnik direktor", "Arxitektura qarorlarini qabul qiladi va keyin o'zi bilan bahslashadi.", "Bosh direktorga", "O'zi bilan review'da"],
      ["Backend dasturchi", "Django, Celery va 3 soat davomida bitta vergul qidirish bo'yicha mutaxassis.", "Bosh texnik direktorga", "Kod yozmoqda"],
      ["Frontend dasturchi", "Tugmani 2 piksel chapga suradi. Keyin yana o'ngga.", "Bosh texnik direktorga", "Kod yozmoqda"],
      ["Judge muhandisi", "Sandbox ichida boshqalarning kodini, tashqarisida o'zinikini jazolaydi.", "Bosh texnik direktorga", "Accepted"],
      ["Kod sharhlovchi", "Har bir PR'ni sinchiklab o'qiydi. Muallifi tanish chiqadi.", "Backend dasturchiga", "Tasdiqladi"],
      ["Bosh dizayner", "12 ta uslub chizdi, chunki bittasini tanlay olmadi.", "Bosh direktorga", "Rang tanlamoqda"],
      ["UX tadqiqotchi", "Foydalanuvchilar bilan suhbat o'tkazadi. Suhbatdosh doim rozi bo'ladi.", "Bosh dizaynerga", "Intervyu o'tkazmoqda"],
      ["QA muhandisi", "Dasturchi «menda ishlayapti» desa, ishonmaydi. To'g'ri qiladi.", "Bosh texnik direktorga", "Bug topdi"],
      ["Salbiy testlar bo'yicha mutaxassis", "Hamma narsani ataylab buzadi va buzilganidan xursand bo'ladi.", "QA muhandisiga", "Qizil = yaxshi"],
      ["DevOps muhandisi", "Deploy tugmasini bosadi va nafasini ichiga yutadi.", "Bosh texnik direktorga", "CI yashil"],
      ["Tungi navbatchi", "Soat ikkida uyg'onadi. Kim uyg'otgani ma'lum.", "DevOps muhandisiga", "Uyqusiz"],
      ["Ma'lumotlar bazasi ma'muri", "Indeks qo'shadi. Zaxira nusxa oladi. Yaxshi uxlaydi (nazariy jihatdan).", "DevOps muhandisiga", "Zaxira bor"],
      ["Masalalar muallifi", "A + B dan boshladi. Hozircha A + B da.", "Kontent rahbariga", "Yozmoqda"],
      ["Kontent rahbari", "Masalalar muallifidan muddatni so'raydi. Javob oladi: «ertaga».", "Bosh direktorga", "Muddat yaqin"],
      ["Tarjimon (10 til)", "O'zbekchani biladi. Qolgan to'qqiztasini tekshirib ko'rishga va'da bergan.", "Kontent rahbariga", "Ko'rib chiqilmagan"],
      ["Qo'llab-quvvatlash xizmati", "Murojaatlarga 24/7 javob beradi, uxlagan paytidan tashqari.", "Bosh direktorga", "Onlayn"],
      ["Marketing direktori", "Reklama byudjeti: 0 so'm. Samaradorlik: cheksiz.", "Bosh direktorga", "Kampaniya ketmoqda"],
      ["SMM menejeri", "Kanalga post yozadi va birinchi bo'lib o'zi layk bosadi.", "Marketing direktoriga", "1 ta layk"],
      ["Moliya direktori", "Xarajatlarni tasdiqlaydi: server, domen va choy.", "Bosh direktorga", "Byudjet ichida"],
      ["Yurist", "Foydalanish shartlarini yozdi. Hatto o'zi ham o'qib chiqdi.", "Bosh direktorga", "Shartlar yozilgan"],
      ["Kadrlar bo'limi boshlig'i", "Yil xodimini aniqladi. Nomzodlar ro'yxati qisqa edi.", "Bosh direktorga", "Jamoa ruhi a'lo"],
      ["Choy damlovchi", "Eng muhim lavozim. Butun ishlab chiqarish shu kishiga bog'liq.", "Hammaga", "Qaynayapti"],
    ],
  },
  ru: {
    eyebrow: "О нас · команда",
    heading: "Большая и дружная команда RankWant",
    lede: "Двенадцать отделов, двадцать четыре должности и одна общая цель. Мы настолько дружны, что совещания длятся минуту и никто никого не перебивает.",
    stats: ["должности", "отделов", "человек", "разногласий"],
    filterLabel: "Фильтр по отделу",
    all: "Все",
    search: "Найти должность",
    serious: "Серьёзный режим",
    count: "Показано должностей: {roles} · людей, которые их занимают: {people}",
    empty: "Такой должности пока нет. Если появится — известно, кто её займёт.",
    more: "Подробнее",
    less: "Свернуть",
    detail: [
      ["Коллеги по команде", "он сам"],
      ["Отпуск", "планируется (каждый год)"],
      ["Любимое совещание", "отменённое"],
    ],
    reportsTo: "Подчиняется",
    soloRole: "Основатель и единственный разработчик",
    soloText:
      "RankWant — платформа, которую строит один человек: бэкенд, фронтенд, judge, дизайн и контент в одних руках. Двадцать четыре должности выше — шутка, а работа настоящая.",
    soloCount: "1 человек, без шуток.",
    hireTitle: "Вакансии",
    hireText:
      "Сейчас все должности заняты — один кандидат подошёл на каждую. Но если хотите внести настоящий вклад, дверь открыта.",
    hireCta: "Написать в Telegram",
    photoAlt: "Фото: {name}",
    depts: [
      "Руководство",
      "Разработка",
      "Дизайн",
      "Качество",
      "Инфраструктура",
      "Контент",
      "Поддержка",
      "Маркетинг",
      "Финансы",
      "Право",
      "Кадры",
      "Хозяйство",
    ],
    roles: [
      ["Основатель и генеральный директор", "Определяет стратегию. Стратегия: «сегодня тоже работаем».", "Совести", "В офисе"],
      ["Председатель совета директоров", "На заседаниях совета принимает решения единогласно.", "Генеральному директору", "Кворум есть"],
      ["Технический директор", "Принимает архитектурные решения, а потом спорит сам с собой.", "Генеральному директору", "На ревью у себя"],
      ["Бэкенд-разработчик", "Специалист по Django, Celery и трёхчасовому поиску одной запятой.", "Техническому директору", "Пишет код"],
      ["Фронтенд-разработчик", "Двигает кнопку на 2 пикселя влево. Потом обратно вправо.", "Техническому директору", "Пишет код"],
      ["Инженер judge", "В песочнице наказывает чужой код, снаружи — свой.", "Техническому директору", "Accepted"],
      ["Ревьюер кода", "Внимательно читает каждый PR. Автор оказывается знакомым.", "Бэкенд-разработчику", "Одобрил"],
      ["Главный дизайнер", "Нарисовал 12 стилей, потому что не смог выбрать один.", "Генеральному директору", "Выбирает цвет"],
      ["UX-исследователь", "Проводит интервью с пользователями. Собеседник всегда согласен.", "Главному дизайнеру", "Берёт интервью"],
      ["QA-инженер", "Не верит разработчику, когда тот говорит «у меня работает». И правильно.", "Техническому директору", "Нашёл баг"],
      ["Специалист по негативным тестам", "Нарочно всё ломает и радуется, когда сломалось.", "QA-инженеру", "Красное = хорошо"],
      ["DevOps-инженер", "Нажимает кнопку деплоя и задерживает дыхание.", "Техническому директору", "CI зелёный"],
      ["Ночной дежурный", "Просыпается в два часа ночи. Известно, кто разбудил.", "DevOps-инженеру", "Не спал"],
      ["Администратор баз данных", "Добавляет индекс. Делает бэкап. Спит спокойно (в теории).", "DevOps-инженеру", "Бэкап есть"],
      ["Автор задач", "Начал с A + B. Пока на A + B.", "Руководителю контента", "Пишет"],
      ["Руководитель контента", "Спрашивает у автора задач о сроках. Получает ответ: «завтра».", "Генеральному директору", "Срок близко"],
      ["Переводчик (10 языков)", "Знает узбекский. Остальные девять обещал проверить.", "Руководителю контента", "Не проверено"],
      ["Служба поддержки", "Отвечает на обращения 24/7, кроме времени сна.", "Генеральному директору", "Онлайн"],
      ["Директор по маркетингу", "Рекламный бюджет: 0 сумов. Эффективность: бесконечная.", "Генеральному директору", "Кампания идёт"],
      ["SMM-менеджер", "Пишет пост в канал и первым ставит лайк.", "Директору по маркетингу", "1 лайк"],
      ["Финансовый директор", "Утверждает расходы: сервер, домен и чай.", "Генеральному директору", "В рамках бюджета"],
      ["Юрист", "Написал условия использования. И даже сам их прочитал.", "Генеральному директору", "Условия написаны"],
      ["Начальник отдела кадров", "Определил сотрудника года. Список кандидатов был коротким.", "Генеральному директору", "Командный дух отличный"],
      ["Заваривающий чай", "Самая важная должность. От неё зависит всё производство.", "Всем", "Закипает"],
    ],
  },
  en: {
    eyebrow: "About · team",
    heading: "The large, close-knit team behind RankWant",
    lede: "Twelve departments, twenty-four roles and one shared goal. We get along so well that meetings take a minute and nobody ever interrupts anybody.",
    stats: ["roles", "departments", "human", "disagreements"],
    filterLabel: "Filter by department",
    all: "All",
    search: "Find a role",
    serious: "Serious mode",
    count: "Showing {roles} roles · people holding them: {people}",
    empty: "No such role yet. If it opens, we know who gets it.",
    more: "Details",
    less: "Close",
    detail: [
      ["Teammates", "himself"],
      ["Holiday", "being planned (every year)"],
      ["Favourite meeting", "the cancelled one"],
    ],
    reportsTo: "Reports to",
    soloRole: "Founder and only developer",
    soloText:
      "RankWant is built by one person: backend, frontend, judge, design and content in one pair of hands. The twenty-four roles above are a joke; the work is real.",
    soloCount: "1 person, no jokes.",
    hireTitle: "Open positions",
    hireText:
      "Every role is taken for now — one candidate fitted all of them. If you want to contribute for real, the door is open.",
    hireCta: "Write on Telegram",
    photoAlt: "Photo of {name}",
    depts: [
      "Leadership",
      "Engineering",
      "Design",
      "Quality",
      "Infrastructure",
      "Content",
      "Support",
      "Marketing",
      "Finance",
      "Legal",
      "People",
      "Facilities",
    ],
    roles: [
      ["Founder and CEO", "Sets the strategy. The strategy: “we work today as well”.", "His conscience", "In the office"],
      ["Chair of the board", "Decides unanimously at every board meeting.", "The CEO", "Quorum reached"],
      ["Chief technology officer", "Makes the architecture decisions, then argues with himself.", "The CEO", "In review with himself"],
      ["Backend developer", "Expert in Django, Celery and three-hour searches for one comma.", "The CTO", "Writing code"],
      ["Frontend developer", "Moves a button 2 pixels left. Then back to the right.", "The CTO", "Writing code"],
      ["Judge engineer", "Punishes other people's code in the sandbox and his own outside it.", "The CTO", "Accepted"],
      ["Code reviewer", "Reads every pull request carefully. The author turns out to be familiar.", "The backend developer", "Approved"],
      ["Head of design", "Drew 12 styles because he could not pick one.", "The CEO", "Choosing a colour"],
      ["UX researcher", "Interviews users. The interviewee always agrees.", "The head of design", "Running an interview"],
      ["QA engineer", "Does not believe a developer who says “works on my machine”. Rightly.", "The CTO", "Found a bug"],
      ["Negative-test specialist", "Breaks everything on purpose and is glad when it breaks.", "The QA engineer", "Red = good"],
      ["DevOps engineer", "Presses the deploy button and holds his breath.", "The CTO", "CI green"],
      ["Night on-call", "Wakes up at two in the morning. It is known who woke him.", "The DevOps engineer", "No sleep"],
      ["Database administrator", "Adds an index. Takes a backup. Sleeps well (in theory).", "The DevOps engineer", "Backup exists"],
      ["Problem setter", "Started with A + B. Still on A + B.", "The head of content", "Writing"],
      ["Head of content", "Asks the problem setter for a deadline. Gets the answer: “tomorrow”.", "The CEO", "Deadline close"],
      ["Translator (10 languages)", "Knows Uzbek. Has promised to check the other nine.", "The head of content", "Not reviewed"],
      ["Support", "Answers requests 24/7, except while asleep.", "The CEO", "Online"],
      ["Chief marketing officer", "Advertising budget: 0 soums. Efficiency: infinite.", "The CEO", "Campaign running"],
      ["Social media manager", "Posts to the channel and is the first to like it.", "The CMO", "1 like"],
      ["Chief financial officer", "Approves the expenses: server, domain and tea.", "The CEO", "Within budget"],
      ["Lawyer", "Wrote the terms of use. And even read them himself.", "The CEO", "Terms written"],
      ["Head of people", "Named the employee of the year. The shortlist was short.", "The CEO", "Team spirit excellent"],
      ["Tea maker", "The most important role. All production depends on it.", "Everyone", "Boiling"],
    ],
  },
};
