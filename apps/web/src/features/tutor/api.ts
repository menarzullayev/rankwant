import { deleteJson, getJson, postJson } from "@/lib/api";
import type { components } from "@/lib/api/generated/schema";

/** AI tutor (ADR-0065): one conversation per student and problem. */
export type TutorConversation = components["schemas"]["TutorConversation"];
export type TutorMessage = components["schemas"]["TutorMessage"];
export type TutorAsk = components["schemas"]["TutorAsk"];

const path = (slug: string) => `/problems/${encodeURIComponent(slug)}/tutor/`;

export const tutorConversation = (slug: string) =>
  getJson<TutorConversation>(path(slug));

/** 202 with the conversation; the reply is pending until the `ai` worker writes it.
 *  `lang` is the page's language: the API would otherwise answer in the
 *  browser's `Accept-Language` (measured: an English reply on an Uzbek page). */
export const askTutor = (slug: string, body: TutorAsk, lang: string) =>
  postJson<TutorConversation>(
    `${path(slug)}?lang=${encodeURIComponent(lang)}`,
    body,
  );

export const deleteTutorConversation = (slug: string) =>
  deleteJson<void>(path(slug));
