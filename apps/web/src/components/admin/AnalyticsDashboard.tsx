"use client";

import { useEffect, useState } from "react";

import { Card } from "@/components/ui/Card";
import { Status } from "@/components/ui/Status";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t, type MessageKey } from "@/i18n/messages";
import { ApiError } from "@/lib/api";
import { staff } from "@/lib/staff";

type FunnelRow = { name: string; sessions: number; share: number };
type CountRow = { sessions: number };

type Data = {
  window_days: number;
  total_events: number;
  funnel: FunnelRow[];
  step2: { saved: number; skipped: number; skipped_share: number };
  variant: { control: number; variant: number; total: number; control_share: number };
  errors: { reason: string; sessions: number }[];
  locales: ({ locale: string } & CountRow)[];
  countries: ({ country: string } & CountRow)[];
  daily: { date: string; started: number; done: number }[];
};

/** Hodisa nomi → odam o'qiydigan yorliq.
 *
 *  Xom nom ko'rsatilsa xodim har safar `auth.form_started` ni
 *  o'qib ma'nosini o'ylab ko'rardi. Noma'lum nom bo'lsa o'zi
 *  ko'rsatiladi — yangi hodisa qo'shilganda dashboard uni
 *  yashirmasligi kerak. */
const EVENT_LABEL: Record<string, MessageKey> = {
  "auth.form_started": "admin.text.eventFormStarted",
  "auth.register_done": "admin.text.eventRegisterDone",
};

/** Xato sababi → yorliq. Sabablar `AuthForm` dagi `track` chaqiruvlaridan. */
const REASON_LABEL: Record<string, MessageKey> = {
  username_taken: "admin.text.reasonLoginTaken",
  password_mismatch: "admin.text.reasonPasswordMismatch",
  terms: "admin.text.reasonTermsNotAccepted",
  email: "admin.text.reasonEmailTaken",
  server: "admin.text.reasonServerError",
  network: "admin.text.reasonNetworkError",
  "—": "admin.text.reasonUnknown",
};

const WINDOWS = [7, 30, 90] as const;

