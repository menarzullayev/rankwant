import { Card } from "@/components/ui/Card";
import { Discussion, type ThreadPage } from "@/features/community";
import { t, type Locale } from "@/i18n/messages";
import { ApiError, type ProblemDetail } from "@/lib/api";
import { getWithSession } from "@/lib/api.server";

/** The problem's discussion (decision 2026-11-11).
 *
 *  The first page is drawn on the server, so the text is in the HTML. A
 *  problem still inside a contest is not in the archive and has no
 *  discussion: reading and writing open when the contest is finalized
 *  (ADR-0055). */
export async function ProblemDiscussionPanel({
  problem,
  slug,
  signedIn,
  locale,
}: {
  problem: ProblemDetail;
  slug: string;
  signedIn: boolean;
  locale: Locale;
}) {
  let page: ThreadPage | null = null;
  if (!problem.contest) {
    try {
      page = await getWithSession<ThreadPage>(
        `/discussions/problem/${encodeURIComponent(slug)}/`,
      );
    } catch (error) {
      if (!(error instanceof ApiError && error.status === 404)) throw error;
    }
  }

  if (page === null)
    return (
      <div data-discussion-closed="">
        <Card className="space-y-1 p-5">
          <p className="font-semibold rw-strong">{t(locale, "discussion.closed")}</p>
          <p className="text-theme-sm rw-dim">{t(locale, "discussion.closedHint")}</p>
        </Card>
      </div>
    );

  return (
    <Card className="p-5">
      <Discussion target={{ kind: "problem", ref: slug }} initial={page} signedIn={signedIn} />
    </Card>
  );
}
