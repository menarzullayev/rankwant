/** The team page's own words — content, like the legal pages (`content/legal.ts`).
 *
 *  The page is a joke with a true line under it: every department and every
 *  title is held by the one person who builds the platform. The people,
 *  the departments and the titles live in the database and are managed from
 *  the admin panel (`/admin/team`); this file keeps only the sentences the
 *  page itself says. They are written in Uzbek, Russian and English; the
 *  other seven locales read the Uzbek text, as they do on the legal pages.
 */

export type TeamLocale = "uz" | "ru" | "en";

export function pickTeam(locale: string): TeamLocale {
  return locale === "ru" || locale === "en" ? locale : "uz";
}

/** `title_uz` / `title_ru` / `title_en` → the one for this page, falling
 *  back to Uzbek: a translation left blank in the admin panel must not
 *  leave a hole in the card. */
export function localized<T extends Record<string, unknown>>(
  row: T,
  field: string,
  locale: TeamLocale,
): string {
  const value = row[`${field}_${locale}`];
  if (typeof value === "string" && value.trim()) return value;
  const fallback = row[`${field}_uz`];
  return typeof fallback === "string" ? fallback : "";
}

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
  soloText: string;
  soloCount: string;
  coreTitle: string;
  contributorsTitle: string;
  contributorsLede: string;
  hireTitle: string;
  hireText: string;
  hireCta: string;
  /** `{name}` is replaced. */
  photoAlt: string;
  website: string;
  unavailable: string;
};

export const TEAM_TEXT: Record<TeamLocale, TeamText> = {
  uz: {
    eyebrow: "Biz haqimizda · jamoa",
    heading: "RankWant ortidagi katta, ahil jamoa",
    lede: "Bir nechta bo'lim, ko'plab lavozim va bitta umumiy maqsad. Jamoamiz shu qadar ahilki, majlislar bir daqiqada tugaydi va hech kim hech qachon bir-birining gapini bo'lmaydi.",
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
    soloText:
      "RankWant — bir kishi tomonidan qurilayotgan platforma: backend, frontend, judge, dizayn va kontent bitta qo'lda. Yuqoridagi lavozimlar hazil, ish esa haqiqiy.",
    soloCount: "1 kishi, hazilsiz.",
    coreTitle: "Asosiy jamoa",
    contributorsTitle: "Loyihaga hissa qo'shganlar",
    contributorsLede: "Bu yerda hazil yo'q: platformaga haqiqatan yordam bergan insonlar.",
    hireTitle: "Bo'sh o'rinlar",
    hireText:
      "Hozircha barcha lavozimlar band — bitta nomzod hammasiga mos keldi. Lekin haqiqiy hissa qo'shmoqchi bo'lsangiz, eshik ochiq.",
    hireCta: "Telegram'da yozish",
    photoAlt: "{name} rasmi",
    website: "Shaxsiy sayt",
    unavailable: "Jamoa ro'yxatini hozir yuklab bo'lmadi. Birozdan keyin qayta urinib ko'ring.",
  },
  ru: {
    eyebrow: "О нас · команда",
    heading: "Большая и дружная команда RankWant",
    lede: "Несколько отделов, множество должностей и одна общая цель. Мы настолько дружны, что совещания длятся минуту и никто никого не перебивает.",
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
    soloText:
      "RankWant — платформа, которую строит один человек: бэкенд, фронтенд, judge, дизайн и контент в одних руках. Должности выше — шутка, а работа настоящая.",
    soloCount: "1 человек, без шуток.",
    coreTitle: "Основная команда",
    contributorsTitle: "Те, кто помог проекту",
    contributorsLede: "Здесь без шуток: люди, которые действительно помогли платформе.",
    hireTitle: "Вакансии",
    hireText:
      "Сейчас все должности заняты — один кандидат подошёл на каждую. Но если хотите внести настоящий вклад, дверь открыта.",
    hireCta: "Написать в Telegram",
    photoAlt: "Фото: {name}",
    website: "Личный сайт",
    unavailable: "Сейчас не удалось загрузить список команды. Попробуйте чуть позже.",
  },
  en: {
    eyebrow: "About · team",
    heading: "The large, close-knit team behind RankWant",
    lede: "Several departments, many roles and one shared goal. We get along so well that meetings take a minute and nobody ever interrupts anybody.",
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
    soloText:
      "RankWant is built by one person: backend, frontend, judge, design and content in one pair of hands. The roles above are a joke; the work is real.",
    soloCount: "1 person, no jokes.",
    coreTitle: "Core team",
    contributorsTitle: "People who helped the project",
    contributorsLede: "No jokes here: people who really helped the platform.",
    hireTitle: "Open positions",
    hireText:
      "Every role is taken for now — one candidate fitted all of them. If you want to contribute for real, the door is open.",
    hireCta: "Write on Telegram",
    photoAlt: "Photo of {name}",
    website: "Personal site",
    unavailable: "The team list could not be loaded just now. Please try again in a moment.",
  },
};
