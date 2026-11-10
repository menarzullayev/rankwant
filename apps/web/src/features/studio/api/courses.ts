/** `/studio/courses` — courses in the studio (ADR-0056, part 4).
 *
 *  `studio/courses/` is the author's surface (text at any time, structure
 *  while unpublished); `staff/courses/` is staff-content's (price, publish,
 *  send back). The rules live in `apps/api/courses/review.py`.
 */

import { deleteJson, getJson, patchJson, postJson, type Paginated } from "@/lib/api/client";
import type { components } from "@/lib/api/generated/schema";

type Schemas = components["schemas"];

export type StudioCourse = Schemas["StudioCourse"];
export type StudioModule = Schemas["StudioModule"];
export type StudioSection = Schemas["StudioSection"];
export type StudioLesson = Schemas["StudioLesson"];
export type StaffCourse = Schemas["StaffCourse"];
export type CourseTextInput = Schemas["StudioText"];
export type ContentLocale = Schemas["ContentLocaleEnum"];

/** `courses.review.MAX_DRAFTS` — `course_studio_rules` keeps the two equal. */
export const COURSE_DRAFT_LIMIT = 3;

export const CONTENT_LOCALES: readonly ContentLocale[] = ["uz", "ru", "en"];

/** What the review asks for, in the order the page lists them. */
export const COURSE_GAPS = [
  "title",
  "summary",
  "lessons",
  "lesson_title",
  "lesson_text",
  "lesson_problem",
  "lesson_quiz",
  "lesson_video",
] as const;
export type CourseGap = (typeof COURSE_GAPS)[number];

export type CourseStatus = "draft" | "review" | "published";

const STATUSES: readonly CourseStatus[] = ["draft", "review", "published"];
const DRAFT: CourseStatus = "draft";

/** The API's `status` string; anything unknown reads as a draft. */
export const courseStatus = (course: { status: string }): CourseStatus =>
  STATUSES.find((status) => status === course.status) ?? DRAFT;

/** A translation row of `texts` in `locale`, if any. */
export function textOf<T extends { locale: string }>(texts: readonly T[], locale: string): T | undefined {
  return texts.find((row) => row.locale === locale);
}

const base = (slug: string) => `/studio/courses/${encodeURIComponent(slug)}`;

export const studioCourses = {
  list: () => getJson<Paginated<StudioCourse>>("/studio/courses/?page_size=100"),
  get: (slug: string) => getJson<StudioCourse>(`${base(slug)}/`),
  create: (data: Schemas["StudioCourseCreate"]) => postJson<StudioCourse>("/studio/courses/", data),
  update: (slug: string, data: Schemas["PatchedStudioCourse"]) =>
    patchJson<StudioCourse>(`${base(slug)}/`, data),
  remove: (slug: string) => deleteJson<void>(`${base(slug)}/`),
  review: (slug: string) => postJson<StudioCourse>(`${base(slug)}/review/`, {}),
  text: (slug: string, data: CourseTextInput) => postJson<StudioCourse>(`${base(slug)}/text/`, data),
  addModule: (slug: string, data: Schemas["PatchedStudioModule"]) =>
    postJson<StudioModule>(`${base(slug)}/modules/`, data),
  updateModule: (slug: string, id: number, data: Schemas["PatchedStudioModule"]) =>
    patchJson<StudioModule>(`${base(slug)}/modules/${id}/`, data),
  removeModule: (slug: string, id: number) => deleteJson<void>(`${base(slug)}/modules/${id}/`),
  addSection: (slug: string, data: Schemas["PatchedStudioSection"]) =>
    postJson<StudioSection>(`${base(slug)}/sections/`, data),
  updateSection: (slug: string, id: number, data: Schemas["PatchedStudioSection"]) =>
    patchJson<StudioSection>(`${base(slug)}/sections/${id}/`, data),
  removeSection: (slug: string, id: number) => deleteJson<void>(`${base(slug)}/sections/${id}/`),
  addLesson: (slug: string, data: Schemas["PatchedStudioLesson"]) =>
    postJson<StudioLesson>(`${base(slug)}/lessons/`, data),
  updateLesson: (slug: string, id: number, data: Schemas["PatchedStudioLesson"]) =>
    patchJson<StudioLesson>(`${base(slug)}/lessons/${id}/`, data),
  removeLesson: (slug: string, id: number) => deleteJson<void>(`${base(slug)}/lessons/${id}/`),
};

const staffBase = (slug: string) => `/staff/courses/${encodeURIComponent(slug)}`;

export const staffCourses = {
  list: (review: boolean) =>
    getJson<Paginated<StaffCourse>>(`/staff/courses/?page_size=100${review ? "&review=1" : ""}`),
  update: (slug: string, data: Schemas["PatchedStaffCourse"]) =>
    patchJson<StaffCourse>(`${staffBase(slug)}/`, data),
  publish: (slug: string) => postJson<StaffCourse>(`${staffBase(slug)}/publish/`, {}),
  sendBack: (slug: string, reason: string) =>
    postJson<StaffCourse>(`${staffBase(slug)}/send-back/`, { reason }),
};

/** New `order` values after moving `index` one step `by` (−1 up, +1 down):
 *  every item is renumbered 1…n, so equal orders cannot pin a row. */
export function reorder<T extends { id: number }>(rows: readonly T[], index: number, by: -1 | 1) {
  const target = index + by;
  if (target < 0 || target >= rows.length) return [];
  const next = [...rows];
  const [moved] = next.splice(index, 1);
  if (!moved) return [];
  next.splice(target, 0, moved);
  return next.map((row, i) => ({ id: row.id, order: i + 1 }));
}
