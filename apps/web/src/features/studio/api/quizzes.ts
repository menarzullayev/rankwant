/** A teacher's question bank and quizzes (ADR-0061 § 5). */

import type { MessageKey } from "@/i18n/messages";
import type { QuestionKind } from "@/lib/api";

export type Folder = { id: number; name: string; question_count: number; created_at: string };

export type AuthorChoice = { id?: number; order: number; text: string; is_correct: boolean };

export type AuthorQuestion = {
  id: number;
  kind: QuestionKind;
  text: string;
  code: string;
  code_language: string;
  explanation: string;
  folder: number | null;
  choices: AuthorChoice[];
  answer_number: number | null;
  tolerance: number;
  answer_text: string;
  difficulty: number;
  /** Quizzes that use it. */
  used: number;
  created_at: string;
};

export type AuthorQuiz = {
  slug: string;
  title: string;
  description: string;
  time_limit_minutes: number | null;
  one_attempt: boolean;
  answers_after: string | null;
  questions: { id: number; kind: QuestionKind; text: string }[];
  attempt_count: number;
  assignment_count: number;
  created_at: string;
};

export const QUESTION_KINDS: readonly QuestionKind[] = ["single", "multiple", "number", "text"];

/** The name of each kind, in the reader's language. */
export const KIND_KEYS: Record<QuestionKind, MessageKey> = {
  single: "studio.questions.kind.single",
  multiple: "studio.questions.kind.multiple",
  number: "studio.questions.kind.number",
  text: "studio.questions.kind.text",
};
