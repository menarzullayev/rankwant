import Link from "next/link";

import BrandMark from "@/layout/BrandMark";
import { LocaleSwitch } from "@/layout/LocaleSwitch";
import { getLocale } from "@/i18n/server";
import { t, type MessageKey } from "@/i18n/messages";

import { AuthPanel } from "./AuthPanel";

/** Platform areas named under the form below `lg`, where the panel is
 *  hidden. Existing nav keys. */
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
 *  panel came up empty. The reason still holds, so the panel is STATIC —
 *  since 2026-10-25 a ten-slide carousel (`AuthPanel`) of illustrations and
 *  the Cho'qqi mascot, no request. The sign-in page must not depend on
 *  anything.
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
    <div className="grid min-h-screen lg:grid-cols-[minmax(26rem,35%)_1fr]">
      <AuthPanel locale={locale} />

      <div className="flex min-h-screen flex-col">
        <div className="flex items-center justify-between gap-3 px-5 py-4 lg:justify-end lg:px-12">
          <BrandMark variant="full" className="lg:hidden" />
          <LocaleSwitch />
        </div>
        <div className="flex flex-1 items-center justify-center px-5 py-6 lg:px-12">
          <div className="w-full max-w-md">
            {children}
            {/* The brand panel is hidden below `lg`; its area names follow
                the form so a phone visitor still sees what the site is. */}
            <ul className="mt-6 flex flex-wrap justify-center gap-2 lg:hidden">
              {AREAS.map((key) => (
                <li
                  key={key}
                  className="rounded-full border rw-line px-3 py-1.5 text-theme-xs rw-dim"
                >
                  {t(locale, key)}
                </li>
              ))}
            </ul>
          </div>
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
