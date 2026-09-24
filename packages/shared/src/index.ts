/**
 * `@rankwant/shared` — platform-independent logic.
 *
 * Three rules decide what belongs here:
 *
 *   1. **No React, no Next, no DOM.** If a module reaches for `window`,
 *      `document`, `next/*` or JSX, it belongs in the app.
 *   2. **Real reuse or a real boundary.** A module earns its place only
 *      when something outside `apps/web` needs it, or when a boundary
 *      (validation rules vs. their wording) is worth enforcing. Moving
 *      files here to look tidy is not a reason.
 *   3. **Data stays with its consumers.** Locale *rules* live here; the ten
 *      dictionaries stay in `apps/web/src/i18n/locales` — they are content,
 *      not mechanism, and they weigh ~400 kB.
 *
 * Consumers import the specific subpath (`@rankwant/shared/i18n`), never
 * this barrel: a barrel makes every import pull in every module, which
 * would put `zod` into bundles that only wanted `fill()`.
 */
export {};
