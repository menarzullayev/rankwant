import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { beforeAll, describe, expect, it } from "vitest";

import { en } from "@/i18n/locales/en";
import { uz } from "@/i18n/locales/uz";
import { registerMessages } from "@/i18n/messages";
import {
  cursorOf,
  dayGroup,
  listQuery,
  MESSAGE_CODES,
  notificationHref,
  notificationText,
  type Notification,
} from "@/lib/notifications/model";

function src(rel: string): string {
  return readFileSync(resolve(__dirname, rel), "utf8");
}

const note = (over: Partial<Notification>): Notification => ({
  id: 1,
  kind: "system",
  title: "saqlangan sarlavha",
  body: "saqlangan matn",
  code: "",
  params: {},
  ref_type: "",
  ref_id: "",
  is_read: false,
  created_at: "2026-10-06T08:00:00Z",
  ...over,
});

beforeAll(() => {
  registerMessages("uz", uz);
  registerMessages("en", en);
});

describe("message codes", () => {
  const keys = Object.keys(uz).filter((key) => key.startsWith("notif.msg."));

  it("lists exactly the codes the dictionary has, with the right parts", () => {
    const fromDictionary: Record<string, { body: boolean }> = {};
    for (const key of keys) {
      const [, , code, part] = key.split(".");
      fromDictionary[code] ??= { body: false };
      if (part === "body") fromDictionary[code].body = true;
    }
    expect(MESSAGE_CODES).toEqual(fromDictionary);
  });

  it("matches the catalogue the server was given", () => {
    const server = src("../../../api/notifications/message_catalog.py");
    // Every language block lists the same codes (the exporter refuses
    // otherwise), so the set over the whole file is the set of codes.
    const codes = new Set([...server.matchAll(/^ {8}"([a-z_]+)": \{$/gm)].map((match) => match[1]));
    expect([...codes].sort()).toEqual(Object.keys(MESSAGE_CODES).sort());
  });
});

describe("notification wording", () => {
  it("draws a coded row in the language it is read in", () => {
    const row = note({ code: "streak", params: { days: 30 }, title: "30 kunlik streak!" });
    expect(notificationText(row, "en").title).toBe("30-day streak!");
    expect(notificationText(row, "uz").title).toBe("30 kunlik streak!");
  });

  it("keeps free text as it was written", () => {
    expect(notificationText(note({}), "en")).toEqual({
      title: "saqlangan sarlavha",
      body: "saqlangan matn",
    });
  });

  it("falls back to the stored text for a code this build does not know", () => {
    const row = note({ code: "retired_code", params: { x: 1 } });
    expect(notificationText(row, "en").title).toBe("saqlangan sarlavha");
  });

  it("keeps a person's own words where the code has no body sentence", () => {
    const row = note({ code: "hackathon_scored", params: { score: 80 }, body: "Yaxshi ish" });
    expect(notificationText(row, "en")).toEqual({
      title: "Hackathon score: 80/100",
      body: "Yaxshi ish",
    });
  });

  it("shows a timestamp value as a date, not as ISO text", () => {
    const row = note({
      code: "duel_accepted",
      params: { user: "ali", duel: "Kuz", start_at: "2026-10-06T14:30:00+00:00" },
    });
    const body = notificationText(row, "en").body;
    expect(body).toContain("2026");
    expect(body).not.toContain("T14:30");
  });
});

describe("where a notification leads", () => {
  it("opens the page it is about", () => {
    expect(notificationHref(note({ ref_type: "duel", ref_id: "a-b" }))).toBe("/duels/a-b");
    expect(notificationHref(note({ ref_type: "contest", ref_id: "r12" }))).toBe("/contests/r12");
    expect(notificationHref(note({ ref_type: "problem", ref_id: "graf" }))).toBe("/problems/graf");
    expect(notificationHref(note({ ref_type: "attempt", ref_id: "88" }))).toBe("/attempts/88");
    expect(notificationHref(note({ ref_type: "post", ref_id: "yangi" }))).toBe("/blog/yangi");
    expect(notificationHref(note({ ref_type: "streak", ref_id: "30" }))).toBe("/qvant");
  });

  it("sends a hack to its problem — a hack has no page of its own", () => {
    const row = note({ ref_type: "hack", ref_id: "5", params: { problem: "ryukzak" } });
    expect(notificationHref(row)).toBe("/problems/ryukzak");
  });

  it("has nowhere to go for a staff message", () => {
    expect(notificationHref(note({ ref_type: "admin" }))).toBeNull();
    expect(notificationHref(note({}))).toBeNull();
  });
});

describe("list helpers", () => {
  it("groups by the reader's calendar day", () => {
    const now = new Date(2026, 9, 6, 9, 0);
    expect(dayGroup(new Date(2026, 9, 6, 0, 5).toISOString(), now)).toBe("today");
    expect(dayGroup(new Date(2026, 9, 5, 23, 55).toISOString(), now)).toBe("yesterday");
    expect(dayGroup(new Date(2026, 9, 3, 12, 0).toISOString(), now)).toBe("earlier");
  });

  it("takes only the cursor from the next link", () => {
    expect(cursorOf("http://api:8000/api/v1/notifications/?cursor=abc%3D&page_size=8")).toBe("abc=");
    expect(cursorOf(null)).toBeNull();
  });

  it("builds the query without defaults", () => {
    expect(listQuery({ unread: false, kind: null, size: 8 })).toBe("?page_size=8");
    expect(listQuery({ unread: true, kind: "duel", size: 20, cursor: "c" })).toBe(
      "?page_size=20&unread=true&kind=duel&cursor=c",
    );
  });
});

describe("the bell and the live channel", () => {
  const bell = src("../../src/components/notifications/NotificationBell.tsx");
  const context = src("../../src/context/NotificationsContext.tsx");
  const stream = src("../../src/lib/useEventStream.ts");

  it("marks seen when the panel opens, and never marks read by itself", () => {
    expect(bell).toContain("if (summary.unseen > 0) markSeen();");
    expect(bell).not.toContain("readAll()");
    expect(bell).toContain("{unseen > 99 ? \"99+\" : unseen}");
  });

  it("listens for the event the server publishes", () => {
    const server = src("../../../api/notifications/services.py");
    expect(server).toContain('EVENT_NOTIFICATION = "notification"');
    expect(stream).toContain('export const EVENT_NOTIFICATION = "notification";');
    expect(stream).toContain("      EVENT_NOTIFICATION,\n");
    expect(context).toContain("name === EVENT_NOTIFICATION || name === EVENT_RESYNC");
  });

  it("holds no stream in a hidden tab and falls back to polling", () => {
    expect(context).toContain("enabled: signedIn && visible");
    expect(context).toContain('stream !== "fallback"');
    expect(context).toContain("window.setInterval(changed, POLL_MS)");
  });

  it("draws the same states in the panel and on the page", () => {
    const center = src("../../src/components/notifications/NotificationCenter.tsx");
    expect(bell).toContain("<Feed");
    expect(center).toContain("<Feed");
  });
});
