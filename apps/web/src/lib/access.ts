/** Who may open which part of the site — the one list (ADR-0054).
 *
 *  Four levels:
 *
 *  - `public` — anyone. A personal block inside such a page is replaced by
 *    the sign-in card (`SignInGate`), the page itself stays open.
 *  - `guest`  — sign-in pages; a signed-in visitor is sent on.
 *  - `user`   — signed in. A guest is redirected to `/login?next=…`.
 *  - `staff`  — staff. A guest is redirected to sign in; a signed-in
 *    non-member gets the ordinary "not found" page, so the section does
 *    not announce itself.
 *
 *  The key is the FIRST path segment: a section is one level as a whole.
 *  `tools/check_access.py` fails CI when a route's section is missing here,
 *  and when a `user`/`staff` section has no server guard — so a new page
 *  cannot ship without somebody deciding who it is for.
 *
 *  ⚠️ This is the web layer. The boundary that protects data is the API
 *  (`IsAuthenticatedOrReadOnly`, `StaffGroup`); nothing here replaces it.
 */
export type AccessLevel = "public" | "guest" | "user" | "staff";

export const ACCESS: Readonly<Record<string, AccessLevel>> = {
  "": "public",
  about: "public",
  algorithms: "public",
  arena: "public",
  attempts: "public",
  blog: "public",
  calendar: "public",
  certificates: "public",
  classroom: "public",
  contests: "public",
  duels: "public",
  hackathons: "public",
  leaderboard: "public",
  learn: "public",
  "platform-roadmap": "public",
  privacy: "public",
  problems: "public",
  quizzes: "public",
  qvant: "public",
  rating: "public",
  roadmaps: "public",
  search: "public",
  team: "public",
  terms: "public",
  tournaments: "public",
  updates: "public",
  users: "public",
  // The link in the verification e-mail must open without a session.
  "verify-email": "public",

  login: "guest",
  register: "guest",
  "reset-password": "guest",

  notifications: "user",
  onboarding: "user",
  settings: "user",

  admin: "staff",
};

/** The level of everything that is not listed. */
const OPEN: AccessLevel = "public";

/** First segment of a path: `/settings/profil?x=1` → `settings`. */
export function sectionOf(pathname: string): string {
  const path = pathname.split(/[?#]/, 1)[0] ?? "";
  return path.split("/").filter(Boolean)[0] ?? "";
}

/** The level of a path. An unknown section is public: a typo must end in
 *  the 404 page, not in a redirect to sign in. */
export function accessFor(pathname: string): AccessLevel {
  const section = sectionOf(pathname);
  return Object.hasOwn(ACCESS, section) ? (ACCESS[section] ?? OPEN) : OPEN;
}

/** A guest cannot see this path at all (as opposed to a block inside it). */
export function needsSignIn(pathname: string): boolean {
  const level = accessFor(pathname);
  return level === "user" || level === "staff";
}

/** Only an inner path may be returned to — the open-redirect guard. */
function innerPath(value: string | null | undefined): string | null {
  if (!value || !value.startsWith("/")) return null;
  if (value.startsWith("//") || value.startsWith("/\\")) return null;
  return value;
}

/** Where to send somebody to sign in, and back afterwards.
 *
 *  `next` that points at a sign-in page itself is dropped: returning to
 *  `/login` after signing in would bounce once more for nothing. */
export function loginHref(
  next?: string | null,
  tab: "login" | "register" = "login",
): string {
  const back = innerPath(next);
  const useful = back !== null && accessFor(back) !== "guest";
  const query = new URLSearchParams({ tab });
  if (useful) query.set("next", back);
  return `/login?${query.toString()}`;
}
