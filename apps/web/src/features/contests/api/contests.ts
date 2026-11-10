/** Contests and other competition formats: arena, duels, tournaments, hackathons. */

import type { UserTitle } from "@/lib/identity";
import type { Question } from "@/lib/api/content";

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
  /** Xona hackingi yoqilganmi (ADR-0020) — raund davomida. */
  hack_room: boolean;
  /** Ochiq faza HOZIR ketyaptimi (musobaqa tugagan, oyna yopilmagan). */
  is_hack_open: boolean;
  /** Ochiq faza qachon yopiladi; `null` — bunday faza yo'q. Oyna vaqt
   *  bo'yicha ochilib yopiladi, ya'ni mijoz buni o'zi hisoblay olmaydi. */
  hack_open_until: string | null;
  /** Registrations. Counted once for the whole list, not per row. */
  participant_count: number;
};

export type ContestProblem = {
  index_letter: string;
  slug: string;
  title: string;
  points: number;
};

/** Someone who knew the problems beforehand (ADR-0055, part 2). */
export type InsiderRole = "author" | "tester" | "jury" | "organizer";

export type CrewPerson = { username: string; user_title: UserTitle | null };

export type ContestDetail = Contest & {
  description: string;
  /** Empty until the contest starts — a title is a hint (ADR-0055). */
  problems: ContestProblem[];
  problem_count: number;
  /** Who prepared the contest — told always. */
  crew: { authors: CrewPerson[]; testers: CrewPerson[]; jury: CrewPerson[] };
};

/** A question, the jury's answer, or an announcement (ADR-0055, part 3). */
export type Clarification = {
  id: number;
  /** Index letter; `null` — about the contest as a whole. */
  problem: string | null;
  /** Empty on an announcement. */
  question: string;
  answer: string;
  /** A quick answer, drawn in the reader's language. */
  answer_code: "" | "yes" | "no" | "read_statement" | "no_comment";
  is_public: boolean;
  is_announcement: boolean;
  mine: boolean;
  /** Filled for the moderators only. */
  author: string | null;
  created_at: string;
  answered_at: string | null;
};

export type ClarificationList = {
  moderator: boolean;
  can_ask: boolean;
  questions_left: number;
  results: Clarification[];
};

/** The signed-in visitor's own standing with a contest (`/viewer/`). */
export type ContestViewer = {
  /** "" for a participant. */
  role: InsiderRole | "";
  registered: boolean;
  /** An insider before the start: the problems are open to them and
   *  what they send is a testing attempt that counts nowhere. */
  testing: boolean;
  /** Filled while `testing`. */
  problems: ContestProblem[];
};

export type Standing = {
  rank: number;
  username: string;
  user_title: UserTitle | null;
  solved_count: number;
  penalty: number;
  /** IOI da tartibni AYNAN shu belgilaydi; ACM da yechilganlar soni. */
  total_score: number;
  /** Hack bali (ADR-0020) — `contest_room` da +100 / −50, ya'ni MANFIY
   *  bo'lishi mumkin. ACM jadvalida tartibga kirmaydi, alohida ustun. */
  hack_score: number;
  hacks_successful: number;
  hacks_unsuccessful: number;
  last_ac_at: string | null;
  /** Set on an insider's row: unrated, no place (`rank` is 0). */
  insider_role: InsiderRole | "";
};

export type Arena = {
  slug: string;
  title: string;
  description: string;
  start_at: string;
  end_at: string;
  seconds_per_question: number;
  question_count: number;
  participant_count: number;
  reward_qvant: number;
  is_running: boolean;
  is_finished: boolean;
};
export type ArenaDetail = Arena & {
  current_index: number | null;
  joined: boolean;
};
export type ArenaCurrent = {
  index: number;
  deadline: string;
  seconds_per_question: number;
  question: Question;
  answered: boolean;
};
export type ArenaStanding = {
  rank: number;
  username: string;
  display_name: string;
  score: number;
  correct_count: number;
  total_ms: number;
};

export type Duel = {
  slug: string;
  title: string;
  status: "open" | "accepted" | "finished" | "cancelled";
  challenger: string;
  opponent: string | null;
  problem_count: number;
  difficulty: number;
  duration_minutes: number;
  start_at: string;
  end_at: string;
  is_running: boolean;
  winner: string | null;
  challenger_solved: number;
  opponent_solved: number;
  is_draw: boolean;
  problems: {
    order: number;
    slug: string;
    title: string;
    difficulty: number;
  }[];
  created_at: string;
};
export type DuelRecord = { wins: number; draws: number; losses: number };

export type Tournament = {
  slug: string;
  title: string;
  description: string;
  start_at: string;
  end_at: string;
  stage_count: number;
  is_running: boolean;
  is_finished: boolean;
};
export type TournamentStage = {
  order: number;
  title: string;
  contest: string;
  contest_title: string;
  start_at: string;
  end_at: string;
  weight: number;
  is_finished: boolean;
};
export type TournamentDetail = Tournament & { stages: TournamentStage[] };
export type TournamentStanding = {
  rank: number;
  username: string;
  display_name: string;
  points: number;
  solved_total: number;
  stages_played: number;
};

export type Hackathon = {
  slug: string;
  title: string;
  description: string;
  start_at: string;
  submission_deadline: string;
  end_at: string;
  submission_count: number;
  accepts_submissions: boolean;
  is_finished: boolean;
};
export type HackathonSubmission = {
  id: number;
  username: string;
  team_name: string;
  title: string;
  description: string;
  repo_url: string;
  demo_url: string;
  submitted_at: string;
  score: number | null;
  feedback: string;
};

export type CalendarEvent = {
  kind: "contest" | "arena" | "tournament" | "hackathon" | "duel";
  slug: string;
  title: string;
  start_at: string;
  end_at: string;
  is_rated?: boolean;
  submission_deadline?: string;
};
