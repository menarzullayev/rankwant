/** Cached GETs for server components, grouped as `api.*`. Browser calls with a
 *  session live next to their domain types (`postJson`/`getJson` helpers). */

import { get, type Paginated } from "./client";
import type { AppearancePrefs } from "./account";
import type {
  Calendar,
  ContestRow,
  ProblemTile,
  RatingChange,
  RatingSeries,
  School,
  SolvedProblem,
  TopicStrength,
  UserPublic,
  UserStats,
} from "./users";
import type {
  ArchiveProgress,
  Attempt,
  Language,
  Problem,
  ProblemDetail,
  ProblemStats,
  Recommendation,
  Solver,
  Topic,
  TopicSkill,
} from "./problems";
import type {
  Arena,
  ArenaDetail,
  ArenaStanding,
  CalendarEvent,
  Contest,
  ContestDetail,
  Duel,
  Hackathon,
  HackathonSubmission,
  Standing,
  Tournament,
  TournamentDetail,
  TournamentStanding,
} from "./contests";
import type {
  Article,
  ArticleDetail,
  Post,
  PostDetail,
  Quiz,
  QuizDetail,
  Roadmap,
} from "./content";
import type {
  Notification,
  PlatformStats,
  RoadmapComment,
  RoadmapItem,
  SystemUpdate,
} from "./platform";
import type { Marathon, Quest, ShopItem, Wallet } from "./qvant";

