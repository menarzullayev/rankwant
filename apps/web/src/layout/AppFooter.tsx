"use client";

import { usePathname } from "next/navigation";

import { IntentLink } from "@/components/ui/IntentLink";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";

import BrandMark from "./BrandMark";

/** Aloqa manzillari — bitta joyda. 2026-09-20 HITL: `t.me/rankwant`
 *  va `support@rankwant.uz` rasmiy (confirm-current). */
const TELEGRAM_URL = "https://t.me/rankwant";
const CONTACT_EMAIL = "support@rankwant.uz";

/** What the footer links to. Labels are the navigation's own keys: no
 *  second translation of "Problems", and no way for the two to drift.
 *
 *  The list is a choice, not a copy of the side menu (21 items): the
 *  product's four front doors, then the pages that explain the platform
 *  — the ones a visitor looks for at the bottom of a page, and the ones
 *  a search engine should find from every page (ADR-0023).
 */
const PRODUCT = [
  { href: "/problems", key: "nav.problems" },
  { href: "/contests", key: "nav.contests" },
  { href: "/arena", key: "nav.arena" },
  { href: "/leaderboard", key: "nav.leaderboard" },
] as const;

const RESOURCES = [
  { href: "/about", key: "nav.about" },
  { href: "/rating", key: "nav.formulas" },
  { href: "/blog", key: "nav.blog" },
  { href: "/updates", key: "nav.updates" },
  { href: "/platform-roadmap", key: "nav.platformRoadmap" },
] as const;

const COMMUNITY = [{ href: "/team", key: "nav.team" }] as const;

type FooterLink = (typeof PRODUCT | typeof RESOURCES | typeof COMMUNITY)[number];

/** A footer link: 14 px, a 32 px row with a mouse and 44 px under a
 *  finger. The old ones were 12 px text in a 16 px row — ten targets,
 *  none of them large enough to tap (measured 2026-10-06). */
const LINK =
  "inline-flex min-h-8 items-center rw-radius-sm text-theme-sm rw-dim-2 transition rw-link-hover rw-focus-ring [@media(pointer:coarse)]:min-h-11";
const CURRENT = "font-medium rw-strong";
/** The wordmark is a link home: the same row height as the rest. */
const BRAND =
  "inline-flex min-h-8 items-center rw-radius-sm rw-focus-ring [@media(pointer:coarse)]:min-h-11";
const HEADING = "text-theme-xs font-semibold tracking-wider rw-faint uppercase";

/** Footer — a band of its own under the page, four groups.
 *
 *  Brand and tagline · product · resources · contact and community, and
 *  a legal row below. Terms and Privacy are on EVERY page: Google OAuth
 *  verification expects the privacy policy reachable from here
 *  (ADR-0016). Links are `IntentLink` — prefetch on intent only (the
 *  header / sidebar / footer decision).
 *
 *  On a phone the two link groups sit side by side under the brand: the
 *  same information in half the height, without an accordion to open.
 */
export default function AppFooter() {
  const locale = useLocale();
  const pathname = usePathname();
  const year = new Date().getFullYear();

  const item = ({ href, key }: FooterLink) => {
    const current = pathname === href || pathname.startsWith(`${href}/`);
    return (
      <li key={href}>
        <IntentLink
          href={href}
          aria-current={current ? "page" : undefined}
          className={current ? `${LINK} ${CURRENT}` : LINK}
        >
          {t(locale, key)}
        </IntentLink>
      </li>
    );
  };

  return (
    <footer className="mt-10 border-t rw-divider rw-chrome">
      <div className="rw-content mx-auto px-4 py-10 md:px-6">
        <div className="grid grid-cols-2 gap-x-6 gap-y-8 md:grid-cols-4 lg:grid-cols-[minmax(0,1.6fr)_repeat(3,minmax(0,1fr))]">
          <div className="col-span-2 md:col-span-4 lg:col-span-1">
            <BrandMark variant="full" className={BRAND} />
            <p className="mt-2 max-w-xs text-theme-sm rw-dim">{t(locale, "footer.tagline")}</p>
          </div>

          <nav aria-labelledby="footer-product">
            <h2 id="footer-product" className={HEADING}>
              {t(locale, "footer.platform")}
            </h2>
            <ul className="mt-2">{PRODUCT.map(item)}</ul>
          </nav>

          <nav aria-labelledby="footer-resources">
            <h2 id="footer-resources" className={HEADING}>
              {t(locale, "footer.resources")}
            </h2>
            <ul className="mt-2">{RESOURCES.map(item)}</ul>
          </nav>

          <nav aria-labelledby="footer-contact" className="col-span-2 md:col-span-2 lg:col-span-1">
            <h2 id="footer-contact" className={HEADING}>
              {t(locale, "footer.contact")}
            </h2>
            <ul className="mt-2">
              {COMMUNITY.map(item)}
              <li>
                <a href={TELEGRAM_URL} target="_blank" rel="noopener noreferrer" className={LINK}>
                  {t(locale, "footer.telegram")}
                  <span className="sr-only"> {t(locale, "footer.opensNewTab")}</span>
                </a>
              </li>
              <li
                // CF rewrites mailto on the <a> itself. email_off/on comments
                // must wrap the whole tag — wrapping only the text left
                // email-decode in place (measured live 2026-09-20, #198):
                // href became /cdn-cgi/l/email-protection.
                dangerouslySetInnerHTML={{
                  __html: `<!--email_off--><a href="mailto:${CONTACT_EMAIL}" class="${LINK} break-all">${CONTACT_EMAIL}</a><!--email_on-->`,
                }}
              />
            </ul>
          </nav>
        </div>

        <div className="mt-8 flex flex-col gap-x-6 gap-y-1 border-t rw-divider pt-4 text-theme-xs rw-dim sm:flex-row sm:items-center sm:justify-between">
          <p>{fill(t(locale, "footer.copyright"), { year })}</p>
          <ul className="flex flex-wrap gap-x-5">
            <li>
              <IntentLink href="/terms" className={LINK}>
                {t(locale, "footer.terms")}
              </IntentLink>
            </li>
            <li>
              <IntentLink href="/privacy" className={LINK}>
                {t(locale, "footer.privacy")}
              </IntentLink>
            </li>
          </ul>
        </div>
      </div>
    </footer>
  );
}
