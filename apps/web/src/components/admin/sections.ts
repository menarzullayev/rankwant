/** Admin bo'limlari — oddiy modul: server sahifa ham, client nav ham import qiladi.
 *  ("use client" modulidan eksport qilingan massiv serverda client-reference bo'lib qoladi.) */
export const ADMIN_SECTIONS = [
  { href: "/admin/problems", label: "Masalalar" },
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
  { href: "/admin/quests", label: "Questlar" },
  { href: "/admin/shop", label: "Do'kon" },
  { href: "/admin/users", label: "Foydalanuvchilar" },
] as const;
