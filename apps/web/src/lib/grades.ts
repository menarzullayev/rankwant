import { fill, t, type Locale, type MessageKey } from "@/i18n/messages";

/** Grade or year of study (ADR-0024). Mirrors `profiles.catalog.GRADES`;
 *  `apps/api/tests/test_grades.py` keeps the two lists equal. */
export const GRADE_CODES = [
  "1",
  "2",
  "3",
  "4",
  "5",
  "6",
  "7",
  "8",
  "9",
  "10",
  "11",
  "b1",
  "b2",
  "b3",
  "b4",
  "m1",
  "m2",
  "teacher",
  "other",
] as const;

export type GradeCode = (typeof GRADE_CODES)[number];

/** Option groups for the settings select, in catalogue order. `null` has no heading. */
export const GRADE_GROUPS: { key: MessageKey | null; codes: readonly GradeCode[] }[] = [
  { key: "settings.gradeSchool", codes: GRADE_CODES.slice(0, 11) },
  { key: "settings.gradeUniversity", codes: GRADE_CODES.slice(11, 17) },
  { key: null, codes: GRADE_CODES.slice(17) },
];

export function isGradeCode(value: string): value is GradeCode {
  return (GRADE_CODES as readonly string[]).includes(value);
}

/** Human label for a stored grade. A value saved before the catalogue shows as written. */
export function gradeLabel(code: string, locale: Locale): string {
  if (!isGradeCode(code)) return code;
  if (code === "teacher") return t(locale, "grade.teacher");
  if (code === "other") return t(locale, "grade.other");
  if (code.startsWith("b")) return fill(t(locale, "grade.bachelor"), { n: code.slice(1) });
  if (code.startsWith("m")) return fill(t(locale, "grade.master"), { n: code.slice(1) });
  return fill(t(locale, "grade.school"), { n: code });
}
