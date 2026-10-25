/** Illustration data for the `/login` brand panel (slides 1, 6 and 7).
 *
 *  None of it is shown to the visitor as a fact: it is a drawing of what
 *  the platform looks like. It lives in a `.ts` file, not in the slides'
 *  JSX, because source code and verdict codes are not interface copy and
 *  must not be translated or flagged as untranslated text. */

/** Token class → text; `""` is plain. Rendered inside a `<pre>`. */
export type CodeToken = readonly [kind: "" | "ap-kw" | "ap-fn", text: string];

export const CODE: ReadonlyArray<readonly CodeToken[]> = [
  [["ap-kw", "import"], ["", " sys"]],
  [["", " "]],
  [["ap-kw", "def"], ["", " "], ["ap-fn", "solve"], ["", "(a):"]],
  [["", "    best = cur = a[0]"]],
  [["", "    "], ["ap-kw", "for"], ["", " x "], ["ap-kw", "in"], ["", " a[1:]:"]],
  [["", "        cur = "], ["ap-fn", "max"], ["", "(x, cur + x)"]],
  [["", "        best = "], ["ap-fn", "max"], ["", "(best, cur)"]],
];

export const TAB_FILES = { active: "solution.py", other: "solution.cpp", language: "Python 3" } as const;

/** Slide 6: [class, code, message key, `{n}`, time]. */
export const VERDICTS: ReadonlyArray<readonly [string, string, string, string, string]> = [
  ["v-ac", "AC", "s6.allTests", "", "0.04"],
  ["v-wa", "WA", "s6.wrongAt", "3", "0.02"],
  ["v-ac", "AC", "s6.allTests", "", "0.11"],
  ["v-tle", "TLE", "s6.timeAt", "7", "2.00"],
  ["v-ac", "AC", "s6.allTests", "", "0.03"],
  ["v-ce", "CE", "s6.compile", "", "—"],
  ["v-mle", "MLE", "s6.memoryAt", "5", "256"],
  ["v-ac", "AC", "s6.allTests", "", "0.07"],
];

const FAINT = "c1";
const SHADES = ["", "c1", "c2", "c3"] as const;

/** Slide 7: 15 weeks × 7 days laid out row by row, the last week lit as the
 *  streak. A fixed pattern, not data. */
export function heatCells(): string[] {
  const weeks: string[][] = [];
  for (let week = 0; week < 15; week++) {
    const column: string[] = [];
    for (let day = 0; day < 7; day++) {
      if (week === 14) column.push("cs");
      else if (week < 3) column.push((week * 7 + day) % 7 === 0 ? FAINT : "");
      else column.push(SHADES[(week * 5 + day * 3 + week * day) % 5 % 4]);
    }
    weeks.push(column);
  }
  const rows: string[] = [];
  for (let day = 0; day < 7; day++) for (const column of weeks) rows.push(column[day]);
  return rows;
}
