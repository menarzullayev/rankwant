/** Courses (ADR-0056): shapes from the OpenAPI schema and the two writes. */

import type { Route } from "next";

import { postJson } from "@/lib/api/client";
import type { components } from "@/lib/api/generated/schema";

type Schemas = components["schemas"];

export type CourseCard = Schemas["CourseCard"];
export type CourseDetail = Schemas["CourseDetail"];
export type CourseModule = Schemas["ModuleOutline"];
export type CourseLessonRow = Schemas["LessonRow"];
export type LessonDetail = Schemas["LessonDetail"];
export type CourseProgress = Schemas["Progress"];
export type MyCourse = Schemas["MyCourse"];
export type CourseLevel = Schemas["CourseLevelEnum"];
export type CourseAccess = CourseCard["access"];

/** What a lesson is for this reader; the API sends it as a plain string. */
export type LessonState = "done" | "open" | "locked";

const STATES: readonly LessonState[] = ["done", "open", "locked"];
const LOCKED: LessonState = "locked";

/** Anything unknown reads as locked: a link that would only answer 403 is
 *  worse than a row that cannot be opened. */
export const lessonState = (raw: string): LessonState =>
  STATES.find((state) => state === raw) ?? LOCKED;

/** A lesson's page. Plain module (no `"use client"`): server pages call it. */
export const lessonHref = (slug: string, id: number) =>
  `/courses/${encodeURIComponent(slug)}/lessons/${id}` as Route;

/** Course text exists in these languages only (`courses.models.CONTENT_LOCALES`). */
export const COURSE_LOCALES = ["uz", "ru", "en"] as const;

/** `?lang=` for the API: the reader's language when courses are written in
 *  it; otherwise nothing, and the API falls back to the course's base. */
export function langQuery(locale: string): string {
  return (COURSE_LOCALES as readonly string[]).includes(locale) ? `lang=${locale}` : "";
}

export const enrollCourse = (slug: string) =>
  postJson<Schemas["Enrollment"]>(`/courses/${encodeURIComponent(slug)}/enroll/`, {});

export const completeLesson = (slug: string, lessonId: number) =>
  postJson<CourseProgress>(
    `/courses/${encodeURIComponent(slug)}/lessons/${lessonId}/complete/`,
    {},
  );

/** The first lesson the reader should open next: the first open lesson that
 *  is not done, else the first lesson. */
export function nextLesson(course: CourseDetail): CourseLessonRow | null {
  const rows = course.modules.flatMap((m) => m.sections.flatMap((s) => s.lessons));
  return rows.find((row) => lessonState(row.state) === "open") ?? rows[0] ?? null;
}
