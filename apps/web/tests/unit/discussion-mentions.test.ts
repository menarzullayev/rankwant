import { describe, expect, it } from "vitest";

import { linkMentions } from "@/features/community/mentions";

describe("linkMentions", () => {
  it("links a mention to the profile", () => {
    expect(linkMentions("salom @nodira_r!")).toBe("salom [@nodira_r](/users/nodira_r)!");
  });

  it("leaves fenced and inline code alone", () => {
    const text = "```\n@inside\n```\n`@inline` va @outside";
    expect(linkMentions(text)).toBe("```\n@inside\n```\n`@inline` va [@outside](/users/outside)");
  });

  it("ignores e-mail addresses and short names", () => {
    expect(linkMentions("a@b.uz va @ab")).toBe("a@b.uz va @ab");
  });
});
