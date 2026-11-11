/** Reading and learning content: posts, articles, roadmaps, quizzes, classrooms. */

export type Post = {
  slug: string;
  kind: string;
  title: string;
  /** The text's language; Uzbek follows the reader's alphabet (ADR-0059). */
  locale: string;
  summary: string;
  /** Cover image for the home page carousel; empty when the post has none. */
  cover_url: string;
  author: string | null;
  published_at: string;
};

export type PostDetail = Post & { body: string };

export type Article = {
  slug: string;
  kind: "article" | "algorithm";
  title: string;
  /** The text's language; Uzbek follows the reader's alphabet (ADR-0059). */
  locale: string;
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
  /** The text's language; Uzbek follows the reader's alphabet (ADR-0059). */
  locale: string;
  description: string;
  /** `general` or `olympiad` (ADR-0060 § 2.4). */
  track: string;
  section_count: number;
  step_count: number;
  /** Traektoriyaning nechta masalasi yechilgan (mehmonda 0). */
  solved_steps: number;
  /** The first step this reader has not done; `null` when the path is finished. */
  next_step: RoadmapNextStep | null;
};

/** A chapter of a study plan with the reader's progress in it. */
export type RoadmapSection = {
  order: number;
  title: string;
  description: string;
  locale: string;
  step_count: number;
  solved_steps: number;
};

export type RoadmapDetail = Roadmap & {
  /** Steps outside every section — in a plan without sections, all of them. */
  steps: RoadmapNextStep[];
  sections: RoadmapSection[];
};

export type RoadmapSectionStep = {
  order: number;
  title: string;
  problem: string | null;
  article: string | null;
  difficulty: number | null;
  is_optional: boolean;
  solved: boolean;
};

export type RoadmapSectionPage = {
  roadmap: { slug: string; title: string; locale: string };
  section: RoadmapSection;
  steps: RoadmapSectionStep[];
  previous: number | null;
  next: number | null;
};

export type RoadmapNextStep = {
  order: number;
  title: string;
  /** Slug of the linked article or problem; a step has at most one of each. */
  article: string | null;
  problem: string | null;
  is_optional: boolean;
};

export type Choice = { id: number; order: number; text: string };
export type Question = {
  id: number;
  text: string;
  difficulty: number;
  topics: string[];
  choices: Choice[];
};
export type Quiz = {
  slug: string;
  title: string;
  description: string;
  reward_qvant: number;
  question_count: number;
  best_score: number | null;
  created_at: string;
};
export type QuizDetail = Quiz & { questions: Question[] };
export type QuizResult = {
  id: number;
  score: number;
  total: number;
  qvant_awarded: number;
  review: {
    question_id: number;
    chosen: number | null;
    correct: number | null;
    is_correct: boolean;
    explanation: string;
  }[];
};

export type ClassroomJoinMode = "instant" | "approval";
/** The reader's place in the classroom; `""` — none (ADR-0061 § 3). */
export type ClassroomRole = "owner" | "assistant" | "student" | "";
export type Classroom = {
  slug: string;
  name: string;
  description: string;
  owner: string;
  /** Students only: assistants are not seats. */
  member_count: number;
  created_at: string;
  join_mode: ClassroomJoinMode;
  my_role: ClassroomRole;
};
export type ClassroomMember = {
  username: string;
  role: "assistant" | "student";
  rating_skills: number;
  joined_at: string;
};
/** The owner gets the code; the owner and assistants get the members. */
export type ClassroomDetail = Classroom & {
  join_code?: string;
  is_active?: boolean;
  members?: ClassroomMember[];
  pending_count?: number;
};
export type ClassroomJoinRequest = {
  id: number;
  username: string;
  rating_skills: number;
  status: "pending" | "approved" | "rejected";
  created_at: string;
};
/** The classroom plus `status`: `member` — in it now (201); `pending` —
 *  waiting for the teacher (202). */
export type ClassroomJoinResult = Classroom & { status: "member" | "pending" };
/** What an invite link shows before joining. */
export type ClassroomInvite = {
  slug: string;
  name: string;
  owner: string;
  join_mode: ClassroomJoinMode;
  member_count: number;
  state: "member" | "pending" | "owner" | "";
};
export type Assignment = {
  id: number;
  title: string;
  description: string;
  problems: string[];
  /** A course given to the class (ADR-0056 part 8). */
  course: AssignmentCourse | null;
  due_at: string | null;
  created_at: string;
};
export type AssignmentCourse = {
  slug: string;
  title: string;
  /** The title's language (ADR-0059). */
  locale: string;
  access: string;
  price_qvant: number;
};
