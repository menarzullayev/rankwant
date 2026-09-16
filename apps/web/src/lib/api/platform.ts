/** Platform-wide: stats, search, notifications, updates and the public roadmap. */

import { deleteJson, getJson, postJson, type Paginated } from "./client";

export type PlatformStats = {
  users: number;
  problems: number;
  contests: number;
  attempts: number;
  statement_locales: string[];
};

export type Notification = {
  id: number;
  kind: string;
  title: string;
  body: string;
  is_read: boolean;
  created_at: string;
};

/** Updates — platforma o'zgarishlari (changelog).
 *
 * `blog.Post` dan ATAYLAB ajratilgan: `blog` — muharrir kontenti, bu esa
 * nima o'zgargani haqidagi yozuv (manbasi GitHub, 10 turga tasniflanadi).
 */
export type UpdateKind =
  | "new"
  | "improved"
  | "fixed"
  | "performance"
  | "security"
  | "design"
  | "content"
  | "infrastructure"
  | "breaking"
  | "deprecated";

export type UpdateModule =
  | "problems"
  | "contests"
  | "arena"
  | "judge"
  | "ratings"
  | "qvant"
  | "profile"
  | "classroom"
  | "quizzes"
  | "content"
  | "design"
  | "core";

/** Filtr qatori tartibi — `apps/api/updates/models.py` `Kind` bilan bir xil.
 *  Ikkita oxirgisi (`breaking`, `deprecated`) harakatga chaqiradi va shu
 *  sababli ro'yxat oxirida ham, alohida guruhda ham turadi. */
export const UPDATE_KINDS: UpdateKind[] = [
  "new",
  "improved",
  "fixed",
  "performance",
  "security",
  "design",
  "content",
  "infrastructure",
  "breaking",
  "deprecated",
];

export type SystemUpdate = {
  id: number;
  kind: UpdateKind;
  module: UpdateModule;
  /** Ro'yxatda har doim `published`. Batafsil sahifada `withdrawn` ham
   *  bo'ladi: nashrdan olingan yozuv o'chirilmaydi va havolasi ishlaydi
   *  (qaror 20), lekin sahifa buni aytishi kerak. */
  status: "draft" | "published" | "withdrawn";
  /** Semantik versiya — bo'sh bo'lishi mumkin (`v1.4.0`). */
  version: string;
  /** So'ralgan tildagi matn; tarjima bo'lmasa kanonik o'zbekcha. */
  title: string;
  body: string;
  image: string;
  /** O'zgarish chiqqan sana (`YYYY-MM-DD`). */
  released_at: string;
  published_at: string | null;
  /** GitHub havolasi — bo'sh bo'lishi mumkin. */
  source_url: string;
  /** Buzuvchi yoki olib tashlanadi — foydalanuvchi biror narsa qilishi kerak. */
  is_actionable: boolean;
  /** Mehmon uchun `null`: o'qilmagan holat faqat kirganlarga tegishli. */
  is_read: boolean | null;
  /** Matn tarjima qilinganmi yoki kanonik o'zbekcha ko'rsatilganmi. */
  is_translated: boolean;
};

/** O'qilmagan yozuvlar soni — nav chipi va qo'ng'iroq uchun. */
export type UpdateUnread = { count: number; actionable: number };

/** Yo'l xaritasi — kelajak haqidagi reja bandi.
 *
 *  `updates` (o'tmish) dan ATAYLAB ajratilgan; bog'lanish `update`
 *  maydoni orqali — chiqarilgan band changelog yozuviga havola qiladi.
 *
 *  ⚠️ Manzil `/platform-roadmap/`, `/roadmap/` EMAS: `/roadmaps/`
 *  (ta'lim traektoriyasi) allaqachon bor va bir harf farq qiladigan
 *  ikki manzil adashtiradi.
 */
export type RoadmapStatus =
  | "suggested"
  | "planned"
  | "in_progress"
  | "released"
  | "declined";

/** Kanban ustunlari tartibi — `apps/api/roadmap/models.py` `COLUMNS` bilan
 *  bir xil. `declined` ATAYLAB yo'q: u ro'yxatda bor, lekin ustun emas
 *  (rad etilganlar taxtani to'ldirib, "nima rejalashtirilgan" savolini
 *  xiralashtiradi). */
