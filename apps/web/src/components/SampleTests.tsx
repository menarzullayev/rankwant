"use client";

import { CopyButton } from "@/components/kit/CopyControl";
import { Card } from "@/components/ui/Card";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import type { Sample } from "@/lib/api";

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
  if (samples.length === 0) return null;

  return (
    <Card title={t(locale, "problem.samples")} bodyClassName="p-0">
      {/* Kod ustunlari tor ekranga sig'maydi — jadval o'z ichida
          gorizontal aylanadi, sahifa emas. */}
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
            </tr>
          </thead>
          <tbody className="rw-divide divide-y">
            {samples.map((sample) => (
              <tr key={sample.order}>
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
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
