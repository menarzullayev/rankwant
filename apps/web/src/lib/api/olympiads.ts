/** The olympiad archive (ADR-0062 § 2.6): seasons, events, statements, results. */

export type OlympiadRoute = { code: string; title: string; description: string; kind: string; order: number };

export type OlympiadRouteMembership = {
  route_code: string;
  order: number | null;
  label: string | null;
  node_style: string | null;
};

export type OlympiadEventCard = {
  slug: string;
  code: string;
  title: string;
  short_title: string;
  summary: string;
  /** `international`, `selection`, `stage`, `training`, `unofficial`. */
  kind: string;
  /** `completed`, `scheduled`, `tba`. */
  status: string;
  start_date: string | null;
  end_date: string | null;
  date_label: string;
  location: string;
  is_featured: boolean;
  routes: OlympiadRouteMembership[];
  task_count: number;
  result_count: number;
};

export type OlympiadSeason = {
  slug: string;
  title: string;
  summary: string;
  start_date: string | null;
  end_date: string | null;
  routes: OlympiadRoute[];
  events: OlympiadEventCard[];
};

export type OlympiadTaskRow = {
  slug: string;
  code: string;
  title: string;
  original_title: string;
  problem_type: string;
  /** Copied from KEP.uz: shown with its source and a "no partnership" note. */
  from_kep: boolean;
};

export type OlympiadResult = {
  participant: string;
  full_name: string;
  country_code: string;
  rank: number | null;
  score: number | null;
  medal: string;
  is_local: boolean;
};

export type OlympiadResource = { type: string; title: string; url: string; is_official: boolean | null };

export type OlympiadEvent = OlympiadEventCard & {
  season: string;
  description: string;
  mode: string;
  platform: string;
  organizer: string;
  eligibility: string;
  resources: OlympiadResource[];
  sets: { slug: string; title: string; description: string; tasks: OlympiadTaskRow[] }[];
  results: OlympiadResult[];
  /** RankWant contests that mirror this event (ADR-0063). */
  mirror_contests: { slug: string; title: string; start_at: string }[];
};

export type OlympiadLink = { kind: string; title: string; url: string; platform: string; is_official: boolean | null };

export type OlympiadTask = {
  slug: string;
  code: string;
  title: string;
  original_title: string;
  statement: string;
  translation_status: string;
  problem_type: string;
  time_limit_ms: number | null;
  memory_limit_mb: number | null;
  max_score: number | null;
  tags: string[];
  links: OlympiadLink[];
  statement_pdf: string;
  from_kep: boolean;
  event: string;
  event_title: string;
  set_title: string;
  /** Our own copy of the problem, matched by its source. */
  practice_here: { slug: string; code: number | null; title: string }[];
};

export type OlympiadParticipant = {
  slug: string;
  full_name: string;
  country_code: string;
  results: {
    event: string;
    event_title: string;
    start_date: string | null;
    rank: number | null;
    score: number | null;
    medal: string;
  }[];
};