export function AnalyticsDashboard() {
  const locale = useLocale();
  const [days, setDays] = useState<number>(30);
  // Natija QAYSI oyna uchun kelgani bilan saqlanadi. «Yuklanmoqda»
  // holati shundan hosil qilinadi — uni effekt ichida `setState` bilan
  // yozish shart emas: aks holda har oyna almashishida qo'shimcha
  // render ketadi (`react-hooks/set-state-in-effect`).
  const [result, setResult] = useState<{ for: number; data?: Data; error?: string }>({
    for: 0,
  });

  const busy = result.for !== days;
  const data = result.for === days ? result.data : undefined;
  const error = result.for === days ? (result.error ?? "") : "";

  useEffect(() => {
    // Bekor qilish bayrog'i: oyna tez almashtirilsa eski javob yangisidan
    // keyin kelib, ekranda eski raqamlar qolib ketishi mumkin edi.
    let stale = false;
    staff
      .get<Data>(`/staff/analytics/?days=${days}`)
      .then((d) => {
        if (!stale) setResult({ for: days, data: d });
      })
      .catch((err) => {
        if (!stale) {
          setResult({
            for: days,
            error: err instanceof ApiError ? err.text : String(err),
          });
        }
      });
    return () => {
      stale = true;
    };
  }, [days]);

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center gap-2">
        {WINDOWS.map((w) => (
          <button
            key={w}
            type="button"
            onClick={() => setDays(w)}
            aria-pressed={days === w}
            className={`rw-radius-sm px-3 py-1.5 text-theme-sm font-medium transition rw-focus-ring ${
              days === w ? "rw-accent-bg" : "rw-dim-2 rw-hover-bg"
            }`}
          >
            {w} kun
          </button>
        ))}
        {busy && <span className="text-theme-xs rw-faint">{t(locale, "admin.text.loading")}</span>}
      </div>

      {error && <Status status="bad" variant="alert" alert label={error} />}

      {data && (
        <>
          <Card title={t(locale, "admin.title.signupFunnel")}>
            {data.total_events === 0 ? (
              <p className="text-theme-sm rw-dim">
                {t(locale, "admin.text.noEventsInWindow")}
              </p>
            ) : (
              <div className="space-y-4">
                {data.funnel.map((row, i) => (
                  <div key={row.name}>
                    <div className="mb-1.5 flex flex-wrap items-baseline justify-between gap-2">
                      <span className="text-theme-sm rw-strong">
                        {EVENT_LABEL[row.name] ?? row.name}
                      </span>
                      <span className="text-theme-sm rw-dim">
                        {row.sessions} sessiya · {row.share}%
                      </span>
                    </div>
                    <div
                      className="h-2.5 overflow-hidden rw-radius-sm rw-hover-bg"
                      role="img"
                      aria-label={fill(t(locale, "admin.text.eventSessions"), {
                          name: EVENT_LABEL[row.name]
                            ? t(locale, EVENT_LABEL[row.name])
                            : row.name,
                          sessions: row.sessions,
                          share: row.share,
                        })}
                    >
                      {/* Rang to'g'ridan-to'g'ri tokenlardan: `rw-ok-bg`
                          kabi klass yo'q, inline `var(--rw-*)` esa 12
                          uslubda ham to'g'ri keladi. */}
                      <div
                        className="h-full"
                        style={{
                          width: `${Math.min(row.share, 100)}%`,
                          background: i === 0 ? "var(--rw-accent)" : "var(--rw-ok-ink)",
                        }}
                      />
                    </div>
                  </div>
                ))}
                <p className="text-theme-xs rw-faint">
                  {t(locale, "admin.text.funnelNote")}
                </p>
              </div>
            )}
          </Card>

          <Card title={t(locale, "admin.title.abRegion")}>
            {data.variant.total === 0 ? (
              <p className="text-theme-sm rw-dim">
                {t(locale, "admin.text.noSignupYet")}
              </p>
            ) : (
              <div className="space-y-3">
                <BarList
                  rows={[
                    { label: t(locale, "admin.label.ab.control"), value: data.variant.control },
                    { label: t(locale, "admin.label.ab.variant"), value: data.variant.variant },
                  ]}
                />
                <p className="text-theme-xs rw-faint">
                  Guruhlar {data.variant.control_share}% /{" "}
                  {(100 - data.variant.control_share).toFixed(1)}%. Teng
                  bo&apos;lmasa natija ishonchsiz — guruh cookie&apos;si
                  tozalangan bo&apos;lishi mumkin.
                </p>
              </div>
            )}
          </Card>

          <div className="grid gap-4 sm:grid-cols-2">
            <Card title={t(locale, "admin.text.step2Funnel")}>
              <div className="flex items-baseline gap-3">
                <span className="text-title-sm font-bold rw-strong">
                  {data.step2.skipped_share}%
                </span>
                <span className="text-theme-sm rw-dim">{t(locale, "admin.text.skipped")}</span>
              </div>
              <p className="mt-2 text-theme-sm rw-dim">
                {data.step2.saved} saqladi · {data.step2.skipped} o&apos;tkazib yubordi
              </p>
              <p className="mt-2 text-theme-xs rw-faint">
                {t(locale, "admin.text.highSkipRate")}
              </p>
            </Card>

            <Card title={t(locale, "admin.title.total")}>
              <div className="text-title-sm font-bold rw-strong">{data.total_events}</div>
              <p className="mt-2 text-theme-sm rw-dim">
                hodisa · oxirgi {data.window_days} kun
              </p>
            </Card>
          </div>

          <Card title={t(locale, "admin.title.errorReasons")}>
            {data.errors.length === 0 ? (
              <p className="text-theme-sm rw-dim">{t(locale, "admin.text.noErrors")}</p>
            ) : (
              <BarList
                rows={data.errors.map((e) => ({
                  label: REASON_LABEL[e.reason]
                    ? t(locale, REASON_LABEL[e.reason])
                    : e.reason,
                  value: e.sessions,
                }))}
              />
            )}
          </Card>

          <div className="grid gap-4 sm:grid-cols-2">
            <Card title={t(locale, "admin.title.languages")}>
              {data.locales.length === 0 ? (
                <p className="text-theme-sm rw-dim">{t(locale, "admin.text.noData")}</p>
              ) : (
                <BarList
                  rows={data.locales.map((l) => ({ label: l.locale, value: l.sessions }))}
                />
              )}
            </Card>
            <Card title={t(locale, "admin.title.countries")}>
              {data.countries.length === 0 ? (
                <p className="text-theme-sm rw-dim">
                  {t(locale, "admin.text.noDataCountries")}
                </p>
              ) : (
                <BarList
                  rows={data.countries.map((c) => ({ label: c.country, value: c.sessions }))}
                />
              )}
            </Card>
          </div>

          <Card title={t(locale, "admin.title.daily")}>
            {data.daily.length === 0 ? (
              <p className="text-theme-sm rw-dim">{t(locale, "admin.text.noData")}</p>
            ) : (
              <Daily rows={data.daily} />
            )}
          </Card>
        </>
      )}
    </div>
  );
}

/** Gorizontal ustunlar ro'yxati — eng kattasi 100% deb olinadi. */
function BarList({ rows }: { rows: { label: string; value: number }[] }) {
  const max = Math.max(...rows.map((r) => r.value), 1);
  return (
    <ul className="space-y-2">
      {rows.map((r) => (
        <li key={r.label} className="flex items-center gap-3">
          <span className="w-40 shrink-0 truncate text-theme-sm rw-strong">{r.label}</span>
          <span className="h-2 flex-1 overflow-hidden rw-radius-sm rw-hover-bg">
            <span
              className="block h-full rw-accent-bg"
              style={{ width: `${(r.value / max) * 100}%` }}
            />
          </span>
          <span className="w-10 shrink-0 text-right text-theme-sm rw-dim">{r.value}</span>
        </li>
      ))}
    </ul>
  );
}

/** Kunlik ustunlar — balandlik eng katta qiymatga nisbatan. */
function Daily({ rows }: { rows: { date: string; started: number; done: number }[] }) {
  const locale = useLocale();
  const max = Math.max(...rows.map((r) => r.started), 1);
  return (
    <div>
      <div className="flex items-end gap-1" style={{ height: 120 }}>
        {rows.map((r) => (
          <span
            key={r.date}
            className="flex flex-1 flex-col justify-end gap-0.5"
            title={fill(t(locale, "admin.text.funnelDay"), {
              date: r.date,
              started: r.started,
              done: r.done,
            })}
          >
            <span
              className="w-full rw-hover-bg"
              style={{ height: `${(r.started / max) * 100}%` }}
            />
            <span
              className="w-full rw-accent-bg"
              style={{ height: `${(r.done / max) * 100}%` }}
            />
          </span>
        ))}
      </div>
      <p className="mt-2 text-theme-xs rw-faint">
        {t(locale, "admin.text.dailyLegend")}
      </p>
    </div>
  );
}
