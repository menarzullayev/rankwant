/** What the team page is showing, and how that is written in its address.
 *
 *  No React here: the server page reads the address with `readTeamView`,
 *  the directory writes it back with `teamHref`. */

export const ALL_DEPARTMENTS = -1;

export type TeamView = {
  /** A department's id, or `ALL_DEPARTMENTS`. */
  dept: number;
  query: string;
  /** The page without the joke: the one person, the links. */
  serious: boolean;
};

const QUERY_MAX = 60;

type Raw = string | string[] | undefined;
const one = (value: Raw): string => (Array.isArray(value) ? (value[0] ?? "") : (value ?? ""));

/** `?dept=3&q=dizayn&view=serious`. Anything it cannot read is the
 *  default, never an error: the address is typed and shared by hand. */
export function readTeamView(
  params: Record<string, Raw>,
  departments: readonly number[],
): TeamView {
  const dept = Number(one(params.dept));
  return {
    dept: Number.isInteger(dept) && departments.includes(dept) ? dept : ALL_DEPARTMENTS,
    query: one(params.q).slice(0, QUERY_MAX),
    serious: one(params.view) === "serious",
  };
}

/** The address of a view. The serious page has no filter, so it carries none. */
export function teamHref(view: TeamView): string {
  const params = new URLSearchParams();
  if (view.serious) params.set("view", "serious");
  else {
    if (view.dept !== ALL_DEPARTMENTS) params.set("dept", String(view.dept));
    const query = view.query.trim();
    if (query) params.set("q", query);
  }
  const search = params.toString();
  return search ? `/team?${search}` : "/team";
}
