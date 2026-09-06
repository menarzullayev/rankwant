/** RankWant API mijozi.
 *
 * SSR da server tomonda chaqiriladi — session cookie uzatiladi
 * (ADR-0008: birinchi tomon web uchun cookie, PAT emas).
 */

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000/api/v1";

export type Paginated<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export type Problem = {
  slug: string;
  title: string;
  difficulty: number;
  level: string;
  level_label: string;
  topics: string[];
  solved_count: number;
  attempt_count: number;
};

export type ProblemDetail = Problem & {
  statement: string;
  statement_locale: string;
  time_limit_ms: number;
  memory_limit_kb: number;
  checker_type: string;
};

export type Contest = {
  slug: string;
  title: string;
  start_at: string;
  end_at: string;
  scoring_type: string;
  is_rated: boolean;
  is_running: boolean;
  is_finished: boolean;
  is_frozen: boolean;
};

export type Standing = {
  rank: number;
  username: string;
  solved_count: number;
  penalty: number;
  last_ac_at: string | null;
};

export type UserPublic = {
  username: string;
  display_name: string;
  rating_skills: number;
  rating_contest: number;
  /** Phase 1 da yoqildi — ADR-0006 fazali ochilish */
  rating_activity: number;
  streak_count: number;
  date_joined: string;
};

export type Wallet = {
  balance: number;
  earned_today: number;
  remaining_today: number;
};

export type Quest = {
  code: string;
  type: "daily" | "weekly" | "achievement";
  title_uz: string;
  reward: number;
  done: boolean;
};

export type Notification = {
  id: number;
  kind: string;
  title: string;
  body: string;
  is_read: boolean;
  created_at: string;
};

export type Post = {
  slug: string;
  kind: string;
  title: string;
  summary: string;
  author: string | null;
  published_at: string;
};

export type PostDetail = Post & { body: string };

export type Recommendation = {
  target_difficulty: number;
  results: Problem[];
};

export type Article = {
  slug: string;
  title: string;
  summary: string;
  difficulty: number;
  topics: string[];
  reading_minutes: number;
  problem_count: number;
};

export type LinkedProblem = {
  slug: string;
  title: string;
  difficulty: number;
  role: string;
};

export type ArticleDetail = Article & {
  body: string;
  author: string | null;
  problems: LinkedProblem[];
};

export type Roadmap = {
  slug: string;
  title: string;
  description: string;
  step_count: number;
};

export type ShopItem = {
  code: string;
  category: string;
  title_uz: string;
  price: number;
  is_consumable: boolean;
  owned: boolean;
};

class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
  ) {
    super(message);
  }
}

async function get<T>(path: string, revalidate = 30): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    next: { revalidate },
    headers: { Accept: "application/json" },
  });
  if (!res.ok) {
    let code = "error";
    let message = res.statusText;
    try {
      const body = await res.json();
      code = body?.error?.code ?? code;
      message = body?.error?.message ?? message;
    } catch {
      /* javob JSON emas */
    }
    throw new ApiError(res.status, code, message);
  }
  return (await res.json()) as T;
}

export const api = {
  problems: (query = "") => get<Paginated<Problem>>(`/problems/${query}`),
  problem: (slug: string) => get<ProblemDetail>(`/problems/${slug}/`),
  contests: () => get<Paginated<Contest>>("/contests/"),
  contest: (slug: string) => get<Contest & { problems: unknown[] }>(`/contests/${slug}/`),
  // Standings tez o'zgaradi — kesh qisqa
  standings: (slug: string) =>
    get<{ frozen: boolean; results: Standing[] }>(`/contests/${slug}/standings/`, 5),
  leaderboard: () => get<Paginated<UserPublic>>("/users/?ordering=-rating_skills"),
  user: (username: string) => get<UserPublic>(`/users/${username}/`),
  // Qvant — Phase 1. Balans va questlar shaxsiy, kesh yo'q.
  wallet: () => get<Wallet>("/qvant/wallet/", 0),
  quests: () => get<Quest[]>("/qvant/quests/", 0),
  shop: () => get<ShopItem[]>("/qvant/shop/", 30),
  // Bildirishnomalar shaxsiy va tez o'zgaradi — keshlanmaydi
  notifications: () => get<Paginated<Notification>>("/notifications/", 0),
  recommendations: () => get<Recommendation>("/problems/recommendation/", 0),
  posts: () => get<Paginated<Post>>("/posts/"),
  post: (slug: string) => get<PostDetail>(`/posts/${slug}/`),
  // O'z o'qish kontenti — ADR-0005 differensiatori. SEO uchun keshlanadi.
  articles: () => get<Paginated<Article>>("/articles/", 300),
  article: (slug: string) => get<ArticleDetail>(`/articles/${slug}/`, 300),
  roadmaps: () => get<Roadmap[]>("/roadmaps/", 300),
};

export { ApiError };
