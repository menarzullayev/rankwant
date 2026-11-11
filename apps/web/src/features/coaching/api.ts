/** Coach and student (ADR-0061 § 4). */

export type Person = { username: string; display_name: string };

export type CoachLink = {
  id: number;
  coach: Person;
  student: Person;
  status: "pending" | "active" | "rejected" | "ended";
  /** The student's consent for THIS coach to open their solutions. */
  can_view_attempts: boolean;
  created_at: string;
};

export type CoachLinks = {
  /** Where the reader is the student. */
  coaches: CoachLink[];
  /** Pending, where the reader is the coach. */
  requests: CoachLink[];
};

export type Recommendation = {
  id: number;
  coach: string;
  problem: string;
  problem_title: string;
  note: string;
  solved: boolean;
  created_at: string;
};

export type CoachStudent = {
  link: number;
  username: string;
  display_name: string;
  can_view_attempts: boolean;
  solved_count: number;
  rating_skills: number;
  streak: number;
  recent: {
    id: number;
    problem: string;
    problem_title: string;
    language: string;
    verdict: string;
    in_contest: boolean;
    created_at: string;
  }[];
  recommended: { problem: string; problem_title: string; solved: boolean }[];
};

/** One student may have at most this many coaches, asked or accepted
 *  (`coaching.services.MAX_COACHES`). */
export const MAX_COACHES = 3;
