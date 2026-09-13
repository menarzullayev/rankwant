/** Admin bo'limlari — oddiy modul: server sahifa ham, client nav ham import qiladi.
 *  ("use client" modulidan eksport qilingan massiv serverda client-reference bo'lib qoladi.) */
export const ADMIN_SECTIONS = [
  { href: "/admin/problems", label: "Masalalar" },
  { href: "/admin/reports", label: "Nuqson xabarlari" },
  { href: "/admin/contests", label: "Musobaqalar" },
  { href: "/admin/questions", label: "Savol banki" },
  { href: "/admin/quizzes", label: "Testlar" },
  { href: "/admin/arena", label: "Arena" },
  { href: "/admin/tournaments", label: "Chempionat" },
  { href: "/admin/hackathons", label: "Hakaton" },
  { href: "/admin/duels", label: "Duel" },
  { href: "/admin/articles", label: "Maqolalar" },
  { href: "/admin/roadmaps", label: "Traektoriya" },
  { href: "/admin/posts", label: "Yangiliklar" },
  // Changelog va yo'l xaritasi: o'tmish va kelajak — shuning uchun yonma-yon.
  // ⚠️ "Traektoriya" (`/admin/roadmaps`) BOSHQA narsa — ta'lim yo'li.
  { href: "/admin/updates", label: "O'zgarishlar" },
  { href: "/admin/platform-roadmap", label: "Yo'l xaritasi" },
  { href: "/admin/roadmap-comments", label: "Reja izohlari" },
  { href: "/admin/quests", label: "Questlar" },
  { href: "/admin/shop", label: "Do'kon" },
  { href: "/admin/users", label: "Foydalanuvchilar" },
  { href: "/admin/analytics", label: "Analitika" },
] as const;
