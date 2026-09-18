/** Problem archive and judging: problems, attempts, custom runs, feedback. */

import { deleteJson, getJson, postJson, type Paginated } from "./client";
import type { UserTitle } from "./users";

export type Problem = {
  /** Ommaviy raqam — `#0431`. Qoralamada `null`. */
  code: number | null;
  is_solved: boolean;
  is_favourite: boolean;
  rating: { average: number | null; count: number };
  has_editorial: boolean;
  /** Oxirgi urinishim verdikti — hech urinmaganda `null`. */
  my_verdict: string | null;
  /** Masala sahifasi ochilishi soni. */
  view_count: number;
  /** Yechilgan / urinilgan, foizda. Urinish bo'lmasa `null`. */
  success_rate: number | null;
  /** Judge tekshira oladimi. Import qilingan masalalarning bir qismida
   * hali test yo'q va ularga yuborish qabul qilinmaydi. */
  has_tests: boolean;
  slug: string;
  title: string;
  difficulty: number;
  level: string;
  level_label: string;
  topics: string[];
  solved_count: number;
  attempt_count: number;
  likes_count: number;
  dislikes_count: number;
  author: {
    username: string;
    display_name: string;
    has_profile: boolean;
  } | null;
};

export type Sample = { order: number; input: string; expected: string };

/** Masalada ruxsat etilgan til — limitlari allaqachon hisoblangan. */
export type ProblemLanguage = {
  code: string;
  name: string;
  version: string;
  time_limit_ms: number;
  memory_limit_kb: number;
  code_template: string;
};

export type SimilarProblem = {
  slug: string;
  title: string;
  difficulty: number;
  level: string;
  level_label: string;
  score: number;
};

export type Attachment = { name: string; url: string; size_bytes: number };

/** ADR-0013: `access` tahlil qaysi asosda ochilganini aytadi. */
export type EditorialState = {
  available: boolean;
  access: "anonymous" | "locked" | "free" | "solved" | "purchased" | "staff";
  price: number;
};

export type ProblemDetail = Problem & {
  samples: Sample[];
  statement: string;
  input_format: string;
  output_format: string;
  note: string;
  /** Ochilmagan bo'lsa serverdan bo'sh keladi — yashirin matn yo'q. */
  editorial: string;
  editorial_state: EditorialState;
  /** `has_profile` — nofaol import mualliflarining profil sahifasi yo'q. */
  author: {
    username: string;
    display_name: string;
    has_profile: boolean;
  } | null;
  rating: { average: number | null; count: number };
  my_rating: number | null;
  is_favourite: boolean;
  statement_locale: string;
  time_limit_ms: number;
  memory_limit_kb: number;
  checker_type: string;
  languages: ProblemLanguage[];
  similar: SimilarProblem[];
  attachments: Attachment[];
  votes: { up: number; down: number; mine: number };
  image: string;
  partial_scoring: boolean;
  /** Import qilingan arxivning xom reytingi (KEP 100–2400). */
  source_rating: number | null;
  source: string;
  source_url: string;
};

export type Recommendation = {
  target_difficulty: number;
  results: Problem[];
};

export type ProblemStats = {
  total: number;
  verdicts: { verdict: string; count: number }[];
  languages: { language: string; count: number; solved: number }[];
  /** Har til uchun eng tez AC. Tillar aralashtirilmaydi. */
  fastest: {
    language: string;
    username: string;
    time_ms: number;
    memory_kb: number;
    created_at: string;
  }[];
};

/** Mavzu kesimidagi kuch. `stuck` — urinilgan, lekin yechilmagan. */
export type TopicSkill = {
  slug: string;
  label: string;
  total: number;
  solved: number;
  stuck: number;
  rating: number;
};

export type Solver = {
  username: string;
  rating_skills: number;
  language: string;
  time_ms: number;
  memory_kb: number;
  /** Yuborilgan manba uzunligi, belgi. */
  code_length: number;
  /** AC gacha bo'lgan urinishlar soni. */
  attempts: number;
  solved_at: string;
};

export type ArchiveProgress = {
  levels: { code: string; label: string; total: number; solved: number }[];
  total: number;
  solved: number;
};

/** Urinishlar ro'yxatidagi filtrlar — KEP dagi kabi.
 *
 * `[so'rov qiymati, yorliq kaliti]`. So'rov qiymati vergulli bo'lishi
 * mumkin: `RE` ikkiga ajratilgandan keyin bitta «Bajarilishda xato»
 * filtri eski qatorlarni ham, yangi `RE_SIGNAL`/`RE_EXIT` ni ham
 * topishi kerak. Yorliq esa `verdict.<KOD>` orqali tarjima qilinadi. */
export const VERDICT_FILTERS = [
  ["AC", "verdict.AC"],
  ["WA", "verdict.WA"],
  ["PE", "verdict.PE"],
  ["HACKED", "verdict.HACKED"],
  ["TLE", "verdict.TLE"],
  ["MLE", "verdict.MLE"],
  ["RE,RE_SIGNAL,RE_EXIT", "verdict.RE"],
  ["CE", "verdict.CE"],
] as const;

