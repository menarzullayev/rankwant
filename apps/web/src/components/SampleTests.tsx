"use client";

import { useState } from "react";

import { Card } from "@/components/ui/Card";
import { Icon } from "@/components/ui/Icon";
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
function CopyButton({ text, label }: { text: string; label: string }) {
  const locale = useLocale();
  const [done, setDone] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      // HTTPS bo'lmagan yoki ruxsat berilmagan kontekst — matn baribir
      // ko'rinib turibdi, qo'lda belgilash mumkin.
      return;
    }
    setDone(true);
    setTimeout(() => setDone(false), 1500);
  }

  return (
    <button
      type="button"
      onClick={copy}
      aria-label={label}
      title={done ? t(locale, "problem.copied") : t(locale, "problem.copy")}
      className={`shrink-0 rw-radius-sm p-1 transition rw-hover-bg ${
        done ? "rw-ok-ink" : "rw-faint"
      }`}
    >
      <Icon name="action.copy" className="size-3.5" />
    </button>
  );
}

function Cell({ text, label }: { text: string; label: string }) {
  return (
    <td className="border-l rw-divider px-2 py-1.5 align-top">
      <div className="flex items-start gap-1">
        <pre className="min-w-0 grow overflow-auto rw-radius-sm rw-field-bg p-2 font-mono text-theme-xs rw-strong [max-height:14rem]">
          {text}
        </pre>
        <CopyButton text={text} label={label} />
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
