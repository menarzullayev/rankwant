/** UI satrlari — PRD P0-7: uz / ru / en.
 *
 * Masala MATNLARI tarjima qilinmaydi — muallif tilida qoladi (Codeforces modeli).
 */

export const LOCALES = ["uz", "ru", "en"] as const;
export type Locale = (typeof LOCALES)[number];
export const DEFAULT_LOCALE: Locale = "uz";

type Dict = Record<string, string>;

export const messages: Record<Locale, Dict> = {
  uz: {
    "nav.problems": "Masalalar",
    "nav.contests": "Musobaqalar",
    "nav.leaderboard": "Reyting",
    "nav.ratingInfo": "Reyting qanday hisoblanadi",
    "problems.title": "Masalalar arxivi",
    "problems.difficulty": "Qiyinlik",
    "problems.solved": "Yechilgan",
    "problems.topics": "Mavzular",
    "problems.limits": "Cheklovlar",
    "contests.title": "Musobaqalar",
    "contests.running": "Ketmoqda",
    "contests.finished": "Tugagan",
    "contests.upcoming": "Kelasi",
    "contests.rated": "Reytingli",
    "standings.title": "Natijalar jadvali",
    "standings.rank": "O'rin",
    "standings.user": "Foydalanuvchi",
    "standings.solved": "Yechildi",
    "standings.penalty": "Jarima",
    "standings.frozen": "Jadval muzlatilgan",
    "leaderboard.title": "Reyting",
    "leaderboard.skills": "Skills",
    "leaderboard.contest": "Contests",
    "empty": "Hozircha bo'sh",
  },
  ru: {
    "nav.problems": "Задачи",
    "nav.contests": "Соревнования",
    "nav.leaderboard": "Рейтинг",
    "nav.ratingInfo": "Как считается рейтинг",
    "problems.title": "Архив задач",
    "problems.difficulty": "Сложность",
    "problems.solved": "Решено",
    "problems.topics": "Темы",
    "problems.limits": "Ограничения",
    "contests.title": "Соревнования",
    "contests.running": "Идёт",
    "contests.finished": "Завершено",
    "contests.upcoming": "Предстоит",
    "contests.rated": "Рейтинговое",
    "standings.title": "Таблица результатов",
    "standings.rank": "Место",
    "standings.user": "Участник",
    "standings.solved": "Решено",
    "standings.penalty": "Штраф",
    "standings.frozen": "Таблица заморожена",
    "leaderboard.title": "Рейтинг",
    "leaderboard.skills": "Skills",
    "leaderboard.contest": "Contests",
    "empty": "Пока пусто",
  },
  en: {
    "nav.problems": "Problems",
    "nav.contests": "Contests",
    "nav.leaderboard": "Leaderboard",
    "nav.ratingInfo": "How rating works",
    "problems.title": "Problem archive",
    "problems.difficulty": "Difficulty",
    "problems.solved": "Solved",
    "problems.topics": "Topics",
    "problems.limits": "Limits",
    "contests.title": "Contests",
    "contests.running": "Running",
    "contests.finished": "Finished",
    "contests.upcoming": "Upcoming",
    "contests.rated": "Rated",
    "standings.title": "Standings",
    "standings.rank": "Rank",
    "standings.user": "User",
    "standings.solved": "Solved",
    "standings.penalty": "Penalty",
    "standings.frozen": "Standings are frozen",
    "leaderboard.title": "Leaderboard",
    "leaderboard.skills": "Skills",
    "leaderboard.contest": "Contests",
    "empty": "Nothing yet",
  },
};

export function t(locale: Locale, key: string): string {
  return messages[locale]?.[key] ?? messages[DEFAULT_LOCALE][key] ?? key;
}