export type Attempt = {
  id: number;
  username: string;
  user_title: UserTitle | null;
  problem: string;
  /** Musobaqa slug'i — musobaqadan tashqarida `null`. Hack yuzasi
   *  masalani qaysi musobaqada lock qilishni shundan biladi. */
  contest: string | null;
  language: string;
  verdict: string;
  score: number;
  time_ms: number;
  memory_kb: number;
  failed_test_index: number | null;
  created_at: string;
  judged_at: string | null;
  /** Yuborilgan manba uzunligi, belgi. Kodning o'zi emas. */
  source_size: number;
};

export type Topic = {
  slug: string;
  name_uz: string;
  name_ru: string;
  name_en: string;
  parent: string | null;
  problem_count: number;
};

export type Language = { code: string; name: string; version: string };

export type TestResult = {
  index: number;
  verdict: string;
  time_ms: number;
  memory_kb: number;
};

/** `source_code` va `compile_output` faqat urinish egasiga va xodimga
 * qaytariladi (backend IDOR himoyasi), shuning uchun ixtiyoriy. */
export type AttemptDetail = Attempt & {
  source_code?: string;
  compile_output?: string;
  test_results: TestResult[];
};

export type CustomRun = {
  id: number;
  language: string;
  verdict: string;
  stdout: string;
  compile_output: string;
  time_ms: number;
  memory_kb: number;
  created_at: string;
  judged_at: string | null;
};

/** Submit. Javob `PENDING` bilan qaytadi — verdikt keyin pollinglanadi. */
export function submitAttempt(body: {
  problem: string;
  language: string;
  source_code: string;
  contest?: string;
}): Promise<Attempt> {
  return postJson<Attempt>("/attempts/", body);
}

export const fetchAttempt = (id: number) =>
  getJson<AttemptDetail>(`/attempts/${id}/`);

/** The whole judge catalog in one page. Language pickers read only the first
 * page, and the API pages at 25 (`core/pagination.py`): once the catalog grew
 * past that, ten languages silently dropped out of them, Python 3.13 among them. */
export const LANGUAGES_PATH = "/languages/?page_size=100";

/** Generator uchun til ro'yxati — mijozda, faqat hack formasi ochilganda. */
export const fetchLanguages = () =>
  getJson<Paginated<Language>>(LANGUAGES_PATH);

export const fetchProblemAttempts = (slug: string, username?: string) =>
  getJson<Paginated<Attempt>>(
    `/attempts/?problem=${encodeURIComponent(slug)}` +
      (username ? `&username=${encodeURIComponent(username)}` : ""),
  );

/** PRD P0-4 — o'z kiritmasi bilan sinash. Urinish tarixiga tushmaydi. */
export function runCustomTest(body: {
  language: string;
  source_code: string;
  stdin: string;
}): Promise<CustomRun> {
  return postJson<CustomRun>("/custom-test/", body);
}

export const fetchCustomRun = (id: number) =>
  getJson<CustomRun>(`/custom-test/${id}/`);

export const setFavourite = (slug: string, on: boolean) =>
  on
    ? postJson<{ is_favourite: boolean }>(`/problems/${slug}/favourite/`, {})
    : deleteJson<{ is_favourite: boolean }>(`/problems/${slug}/favourite/`);

/** Nuqson sabablari: qiymat (API'ga ketadi) + tarjima KALITI.
 *
 * Ilgari ikkinchi element tayyor o'zbekcha matn edi, ya'ni sabablar
 * ro'yxati 9 tilda ham o'zbekcha ko'rinardi. Endi u `t()` kaliti:
 * tarjima `locales/` da, kod esa faqat kalitni biladi.
 *
 * DIQQAT: kalitlarni bu yerda o'zgartirsangiz, `uz.ts` dagi
 * `report.reason.*` kalitlarini ham yangilang — `check_i18n.py` buni
 * tutadi, lekin sababini bilish uchun shu izoh kerak. */
export const REPORT_REASONS = [
  ["statement", "report.reason.statement"],
  ["tests", "report.reason.tests"],
  ["translation", "report.reason.translation"],
  ["duplicate", "report.reason.duplicate"],
  ["other", "report.reason.other"],
] as const;

export const reportProblem = (slug: string, reason: string, comment: string) =>
  postJson<{ reported: boolean }>(`/problems/${slug}/report/`, {
    reason,
    comment,
  });

export const voteProblem = (slug: string, value: -1 | 0 | 1) =>
  postJson<{ up: number; down: number; mine: number }>(
    `/problems/${slug}/vote/`,
    {
      value,
    },
  );

export const unlockEditorial = (slug: string) =>
  postJson<{ editorial: string; price: number }>(
    `/problems/${slug}/editorial/`,
    {},
  );

export const rateProblem = (slug: string, score: number) =>
  postJson<{ average: number | null; count: number; my_rating: number }>(
    `/problems/${slug}/rate/`,
    { score },
  );
