import { Card } from "@/components/ui/Card";
import { getLocale } from "@/i18n/server";
import { t, type MessageKey } from "@/i18n/messages";

const STEPS: { title: MessageKey; body: MessageKey }[] = [
  { title: "about.journey.solveTitle", body: "about.journey.solveBody" },
  { title: "about.journey.measureTitle", body: "about.journey.measureBody" },
  { title: "about.journey.competeTitle", body: "about.journey.competeBody" },
  { title: "about.journey.qvantTitle", body: "about.journey.qvantBody" },
  { title: "about.journey.transparencyTitle", body: "about.journey.transparencyBody" },
];

/** Qisqa platforma yo'li — reyting shaffofligi; tizim yo'riqnomasidan oldin. */
export async function AboutJourney() {
  const locale = await getLocale();
  return (
    <ol className="space-y-4">
      {STEPS.map(({ title, body }, i) => (
        <li key={title}>
          <Card>
            <div className="flex gap-4">
              <span className="flex size-9 shrink-0 items-center justify-center rounded-full rw-accent-soft font-bold rw-accent-ink">
                {i + 1}
              </span>
              <div>
                <p className="font-semibold rw-strong">{t(locale, title)}</p>
                <p className="mt-1 text-theme-sm rw-dim">{t(locale, body)}</p>
              </div>
            </div>
          </Card>
        </li>
      ))}
    </ol>
  );
}
