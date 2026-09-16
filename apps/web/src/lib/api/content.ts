/** Reading and learning content: posts, articles, roadmaps, quizzes, classrooms. */

export type Post = {
  slug: string;
  kind: string;
  title: string;
  summary: string;
  author: string | null;
  published_at: string;
};

export type PostDetail = Post & { body: string };

export type Article = {
  slug: string;
  kind: "article" | "algorithm";
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
  /** Traektoriyaning nechta masalasi yechilgan (mehmonda 0). */
  solved_steps: number;
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

export type Classroom = {
  slug: string;
  name: string;
  description: string;
  owner: string;
  member_count: number;
  created_at: string;
};
export type ClassroomDetail = Classroom & {
  join_code?: string;
  is_active?: boolean;
  members?: {
    username: string;
    role: string;
    rating_skills: number;
    joined_at: string;
  }[];
};
export type Assignment = {
  id: number;
  title: string;
  description: string;
  problems: string[];
  due_at: string | null;
  created_at: string;
};
