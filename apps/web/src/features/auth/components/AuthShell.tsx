import Image from "next/image";
import Link from "next/link";

import BrandMark from "@/layout/BrandMark";
import { LocaleSwitch } from "@/layout/LocaleSwitch";
import { getLocale } from "@/i18n/server";
import { t, type MessageKey } from "@/i18n/messages";

/** Platform areas named in the brand panel. Existing nav keys, so the
 *  panel adds no new copy to translate. */
const AREAS: MessageKey[] = [
  "nav.problems",
  "nav.contests",
  "nav.arena",
  "nav.leaderboard",
];

/** The sign-in page shell: brand panel on the left, form on the right
 *  (HITL 2026-10-04, variant B).
 *
 *  This replaces the single centred card of decision 18. That decision
 *  dropped an earlier split screen because its panel rendered
 *  `api.stats()` and `api.contests()`: when the API was slow or down the
 *  panel came up empty. The reason still holds, so this panel is
 *  STATIC — brand, tagline and area names, no request. The sign-in page
 *  must not depend on anything.
 *
 *  The site header and footer are not drawn on this route (`FULL` in
 *  `AppShell`), so what they carried lives here: the brand link, the
 *  language switch, and the Terms/Privacy links ADR-0016 requires on the
 *  page where an OAuth account is created.
 *
 *  Below `lg` the panel is hidden and the brand moves into the top row —
 *  on a phone the form is the page.
 */
export async function AuthShell({ children }: { children: React.ReactNode }) {
  const locale = await getLocale();

  return (
    <div className="grid min-h-screen lg:grid-cols-[5fr_6fr]">
      {/* Panel colours are the page's own text/ground pair, swapped: that
          pair is already contrast-checked in every style, light or dark. */}
      <aside className="hidden flex-col justify-between gap-8 bg-[var(--rw-text)] p-12 text-[var(--rw-ground)] lg:flex">
        <Link
          href="/"
          className="self-start text-2xl font-bold rw-radius-sm rw-focus-ring"
        >
          RankWant
        </Link>
        <div className="flex flex-col gap-6">
          <span className="grid h-36 w-36 place-items-center rounded-[2rem] bg-white">
            <Image
              src="/brand/mark-crest.svg"
              alt=""
              width={112}
              height={112}
              unoptimized
            />
          </span>
          <p className="text-4xl font-bold leading-tight">
            {t(locale, "auth.tagline")}
          </p>
          <p className="text-theme-xl">{t(locale, "footer.tagline")}</p>
        </div>
        <ul className="flex flex-wrap gap-2.5">
          {AREAS.map((key) => (
            <li
              key={key}
              className="rounded-full border border-current px-3.5 py-2 text-theme-sm"
            >
              {t(locale, key)}
            </li>
          ))}
        </ul>
      </aside>

      <div className="flex min-h-screen flex-col">
        <div className="flex items-center justify-between gap-3 px-5 py-4 lg:justify-end lg:px-12">
          <BrandMark variant="full" className="lg:hidden" />
          <LocaleSwitch />
        </div>
        <div className="flex flex-1 items-center justify-center px-5 py-6 lg:px-12">
          <div className="w-full max-w-md">{children}</div>
        </div>
        <p className="px-5 pb-6 text-center text-theme-xs rw-dim lg:px-12">
          <Link href="/terms" className="underline rw-focus-ring">
            {t(locale, "footer.terms")}
          </Link>
          {" · "}
          <Link href="/privacy" className="underline rw-focus-ring">
            {t(locale, "footer.privacy")}
          </Link>
        </p>
      </div>
    </div>
  );
}
