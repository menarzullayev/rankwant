"use client";

import { useEffect, useState } from "react";

import { Card } from "@/components/ui/Card";
import { Status } from "@/components/ui/Status";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { staff } from "@/lib/staff";

type Provider = {
  name: string;
  sent: number;
  quota: number;
  remaining: number;
  queue: number;
  configured: boolean;
  exhausted: boolean;
  warning: boolean;
  in_queue: boolean;
  lost: number;
  used_ratio: number;
};

type Data = {
  window: string;
  day_start: string;
  providers: Provider[];
  total_remaining: number;
  total_with_queue: number;
  failures: number;
};

/** Kunlik email kvota paneli.
 *
 *  Nega kerak: zanjir bepul planlar ustiga qurilgan (`EMAIL_CHAIN`),
 *  ya'ni «kvota tugadi» kundalik hodisa. Ungacha bu HECH QAYERDA
 *  ko'rinmasdi — provayder jimgina tushib qolardi va faqat
 *  `EmailDelivery` jadvalida iz qolardi.
 *
 *  Ma'lumot `EmailDelivery` dan o'qiladi (alohida hisoblagich yo'q):
 *  ikkinchi haqiqat manbai vaqt o'tib ajralib ketardi.
 */
export function EmailQuotaPanel() {
  const locale = useLocale();
  const [result, setResult] = useState<{ data?: Data; error?: string }>({});

  useEffect(() => {
    let stale = false;
    staff
      .get<Data>("/staff/email-quota/")
      .then((data) => {
        if (!stale) setResult({ data });
      })
      .catch(() => {
        if (!stale) setResult({ error: t(locale, "admin.quotaLoadFail") });
      });
    return () => {
      stale = true;
    };
  }, [locale]);

  if (result.error) return <Status status="bad" variant="alert" label={result.error} />;
  if (!result.data) return <Card>{t(locale, "settings.loading")}</Card>;

  const data = result.data;

  return (
    <div className="space-y-4">
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-theme-sm">
            <thead>
              <tr className="text-left rw-dim">
                <th className="py-2 pr-3 font-medium">{t(locale, "admin.quotaProvider")}</th>
                <th className="py-2 pr-3 text-right font-medium">{t(locale, "admin.quotaSent")}</th>
                <th className="py-2 pr-3 text-right font-medium">{t(locale, "admin.quotaLimit")}</th>
                <th className="py-2 pr-3 text-right font-medium">{t(locale, "admin.quotaLeft")}</th>
                <th className="py-2 font-medium">{t(locale, "admin.quotaState")}</th>
              </tr>
            </thead>
            <tbody>
              {data.providers.map((p) => (
                <tr key={p.name} className="border-t rw-border">
                  <td className="py-2 pr-3">
                    <code>{p.name}</code>
                  </td>
                  <td className="py-2 pr-3 text-right tabular-nums">{p.sent}</td>
                  <td className="py-2 pr-3 text-right tabular-nums">
                    {p.configured ? p.quota : "—"}
                  </td>
                  <td className="py-2 pr-3 text-right tabular-nums">
                    {p.configured ? p.remaining : "—"}
                  </td>
                  <td className="py-2">
                    {p.lost > 0 ? (
                      // Eng qizil holat: navbat ham to'ldi, xat YETKAZILMAYDI.
                      <span className="rw-bad-ink font-medium">
                        {t(locale, "admin.quotaLost").replace("{n}", String(p.lost))}
                      </span>
                    ) : p.in_queue ? (
                      <span className="rw-warn-ink">
                        {t(locale, "admin.quotaInQueue").replace("{n}", String(p.queue))}
                      </span>
                    ) : p.exhausted ? (
                      <span className="rw-warn-ink">{t(locale, "admin.quotaExhausted")}</span>
                    ) : p.warning ? (
                      <span className="rw-warn-ink">
                        {t(locale, "admin.quotaWarning").replace(
                          "{percent}",
                          String(Math.round(p.used_ratio * 100)),
                        )}
                      </span>
                    ) : p.configured ? (
                      <span className="rw-ok-ink">✓</span>
                    ) : (
                      <span className="rw-dim">{t(locale, "admin.quotaUnset")}</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <Card>
        <p className="text-theme-sm">
          <strong>{t(locale, "admin.quotaTodayLeft")}</strong>{" "}
          <span className="tabular-nums">{data.total_remaining}</span>{" "}
          <span className="rw-dim">
            {t(locale, "admin.quotaWithQueue").replace("{n}", String(data.total_with_queue))}
          </span>
          {data.failures > 0 && (
            <>
              {" · "}
              <span className="rw-bad-ink font-medium">
                {t(locale, "admin.quotaFailures").replace("{n}", String(data.failures))}
              </span>
            </>
          )}
        </p>
        <p className="mt-2 text-theme-xs rw-dim">{t(locale, "admin.quotaUtcNote")}</p>
      </Card>
    </div>
  );
}
