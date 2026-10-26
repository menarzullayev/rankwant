import { beforeAll, describe, expect, it } from "vitest";

import { registerMessages } from "@/i18n/messages";
import { en } from "@/i18n/locales/en";
import { uz } from "@/i18n/locales/uz";
import { GRADE_CODES, GRADE_GROUPS, gradeLabel, isGradeCode } from "@rankwant/shared/grades";

beforeAll(() => {
  registerMessages("uz", uz);
  registerMessages("en", en);
});

describe("gradeLabel", () => {
  it("names every kind of code", () => {
    expect(gradeLabel("9", "uz")).toBe("9-sinf");
    expect(gradeLabel("b2", "uz")).toBe("Bakalavriat, 2-kurs");
    expect(gradeLabel("m1", "en")).toBe("Master's, year 1");
    expect(gradeLabel("teacher", "en")).toBe("Teacher");
    expect(gradeLabel("other", "uz")).toBe("Boshqa");
  });

  it("names the college, doctoral and postgraduate years (2026-10-26)", () => {
    expect(gradeLabel("c2", "uz")).toBe("Kollej, 2-kurs");
    expect(gradeLabel("b6", "uz")).toBe("Bakalavriat, 6-kurs");
    expect(gradeLabel("d3", "uz")).toBe("PhD / doktorantura, 3-yil");
    expect(gradeLabel("a1", "en")).toBe("Postgraduate (aspirantura), year 1");
  });

  it("shows a value saved before the catalogue as written", () => {
    expect(gradeLabel("9-A", "uz")).toBe("9-A");
    expect(isGradeCode("9-A")).toBe(false);
  });
});

describe("GRADE_GROUPS", () => {
  it("covers the catalogue once, in order", () => {
    expect(GRADE_GROUPS.flatMap((group) => group.codes)).toEqual([...GRADE_CODES]);
  });
});
