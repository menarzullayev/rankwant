import { fill, t, type Locale, type MessageKey } from "./i18n/index";

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
  "c1",
  "c2",
  "c3",
  "c4",
  "b1",
  "b2",
  "b3",
  "b4",
  "b5",
  "b6",
  "m1",
  "m2",
  "d1",
  "d2",
  "d3",
  "d4",
  "a1",
  "a2",
  "a3",
  "a4",
  "teacher",
  "other",
] as const;

export type GradeCode = (typeof GRADE_CODES)[number];

/** Option groups for the settings select, in catalogue order. `null` has no heading. */
export const GRADE_GROUPS: { key: MessageKey | null; codes: readonly GradeCode[] }[] = [
  { key: "settings.gradeSchool", codes: GRADE_CODES.slice(0, 11) },
  { key: "settings.gradeCollege", codes: GRADE_CODES.slice(11, 15) },
  { key: "settings.gradeUniversity", codes: GRADE_CODES.slice(15, 23) },
  { key: "settings.gradePostgraduate", codes: GRADE_CODES.slice(23, 31) },
  { key: null, codes: GRADE_CODES.slice(31) },
];

/** Where a person studies (`profiles.catalog.EDUCATION_LEVELS`). */
export const EDUCATION_LEVELS = [
  "school",
  "lyceum",
  "college",
  "bachelor",
  "master",
  "phd",
  "aspirantura",
  "working",
  "other",
] as const;

export type EducationLevel = (typeof EDUCATION_LEVELS)[number];

/** The grade choices that belong to a level, so the second select never offers
 *  "5th year" to a schoolchild. `working` and `other` have no year. */
export function gradeCodesFor(level: string): readonly GradeCode[] {
  switch (level) {
    case "school":
    case "lyceum":
      return GRADE_CODES.slice(0, 11);
    case "college":
      return GRADE_CODES.slice(11, 15);
    case "bachelor":
      return GRADE_CODES.slice(15, 21);
    case "master":
      return GRADE_CODES.slice(21, 23);
    case "phd":
      return GRADE_CODES.slice(23, 27);
    case "aspirantura":
      return GRADE_CODES.slice(27, 31);
    default:
      return [];
  }
}

/** Levels that name a field of study. */
export function hasSpecialty(level: string): boolean {
  return ["college", "bachelor", "master", "phd", "aspirantura"].includes(level);
}

export function isGradeCode(value: string): value is GradeCode {
  return (GRADE_CODES as readonly string[]).includes(value);
}

/** Human label for a stored grade. A value saved before the catalogue shows as written. */
export function gradeLabel(code: string, locale: Locale): string {
  if (!isGradeCode(code)) return code;
  if (code === "teacher") return t(locale, "grade.teacher");
  if (code === "other") return t(locale, "grade.other");
  if (code.startsWith("c")) return fill(t(locale, "grade.college"), { n: code.slice(1) });
  if (code.startsWith("b")) return fill(t(locale, "grade.bachelor"), { n: code.slice(1) });
  if (code.startsWith("m")) return fill(t(locale, "grade.master"), { n: code.slice(1) });
  if (code.startsWith("d")) return fill(t(locale, "grade.doctoral"), { n: code.slice(1) });
  if (code.startsWith("a")) return fill(t(locale, "grade.aspirant"), { n: code.slice(1) });
  return fill(t(locale, "grade.school"), { n: code });
}