export const api = {
  // Mehmon bosh sahifasi raqamlari — serverda 60 s keshlanadi.
  stats: () => get<PlatformStats>("/stats/", 60),
  problems: (query = "") => get<Paginated<Problem>>(`/problems/${query}`),
  problem: (slug: string) => get<ProblemDetail>(`/problems/${slug}/`),
  contests: () => get<Paginated<Contest>>("/contests/"),
  contest: (slug: string) => get<ContestDetail>(`/contests/${slug}/`),
  // Standings tez o'zgaradi — kesh qisqa
  standings: (slug: string) =>
    get<{ frozen: boolean; results: Standing[] }>(
      `/contests/${slug}/standings/`,
      5,
    ),
  leaderboard: (school?: string) =>
    get<Paginated<UserPublic>>(
      `/users/?ordering=-rating_skills${school ? `&school=${school}` : ""}`,
    ),
  school: (id: string) => get<School>(`/schools/${id}/`),
  /** Maktab katalogi — nom bo'yicha qidiruv, viloyat/tuman bo'yicha filtr.
   *  Katalog moderator to'ldiradi (ADR-0017), ya'ni bu ro'yxat to'liq emas:
   *  topilmagan maktab erkin matn bo'lib qoladi. */
  schools: (params: { q?: string; region?: string; district?: string } = {}) => {
    const query = new URLSearchParams();
    if (params.q) query.set("q", params.q);
    if (params.region) query.set("region", params.region);
    if (params.district) query.set("district", params.district);
    return get<Paginated<School>>(`/schools/${query.size ? `?${query}` : ""}`);
  },
  user: (username: string) => get<UserPublic>(`/users/${username}/`),
  // Qvant — Phase 1. Balans va questlar shaxsiy, kesh yo'q.
  wallet: () => get<Wallet>("/qvant/wallet/", 0),
  quests: () => get<Quest[]>("/qvant/quests/", 0),
  marathon: () => get<Marathon>("/qvant/marathon/", 0),
  // Sitemap uchun — faqat slug kerak, lekin ro'yxat endpointi to'liq
  // yozuvni beradi. Soatiga bir marta chaqiriladi (app/sitemap.ts).
  problemSlugs: (page: number) =>
    get<Paginated<{ slug: string }>>(
      `/problems/?page=${page}&page_size=100`,
      3600,
    ),
  contestSlugs: (page: number) =>
    get<Paginated<{ slug: string }>>(
      `/contests/?page=${page}&page_size=100`,
      3600,
    ),
  articleSlugs: (page: number) =>
    get<Paginated<{ slug: string }>>(
      `/articles/?page=${page}&page_size=100`,
      3600,
    ),
  postSlugs: (page: number) =>
    get<Paginated<{ slug: string }>>(
      `/posts/?page=${page}&page_size=100`,
      3600,
    ),
  shop: () => get<ShopItem[]>("/qvant/shop/", 30),
  // Bildirishnomalar shaxsiy va tez o'zgaradi — keshlanmaydi
  notifications: () => get<Paginated<Notification>>("/notifications/", 0),
  recommendations: () => get<Recommendation>("/problems/recommendation/", 0),
  posts: () => get<Paginated<Post>>("/posts/"),
  post: (slug: string) => get<PostDetail>(`/posts/${slug}/`),
  // Updates — ochiq arxiv, mehmon ham ko'radi (qaror 8-savol). Har yozuv
  // doimiy havola oladi, chunki Telegram kanal va Codeforces blog shunga
  // havola beradi. Kesh 60 s: yozuv qo'lda tasdiqlanadi, tez o'zgarmaydi.
  updates: (query = "") =>
    get<Paginated<SystemUpdate>>(`/updates/${query}`, 60),
  update: (id: number) => get<SystemUpdate>(`/updates/${id}/`, 60),
  /** Harakatga chaqiruvchi yozuvlar (`breaking`, `deprecated`) — arxiv
   *  tepasidagi alohida blok uchun. Sahifalangan ro'yxatdan ularni
   *  ajratib bo'lmaydi: kam uchraydi, ya'ni joriy sahifada umuman
   *  bo'lmasligi mumkin. Javob sahifalanmagan — ro'yxat qisqa. */
  updatesActionable: () => get<SystemUpdate[]>("/updates/actionable/", 60),
  // Sitemap uchun — faqat `id` kerak. Soatiga bir marta (app/sitemap.ts).
  updateIds: (page: number) =>
    get<Paginated<{ id: number }>>(
      `/updates/?page=${page}&page_size=100`,
      3600,
    ),
  // Yo'l xaritasi — mehmon o'qiydi, ovoz/izoh/taklif uchun kirish shart.
  // Kesh YO'Q: ovoz soni tugma bosilishi bilan o'zgaradi.
  // Saytning standart ko'rinishi (D37) — kamdan-kam o'zgaradi.
  siteAppearance: () =>
    get<{ appearance: AppearancePrefs }>("/appearance/", 300),
  roadmap: (query = "") =>
    get<Paginated<RoadmapItem>>(`/platform-roadmap/${query}`, 0),
  roadmapItem: (id: number) => get<RoadmapItem>(`/platform-roadmap/${id}/`, 0),
  // Izohlar sahifada SERVERDA chiziladi (SEO + JS'siz ham ko'rinadi);
  // yozish esa brauzerda sessiya bilan ketadi (`postRoadmapComment`).
  roadmapComments: (id: number) =>
    get<RoadmapComment[]>(`/platform-roadmap/${id}/comments/`, 0),
  roadmapIds: (page: number) =>
    get<Paginated<{ id: number }>>(
      `/platform-roadmap/?page=${page}&page_size=100`,
      3600,
    ),
  // O'z o'qish kontenti — ADR-0005 differensiatori. SEO uchun keshlanadi.
  articles: () => get<Paginated<Article>>("/articles/", 300),
  article: (slug: string) => get<ArticleDetail>(`/articles/${slug}/`, 300),
  roadmaps: () => get<Roadmap[]>("/roadmaps/", 300),
  // Progress foydalanuvchiga xos — SSR da `getWithSession` bilan olinadi.
  progress: () => get<ArchiveProgress>("/problems/progress/", 0),
  problemSolvers: (slug: string, ordering = "first") =>
    get<{ count: number; results: Solver[] }>(
      `/problems/${slug}/solvers/?ordering=${ordering}`,
    ),
  problemStats: (slug: string) =>
    get<ProblemStats>(`/problems/${slug}/stats/`, 30),
  /** Masalaning barcha urinishlari — ochiq. Manba begonaga ko'rinmaydi
   * (backend uni faqat egasiga qaytaradi). */
  problemAttempts: (slug: string, query = "") =>
    get<Paginated<Attempt>>(
      `/attempts/?problem=${encodeURIComponent(slug)}${query ? `&${query}` : ""}`,
      0,
    ),
  attempts: () => get<Paginated<Attempt>>("/attempts/", 0),
  // Tillar deyarli o'zgarmaydi — judge obrazi bilan bir manbadan (ADR-0004).
  languages: () => get<Paginated<Language>>("/languages/", 300),
  // Filtr paneli mavzularni TO'LIQ ko'rsatishi kerak — birinchi 25 tasi
  // emas, aks holda tanlab bo'lmaydigan yorliqlar paydo bo'lardi.
  topics: () => get<Paginated<Topic>>("/topics/?page_size=100", 300),
  topicSkills: () => get<{ topics: TopicSkill[] }>("/problems/skills/"),
  quizzes: () => get<Paginated<Quiz>>("/quizzes/", 60),
  quiz: (slug: string) => get<QuizDetail>(`/quizzes/${slug}/`, 60),
  arenas: () => get<Paginated<Arena>>("/arena/", 10),
  arena: (slug: string) => get<ArenaDetail>(`/arena/${slug}/`, 0),
  arenaStandings: (slug: string) =>
    get<{ results: ArenaStanding[] }>(`/arena/${slug}/standings/`, 0),
  duels: () => get<Paginated<Duel>>("/duels/", 0),
  duel: (slug: string) => get<Duel>(`/duels/${slug}/`, 0),
  tournaments: () => get<Paginated<Tournament>>("/tournaments/", 60),
  tournament: (slug: string) =>
    get<TournamentDetail>(`/tournaments/${slug}/`, 60),
  tournamentStandings: (slug: string) =>
    get<{ results: TournamentStanding[] }>(
      `/tournaments/${slug}/standings/`,
      30,
    ),
  hackathons: () => get<Paginated<Hackathon>>("/hackathons/", 60),
  hackathon: (slug: string) => get<Hackathon>(`/hackathons/${slug}/`, 60),
  hackathonSubmissions: (slug: string) =>
    get<{ results: HackathonSubmission[] }>(
      `/hackathons/${slug}/submissions/`,
      0,
    ),
  calendar: () => get<{ results: CalendarEvent[] }>("/calendar/", 60),
  algorithms: () => get<Paginated<Article>>("/articles/?kind=algorithm", 300),
  ratingHistory: (username: string) =>
    get<Paginated<RatingChange>>(`/users/${username}/rating-history/`, 30),
  solved: (username: string) =>
    get<Paginated<SolvedProblem>>(`/users/${username}/solved/`, 30),
  // Profil statistikasi — backend foydalanuvchi bo'yicha keshlaydi.
  userStats: (username: string) =>
    get<UserStats>(`/users/${username}/stats/`, 30),
  userCalendar: (username: string, year?: number) =>
    get<Calendar>(
      `/users/${username}/calendar/${year ? `?year=${year}` : ""}`,
      30,
    ),
  problemMap: (username: string) =>
    get<{ problems: ProblemTile[] }>(`/users/${username}/problem-map/`, 30),
  ratingSeries: (username: string) =>
    get<RatingSeries>(`/users/${username}/rating-series/`, 30),
  userTopics: (username: string) =>
    get<{ topics: TopicStrength[] }>(`/users/${username}/topics/`, 60),
  userContests: (username: string, query = "") =>
    get<Paginated<ContestRow>>(`/users/${username}/contests/${query}`, 0),
  solvedPage: (username: string, query = "") =>
    get<Paginated<SolvedProblem>>(`/users/${username}/solved/${query}`, 0),
  attemptsQuery: (query: string) =>
    get<Paginated<Attempt>>(`/attempts/${query}`, 0),
};
