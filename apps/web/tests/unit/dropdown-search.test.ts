import { describe, expect, it } from "vitest";

import {
  filterDropdownOptions,
  groupDropdownOptions,
} from "@/lib/dropdown-search";

const OPTIONS = [
  { value: "male", label: "Erkak", keywords: "men" },
  { value: "female", label: "Ayol", keywords: "women" },
  { value: "UZ", label: "O'zbekiston", keywords: "Uzbekistan UZ", group: "Mintaqa" },
  { value: "KZ", label: "Qozog'iston", keywords: "Kazakhstan KZ", group: "Mintaqa" },
  { value: "recent", label: "Yangi", group: "Tartib" },
];

describe("filterDropdownOptions", () => {
  it("returns every option when the query is blank", () => {
    expect(filterDropdownOptions(OPTIONS, "  ")).toHaveLength(OPTIONS.length);
  });

  it("matches label, keywords, and value", () => {
    expect(filterDropdownOptions(OPTIONS, "qoz").map((o) => o.value)).toEqual(["KZ"]);
    expect(filterDropdownOptions(OPTIONS, "uzbekistan").map((o) => o.value)).toEqual(["UZ"]);
    expect(filterDropdownOptions(OPTIONS, "erkak").map((o) => o.value)).toEqual(["male"]);
  });

  it("yields an empty list when nothing matches", () => {
    expect(filterDropdownOptions(OPTIONS, "zzzz")).toEqual([]);
  });
});

describe("groupDropdownOptions", () => {
  it("keeps first-seen group order", () => {
    expect(groupDropdownOptions(OPTIONS).map((bucket) => bucket.group)).toEqual([
      undefined,
      "Mintaqa",
      "Tartib",
    ]);
  });
});
