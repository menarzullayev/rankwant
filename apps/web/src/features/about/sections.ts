import type { MessageKey } from "@/i18n/messages";
import type { VerdictKey } from "@/lib/theme/verdict";
import { ABOUT_VERDICT_ORDER } from "@/content/about/verdict-guide-order";

/** The page's sections, in reading order. The id is the anchor: it is
 *  shared in links (`/about#verdicts`), so it is the same in every
 *  language and must not be renamed. */
export const ABOUT_SECTIONS = [
  { id: "journey", label: "about.journey.title" },
  { id: "submit", label: "about.toc.submit" },
  { id: "languages", label: "about.toc.languages" },
  { id: "verdicts", label: "about.toc.verdicts" },
  { id: "practices", label: "about.toc.practices" },
  { id: "judge", label: "about.toc.judge" },
] as const satisfies readonly { id: string; label: MessageKey }[];

export type AboutSectionId = (typeof ABOUT_SECTIONS)[number]["id"];

/** Twenty-four codes are not twenty-four equal things: nine are what a
 *  solver meets every day, a few are a submission on its way, the rest
 *  are rare or the platform's own trouble. The table used to give
 *  `DENIAL_OF_JUDGEMENT` the same weight as `WA`. */
const COMMON: VerdictKey[] = ["AC", "WA", "PE", "TLE", "MLE", "CE", "RE_SIGNAL", "RE_EXIT", "PARTIAL"];
const FLOW: VerdictKey[] = ["PENDING", "RUNNING", "TESTING_ABORTED", "SKIPPED", "HACKED"];

export type VerdictGroupId = "common" | "flow" | "system";

export const VERDICT_GROUPS: { id: VerdictGroupId; label: MessageKey; codes: VerdictKey[] }[] = [
  { id: "common", label: "about.verdicts.group.common", codes: COMMON },
  { id: "flow", label: "about.verdicts.group.flow", codes: FLOW },
  {
    id: "system",
    label: "about.verdicts.group.system",
    // Whatever is not named above: a code added to the order later lands
    // here instead of vanishing from the page.
    codes: ABOUT_VERDICT_ORDER.filter((code) => !COMMON.includes(code) && !FLOW.includes(code)),
  },
];
