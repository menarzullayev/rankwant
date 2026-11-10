"use client";

import { useState } from "react";

import { FormCheck } from "@/components/form/FormKit";
import { FM_INP, FM_LAB } from "@/components/form/chrome";
import { useConfirm } from "@/components/overlay/OverlayHost";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { EmptyRow, TBody, TD, TH, THead, TR, Table } from "@/components/ui/Table";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, fill, t } from "@/i18n/messages";
import { ApiError } from "@/lib/api";

import { studioProblems, type DraftTest } from "../api/problems";

/** The draft's tests. The text goes to storage and is not read back here
 *  (the API returns only references), so replacing a test means writing it
 *  again under the same number. */
export function DraftTests({
  slug,
  locked,
  tests,
  onChange,
}: {
  slug: string;
  /** Published: tests belong to staff-ops (ADR-0025). */
  locked: boolean;
  tests: DraftTest[];
  onChange: (tests: DraftTest[]) => void;
}) {
  const locale = useLocale();
  const confirm = useConfirm();
  const nextOrder = tests.reduce((max, row) => Math.max(max, row.order), 0) + 1;
  const [order, setOrder] = useState<number | null>(null);
  const [input, setInput] = useState("");
  const [expected, setExpected] = useState("");
  const [sample, setSample] = useState(tests.length === 0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const target = order ?? nextOrder;

  async function reload() {
    onChange(await studioProblems.tests(slug));
  }

  async function save(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await studioProblems.saveTest(slug, { order: target, input, expected, is_sample: sample });
      setInput("");
      setExpected("");
      setOrder(null);
      setSample(false);
      await reload();
    } catch (err) {
      setError(err instanceof ApiError ? errorText(locale, err.code) : String(err));
    } finally {
      setBusy(false);
    }
  }

  async function remove(row: DraftTest, origin: HTMLElement) {
    const ok = await confirm(fill(t(locale, "studio.tests.deleteConfirm"), { order: row.order }), {
      danger: true,
      confirmLabel: t(locale, "studio.tests.delete"),
      origin,
    });
    if (!ok) return;
    setError("");
    try {
      await studioProblems.removeTest(slug, row.order);
      await reload();
    } catch (err) {
      setError(err instanceof ApiError ? errorText(locale, err.code) : String(err));
    }
  }

  return (
    <div className="space-y-4">
      <Table>
        <THead>
          <TH>{t(locale, "studio.tests.order")}</TH>
          <TH>{t(locale, "studio.tests.kind")}</TH>
          <TH align="right">{t(locale, "studio.tests.actions")}</TH>
        </THead>
        <TBody>
          {tests.length === 0 ? (
            <EmptyRow colSpan={3}>{t(locale, "studio.tests.empty")}</EmptyRow>
          ) : (
            tests.map((row) => (
              <TR key={row.order}>
                <TD className="tabular-nums">{row.order}</TD>
                <TD>
                  <Badge color={row.is_sample ? "info" : "neutral"}>
                    {t(locale, row.is_sample ? "studio.tests.sample" : "studio.tests.hidden")}
                  </Badge>
                </TD>
                <TD align="right">
                  {!locked && (
                    <span className="inline-flex flex-wrap justify-end gap-2">
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => {
                          setOrder(row.order);
                          setSample(row.is_sample);
                        }}
                      >
                        {t(locale, "studio.tests.replace")}
                      </Button>
                      <Button
                        type="button"
                        variant="outline"
                        className="rw-bad-ink"
                        onClick={(event) => void remove(row, event.currentTarget)}
                      >
                        {t(locale, "studio.tests.delete")}
                      </Button>
                    </span>
                  )}
                </TD>
              </TR>
            ))
          )}
        </TBody>
      </Table>

      {locked ? (
        <p className="text-theme-sm rw-dim">{t(locale, "studio.tests.locked")}</p>
      ) : (
        <form onSubmit={save} className="space-y-3 rw-radius-sm border rw-line p-4">
          <p className="text-theme-sm font-medium rw-strong">
            {fill(t(locale, order === null ? "studio.tests.adding" : "studio.tests.replacing"), {
              order: target,
            })}
          </p>
          <div className="grid gap-3 md:grid-cols-2">
            <label className="block">
              <span className={FM_LAB}>{t(locale, "problem.sampleInput")}</span>
              <textarea
                value={input}
                onChange={(event) => setInput(event.target.value)}
                rows={6}
                spellCheck={false}
                className={`${FM_INP} font-mono`}
              />
            </label>
            <label className="block">
              <span className={FM_LAB}>{t(locale, "studio.tests.expected")}</span>
              <textarea
                value={expected}
                onChange={(event) => setExpected(event.target.value)}
                rows={6}
                spellCheck={false}
                className={`${FM_INP} font-mono`}
              />
            </label>
          </div>
          <FormCheck
            checked={sample}
            onChange={(event) => setSample(event.target.checked)}
            label={t(locale, "studio.tests.isSample")}
            hint={t(locale, "studio.tests.isSampleHint")}
          />
          <p className="text-theme-xs rw-faint">{t(locale, "studio.tests.note")}</p>
          {error && (
            <p role="alert" className="text-theme-sm rw-bad-ink">
              {error}
            </p>
          )}
          <div className="flex flex-wrap justify-end gap-2">
            {order !== null && (
              <Button type="button" variant="outline" onClick={() => setOrder(null)}>
                {t(locale, "studio.cancel")}
              </Button>
            )}
            <Button type="submit" busy={busy}>
              {t(locale, "studio.tests.save")}
            </Button>
          </div>
        </form>
      )}
    </div>
  );
}
