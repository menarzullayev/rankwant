/** Leave a sign-in page for the site with a full page load.
 *
 *  The sign-in pages and the rest of the site can be in different languages
 *  (until 2026-11-26 sign-in and sign-up were Uzbek for every guest; reset and
 *  onboarding still follow their own rules), while the rest of the site
 *  follows the reader's language. `router.push` keeps the browser's Uzbek dictionary and lets the
 *  next page's server parts render in the reader's language: measured
 *  2026-11-26 with an English browser, the first home page after onboarding
 *  showed the raw property `kit.left` in the contest countdown (and threw in
 *  development). A full load brings the right dictionary with the page.
 */
export function leaveAuth(href: string): void {
  window.location.assign(href);
}
