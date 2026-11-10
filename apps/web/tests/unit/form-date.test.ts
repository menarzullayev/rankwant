import { createElement, type ComponentProps } from "react";
import { prerender } from "react-dom/static";
import { afterEach, beforeAll, describe, expect, it, vi } from "vitest";

import { FormDate } from "@/components/form/FormKit";
import { LocaleProvider } from "@/i18n/LocaleProvider";
import { registerMessages, type Locale } from "@/i18n/messages";
import { ru } from "@/i18n/locales/ru";
import { uz } from "@/i18n/locales/uz";

// FormDate is a client component that the server renders too. Node has
// `uz` date data and Chrome does not, so anything it wrote through `Intl`
// came out as «noyabr, 2026» on the server and «2026 M11» in the browser —
// a hydration error on /settings (measured 2026-11-10).

beforeAll(() => {
  registerMessages("uz", uz);
  registerMessages("ru", ru);
});

afterEach(() => {
  vi.unstubAllGlobals();
  vi.useRealTimers();
});

async function render(locale: Locale, value?: string): Promise<string> {
  // `children` goes as the third argument; the props type still lists it.
  const props = { locale, dictionaryUrl: `/i18n/${locale}.js` } as ComponentProps<
    typeof LocaleProvider
  >;
  const tree = createElement(
    LocaleProvider,
    props,
    createElement(FormDate, { label: "birth", name: "birth_date", value }),
  );
  const { prelude } = await prerender(tree);
  return new Response(prelude).text();
}

const month = (html: string) => /<strong>([^<]*)<\/strong>/.exec(html)?.[1];
const day = (html: string) => /rw-fm-date-btn"[^>]*>([^<]*)</.exec(html)?.[1];
const weekdays = (html: string) =>
  [...html.matchAll(/<span class="rw-fm-cal-wd">([^<]*)<\/span>/g)].map((m) => m[1]);

describe("FormDate writes no text through Intl", () => {
  it("pins the month label and the day in uz", async () => {
    const html = await render("uz", "2026-11-10");
    expect(month(html)).toBe("11.2026");
    expect(day(html)).toBe("10.11.2026");
    expect(weekdays(html)).toEqual(["Dush", "Sesh", "Chor", "Pay", "Jum", "Shan", "Yak"]);
  });

  it("pins the same digits in ru, with ru weekday names", async () => {
    const html = await render("ru", "2026-11-10");
    expect(month(html)).toBe("11.2026");
    expect(day(html)).toBe("10.11.2026");
    expect(weekdays(html)).toEqual(["пн", "вт", "ср", "чт", "пт", "сб", "вс"]);
  });

  it("renders the same markup when the runtime has no date data", async () => {
    const node = await render("uz", "2026-11-10");
    // Chrome's ICU has no `uz` dates; the strictest stand-in is an `Intl`
    // that cannot format at all. Server and browser must not differ.
    vi.stubGlobal("Intl", {
      ...Intl,
      DateTimeFormat: function DateTimeFormat() {
        throw new Error("FormDate must not format through Intl.DateTimeFormat");
      },
    });
    expect(await render("uz", "2026-11-10")).toBe(node);
  });

  it("opens on today's month in the site zone, not the machine's", async () => {
    // 20:00 UTC on 30 November is already 1 December in Tashkent: the UTC
    // server and a browser in Tashkent used to open different months.
    vi.useFakeTimers({ toFake: ["Date"] });
    vi.setSystemTime(new Date("2026-11-30T20:00:00Z"));
    expect(month(await render("uz"))).toBe("12.2026");
  });
});
