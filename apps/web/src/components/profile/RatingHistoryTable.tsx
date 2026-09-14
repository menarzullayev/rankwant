import {
  EmptyRow,
  TBody,
  TD,
  TH,
  THead,
  TR,
  Table,
} from "@/components/ui/Table";
import { t, type Locale } from "@/i18n/messages";
import type { RatingChange } from "@/lib/api";
import { formatDate } from "@/lib/format";

/** Principle #2 ning ko'rinadigan qismi: har o'zgarish sababi bilan. */
export function RatingHistoryTable({ rows, locale }: { rows: RatingChange[]; locale: Locale }) {
  return (
    <div className="overflow-hidden rw-radius border rw-line">
      <Table>
        <THead>
          <TH>{t(locale, "profile.ratingColumn")}</TH>
          <TH align="right">{t(locale, "profile.change")}</TH>
          <TH>{t(locale, "profile.reason")}</TH>
          <TH align="right">{t(locale, "profile.date")}</TH>
        </THead>
        <TBody>
          {rows.map((row, i) => (
            <TR key={`${row.created_at}-${i}`}>
              <TD className="font-medium rw-strong">{row.rating_type}</TD>
              <TD align="right">
                <span className={row.delta >= 0 ? "font-semibold rw-ok-ink" : "font-semibold rw-bad-ink"}>
                  {row.delta > 0 ? "+" : ""}
                  {row.delta}
                </span>
              </TD>
              <TD className="rw-dim">
                {t(locale, `profile.reason.${row.reason}`)}
                {row.rank !== null && ` · #${row.rank}`}
                {row.ref_id && ` · ${row.ref_id}`}
              </TD>
              <TD align="right" className="rw-faint">
                {formatDate(row.created_at, locale)}
              </TD>
            </TR>
          ))}
          {rows.length === 0 && <EmptyRow colSpan={4}>{t(locale, "common.empty")}</EmptyRow>}
        </TBody>
      </Table>
    </div>
  );
}
