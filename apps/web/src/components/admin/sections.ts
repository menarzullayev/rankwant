/** Admin bo'limlari — oddiy modul: server sahifa ham, client nav ham import qiladi.
 *  ("use client" modulidan eksport qilingan massiv serverda client-reference bo'lib qoladi.)
 *
 *  `label` EMAS, `labelKey`: matn `t(locale, ...)` orqali olinadi. Ilgari
 *  bu yerda tayyor o'zbekcha nom turardi va admin navigatsiyasi 9 tilda
 *  ham o'zbekcha chiqardi.
 */
export const ADMIN_SECTIONS = [
  { href: "/admin/problems", labelKey: "admin.section.problems" },
  { href: "/admin/reports", labelKey: "admin.section.reports" },
  { href: "/admin/contests", labelKey: "admin.section.contests" },
  { href: "/admin/questions", labelKey: "admin.section.questions" },
  { href: "/admin/quizzes", labelKey: "admin.section.quizzes" },
  { href: "/admin/arena", labelKey: "admin.section.arena" },
  { href: "/admin/tournaments", labelKey: "admin.section.tournaments" },
  { href: "/admin/hackathons", labelKey: "admin.section.hackathons" },
  { href: "/admin/duels", labelKey: "admin.section.duels" },
  { href: "/admin/articles", labelKey: "admin.section.articles" },
  { href: "/admin/roadmaps", labelKey: "admin.section.roadmaps" },
  { href: "/admin/posts", labelKey: "admin.section.posts" },
  // Changelog va yo'l xaritasi: o'tmish va kelajak — shuning uchun yonma-yon.
  // ⚠️ "Traektoriya" (`/admin/roadmaps`) BOSHQA narsa — ta'lim yo'li.
  { href: "/admin/updates", labelKey: "admin.section.updates" },
  { href: "/admin/platform-roadmap", labelKey: "admin.section.platformRoadmap" },
  { href: "/admin/roadmap-comments", labelKey: "admin.section.roadmapComments" },
  { href: "/admin/quests", labelKey: "admin.section.quests" },
  { href: "/admin/shop", labelKey: "admin.section.shop" },
  { href: "/admin/users", labelKey: "admin.section.users" },
  { href: "/admin/analytics", labelKey: "admin.section.analytics" },
  // Email kvota: «bugun qancha xat yuborish mumkin» — analitika yonida,
  // chunki ikkalasi ham jamlanma ko'rsatkich (CRUD emas).
  { href: "/admin/email-quota", labelKey: "admin.section.emailQuota" },
  { href: "/admin/kit", labelKey: "admin.section.kit" },
] as const;