export const ROADMAP_COLUMNS: RoadmapStatus[] = [
  "suggested",
  "planned",
  "in_progress",
  "released",
];

export type RoadmapItem = {
  id: number;
  title: string;
  body: string;
  status: RoadmapStatus;
  /** Chorak darajasidagi muddat (`2026-Q4`, `Sentabr oxiri`) — sana emas. */
  target_quarter: string;
  /** Ovoz soni. Nom `votes` emas: u API da ham, modelda ham
   *  annotatsiya/teskari bog'lanish nomi bilan to'qnashardi. */
  vote_count: number;
  /** Joriy foydalanuvchi ovoz berganmi. Mehmon uchun har doim `false`. */
  has_voted: boolean;
  comment_count: number;
  author: string | null;
  author_name: string | null;
  /** Chiqarilganda bog'langan changelog yozuvi — havola `/updates/<id>`. */
  update_id: number | null;
  update_title: string | null;
  planned_at: string | null;
  started_at: string | null;
  released_at: string | null;
  created_at: string;
};

export type RoadmapComment = {
  id: number;
  body: string;
  author: string | null;
  author_name: string | null;
  is_mine: boolean;
  created_at: string;
};

export type RoadmapVoteResult = { voted: boolean; vote_count: number };

export type SearchResult = {
  q: string;
  problems: { slug: string; title: string; difficulty: number }[];
  users: { username: string; display_name: string; rating_skills: number }[];
  articles: { slug: string; title: string; kind: string }[];
  contests: { slug: string; title: string; start_at: string }[];
};

/** O'qilmagan o'zgarishlar — qo'ng'iroq paneli uchun.
 *
 *  Faqat KIRGAN foydalanuvchi chaqirsin: endpoint `IsAuthenticated`
 *  talab qiladi, ya'ni mehmon uchun 401 qaytadi va brauzer uni konsolga
 *  xato qilib yozadi (Lighthouse `errors-in-console`). Shu sababli
 *  chaqiruv `SessionContext`dagi `user` bo'lgandagina bo'ladi. */
export const fetchUpdateUnread = (query = "") =>
  getJson<Paginated<SystemUpdate>>(`/updates/unread/${query}`);

export const fetchUpdateUnreadCount = () =>
  getJson<UpdateUnread>("/updates/unread-count/");

/** O'qilgan deb belgilash. `ids` berilmasa — hammasi ("Hammasi o'qildi"). */
export const markUpdatesRead = (ids?: number[]) =>
  postJson<{ updated: number }>("/updates/mark-read/", ids ? { ids } : {});

/** Ovoz berish yoki qaytarib olish — bitta manzil, `POST`/`DELETE`.
 *
 *  `DELETE` ni tanlash `POST` + `{"on": false}` dan yaxshiroq: amal
 *  idempotent bo'ladi va "o'chirish" ni niyat bilan aytadi. Xuddi
 *  `setFavourite` kabi. */
export const voteRoadmap = (id: number, on: boolean) =>
  on
    ? postJson<RoadmapVoteResult>(`/platform-roadmap/${id}/vote/`, {})
    : deleteJson<RoadmapVoteResult>(`/platform-roadmap/${id}/vote/`);

export const fetchRoadmapComments = (id: number) =>
  getJson<RoadmapComment[]>(`/platform-roadmap/${id}/comments/`);

export const postRoadmapComment = (id: number, body: string) =>
  postJson<RoadmapComment>(`/platform-roadmap/${id}/comments/`, { body });

/** Taklif berish. Holatni server `suggested` qilib qo'yadi — yuborilmaydi. */
export const suggestRoadmapItem = (title: string, body: string) =>
  postJson<RoadmapItem>("/platform-roadmap/", { title, body });

/** Mening takliflarim — rad etilganlari ham (javobsiz qolmasin). */
export const fetchMyRoadmapItems = () =>
  getJson<RoadmapItem[]>("/platform-roadmap/mine/");
