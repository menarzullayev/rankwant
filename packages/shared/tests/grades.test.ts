import { describe, expect, it } from "vitest";

import {
  EDUCATION_LEVELS,
  GRADE_CODES,
  GRADE_GROUPS,
  gradeCodesFor,
  hasSpecialty,
} from "../src/grades";

describe("gradeCodesFor", () => {
  it("offers each level only its own years", () => {
    expect(gradeCodesFor("school")).toHaveLength(11);
    expect(gradeCodesFor("college")).toEqual(["c1", "c2", "c3", "c4"]);
    expect(gradeCodesFor("bachelor")).toEqual(["b1", "b2", "b3", "b4", "b5", "b6"]);
    expect(gradeCodesFor("master")).toEqual(["m1", "m2"]);
    expect(gradeCodesFor("phd")).toEqual(["d1", "d2", "d3", "d4"]);
    expect(gradeCodesFor("aspirantura")).toEqual(["a1", "a2", "a3", "a4"]);
  });

  it("has no year for working or other", () => {
    expect(gradeCodesFor("working")).toEqual([]);
    expect(gradeCodesFor("other")).toEqual([]);
  });

  it("never offers a code the catalogue does not know", () => {
    for (const level of EDUCATION_LEVELS) {
      for (const code of gradeCodesFor(level)) expect(GRADE_CODES).toContain(code);
    }
  });
});

describe("the settings groups", () => {
  it("cover every code exactly once", () => {
    const grouped = GRADE_GROUPS.flatMap((group) => [...group.codes]);
    expect(grouped).toEqual([...GRADE_CODES]);
  });
});

describe("hasSpecialty", () => {
  it("asks for a field of study from college up", () => {
    expect(hasSpecialty("school")).toBe(false);
    expect(hasSpecialty("college")).toBe(true);
    expect(hasSpecialty("aspirantura")).toBe(true);
    expect(hasSpecialty("working")).toBe(false);
  });
});
