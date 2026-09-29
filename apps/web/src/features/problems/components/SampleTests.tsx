"use client";

import { Fragment } from "react";

import { CopyButton } from "@/components/kit/CopyControl";
import { Card } from "@/components/ui/Card";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import type { Sample } from "@/lib/api";

import { useProblemSolve } from "./problem-solve-context";

/** Namunalar jadvali.
 *
 * Ilgari har namuna alohida blok edi va «Kirish/Chiqish» yozuvi har
 * safar takrorlanardi — uchta namuna masala matnining 38 % ini
 * egallardi. Jadvalda sarlavha bir marta yoziladi va kirish bilan
 * chiqish bir qatorda turadi, ya'ni ularni taqqoslash osonroq
 * (RoboContest ham shunday qiladi).
 */
function Cell({ text, label }: { text: string; label: string }) {
  return (
    <td className="border-l rw-divider px-2 py-1.5 align-top">
      <div className="flex items-start gap-1">
        <pre className="min-w-0 grow overflow-auto rw-radius-sm rw-field-bg p-2 font-mono text-theme-xs rw-strong [max-height:14rem]">
          {text}
        </pre>
        <CopyButton text={text} tone="ghost" label={label} />
      </div>
    </td>
  );
}

export function SampleTests({ samples }: { samples: Sample[] }) {
  const locale = useLocale();
  const solve = useProblemSolve();
  if (samples.length === 0) return null;

  return (
    <Card title={t(locale, "problem.samples")} bodyClassName="p-0">
      <div className="min-w-0 overflow-x-auto">
        <table className="w-full min-w-[34rem] table-fixed">
          <thead>
            <tr className="border-b rw-divider">
              <th className="w-10 px-3 py-2 text-left text-theme-xs font-medium rw-faint">
                #
              </th>
              <th className="border-l rw-divider px-3 py-2 text-left text-theme-xs font-medium rw-faint">
                {t(locale, "problem.sampleInput")}
              </th>
              <th className="border-l rw-divider px-3 py-2 text-left text-theme-xs font-medium rw-faint">
                {t(locale, "problem.sampleOutput")}
              </th>
              {solve && (
                <th className="w-11 border-l rw-divider px-1 py-2 text-center text-theme-xs font-medium rw-faint">
                  <span className="sr-only">{t(locale, "submit.run")}</span>
                  ▶
                </th>
              )}
            </tr>
          </thead>
          <tbody className="rw-divide divide-y">
            {samples.map((sample) => {
              const inline = solve?.inlineSamples[sample.order];
              return (
                <Fragment key={sample.order}>
                  <tr>
                    <td className="px-3 py-1.5 align-top text-theme-xs rw-faint tabular-nums">
                      {sample.order}
                    </td>
                    <Cell
                      text={sample.input}
                      label={fill(t(locale, "problem.copyInput"), {
                        order: sample.order,
                      })}
                    />
                    <Cell
                      text={sample.expected}
                      label={fill(t(locale, "problem.copyOutput"), {
                        order: sample.order,
                      })}
                    />
                    {solve && (
                      <td className="border-l rw-divider px-1 py-1.5 text-center align-top">
                        <button
                          type="button"
                          aria-label={fill(t(locale, "problem.sampleRun"), {
                            order: sample.order,
                          })}
                          title={fill(t(locale, "problem.sampleRun"), {
                            order: sample.order,
                          })}
                          onClick={() => solve.runSample(sample.order)}
                          className="inline-flex size-7 items-center justify-center rw-radius-sm border rw-divider rw-panel-bg text-theme-xs rw-accent-ink rw-hover-bg rw-focus-ring"
                        >
                          ▶
                        </button>
                      </td>
                    )}
                  </tr>
                  {inline && inline.status === "done" && (
                    <tr key={`${sample.order}-res`}>
                      <td
                        colSpan={solve ? 4 : 3}
                        className="border-t-0 px-3 py-1"
                      >
                        <p
                          className={`font-mono text-theme-xs rw-radius-sm px-2 py-1.5 ${
                            inline.ok ? "rw-ok-soft rw-ok-ink" : "rw-bad-soft rw-bad-ink"
                          }`}
                        >
                          {inline.message}
                        </p>
                      </td>
                    </tr>
                  )}
                  {inline && inline.status === "running" && (
                    <tr key={`${sample.order}-run`}>
                      <td
                        colSpan={solve ? 4 : 3}
                        className="border-t-0 px-3 py-1 text-theme-xs rw-dim"
                      >
                        {t(locale, "submit.sampleConsoleRunning")}
                      </td>
                    </tr>
                  )}
                </Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
