"use client";

import { IntentLink } from "@/components/ui/IntentLink";

import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";

/** Aloqa manzillari — bitta joyda. 2026-09-20 HITL: `t.me/rankwant`
 *  va `support@rankwant.uz` rasmiy (confirm-current). */
const TELEGRAM_URL = "https://t.me/rankwant";
const CONTACT_EMAIL = "support@rankwant.uz";

/** Footer'dagi «Platforma» havolalari — matnlari mavjud nav kalitlaridan
 *  olinadi, ya'ni yangi tarjima kiritilmaydi va til paritysi buzilmaydi.
 *  Ro'yxat tasodifiy emas: indekslanadigan sayt uchun (ADR-0023) bu
 *  sahifalar qidiruv tizimlariga ham shu yerda ko'rinadi. */
const PLATFORM_LINKS = [
  { href: "/problems", key: "nav.problems" },
  { href: "/contests", key: "nav.contests" },
  { href: "/arena", key: "nav.arena" },
  { href: "/leaderboard", key: "nav.leaderboard" },
  { href: "/blog", key: "nav.blog" },
  { href: "/updates", key: "nav.updates" },
] as const;

/** Footer — uch ustun (qaror 22): brend, platforma havolalari, aloqa.
 *  Pastda huquqiy qator: Terms/Privacy HAR sahifada turishi shart —
 *  Google OAuth tasdig'i maxfiylik siyosati manzilini kutadi (ADR-0016).
 *  Havolalar `IntentLink` — niyatda prefetch (header/sidebar/footer
 *  qarori), fokus halqasi `rw-focus-ring` (WCAG 2.4.11). */
export default function AppFooter() {
  const locale = useLocale();
  const year = new Date().getFullYear();
  return (
    <footer className="rw-content mx-auto px-4 pb-8 pt-6 md:px-6">
      <div className="grid gap-8 border-t rw-divider pt-6 sm:grid-cols-2 lg:grid-cols-[1fr_auto_auto]">
        <div>
          <p className="text-lg font-bold">
            Rank<span className="rw-accent-ink">Want</span>
          </p>
          <p className="mt-2 max-w-72 text-theme-xs rw-dim">
            {t(locale, "footer.tagline")}
          </p>
        </div>
        <nav aria-label={t(locale, "footer.platform")}>
          <p className="text-theme-xs font-semibold rw-strong">
            {t(locale, "footer.platform")}
          </p>
          <ul className="mt-3 space-y-2 text-theme-xs rw-dim">
            {PLATFORM_LINKS.map(({ href, key }) => (
              <li key={href}>
                <IntentLink href={href} className="rw-focus-ring hover:underline">
                  {t(locale, key)}
                </IntentLink>
              </li>
            ))}
          </ul>
        </nav>
        <div>
          <p className="text-theme-xs font-semibold rw-strong">
            {t(locale, "footer.contact")}
          </p>
          <ul className="mt-3 space-y-2 text-theme-xs rw-dim">
            <li>
              <a
                href={TELEGRAM_URL}
                target="_blank"
                rel="noreferrer"
                className="rw-focus-ring hover:underline"
              >
                t.me/rankwant
              </a>
            </li>
            <li
              // CF rewrites mailto on the <a> itself. email_off/on comments
              // must wrap the whole tag — wrapping only the text left
              // email-decode in place (measured live 2026-09-20, #198):
              // href became /cdn-cgi/l/email-protection.
              dangerouslySetInnerHTML={{
                __html:
                  `<!--email_off--><a href="mailto:${CONTACT_EMAIL}" class="rw-focus-ring hover:underline">${CONTACT_EMAIL}</a><!--email_on-->`,
              }}
            />
          </ul>
        </div>
      </div>
      <div className="mt-6 flex flex-wrap items-center gap-x-5 gap-y-2 border-t rw-divider pt-4 text-theme-xs rw-dim">
        <span>{fill(t(locale, "footer.copyright"), { year })}</span>
        <IntentLink href="/terms" className="rw-focus-ring hover:underline">
          {t(locale, "footer.terms")}
        </IntentLink>
        <IntentLink href="/privacy" className="rw-focus-ring hover:underline">
          {t(locale, "footer.privacy")}
        </IntentLink>
      </div>
    </footer>
  );
}
