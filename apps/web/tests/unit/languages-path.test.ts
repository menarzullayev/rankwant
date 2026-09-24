import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { LANGUAGES_PATH } from "@/features/problems/api/problems";

const CATALOG = new URL("../../../api/problems/languages.py", import.meta.url);
const PAGINATION = new URL("../../../api/core/pagination.py", import.meta.url);

describe("LANGUAGES_PATH", () => {
  // The profile's language filter and the hack generator show only the first
  // page. At 35 languages the API's default page of 25 hid ten of them, Python
  // 3.13 among them, and nothing failed.
  it("fits the whole judge catalog on one page", () => {
    const catalog = readFileSync(CATALOG, "utf8");
    const codes = [...catalog.matchAll(/"code": "([a-z][a-z0-9]*)"/g)];
    const pagination = readFileSync(PAGINATION, "utf8");
    const standard = pagination.slice(pagination.indexOf("class StandardPagination"));
    const setting = (name: string) =>
      Number(new RegExp(`^\\s+${name} = (\\d+)`, "m").exec(standard)?.[1]);

    // DRF caps page_size at max_page_size and uses page_size when none is sent.
    const requested = new URL(LANGUAGES_PATH, "http://api").searchParams.get("page_size");
    const served = Math.min(
      requested === null ? setting("page_size") : Number(requested),
      setting("max_page_size"),
    );

    expect(codes.length).toBeGreaterThan(0);
    expect(served).toBeGreaterThanOrEqual(codes.length);
  });
});
