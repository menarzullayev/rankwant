/** The commit this web image was built from (2026-10-27).
 *
 *  `/api/v1/version/` answers for the API image only. A deploy rebuilds just
 *  what changed, so after a web-only change it keeps reporting the old
 *  commit and reads as «the deploy did not happen» (it did: 2026-10-27).
 *  This is the web app's own answer, read from the same build argument the
 *  image label carries.
 *
 *  `force-dynamic` and `no-store`: a cached answer would report a deploy that
 *  already happened as missing. */
export const dynamic = "force-dynamic";

export function GET(): Response {
  return Response.json(
    { sha: process.env.GIT_SHA || "unknown" },
    { headers: { "Cache-Control": "no-store" } },
  );
}
