"use client";

import { useEffect, useState } from "react";

import { Card } from "@/components/ui/Card";
import { Segmented } from "@/components/ui/Segmented";
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

/** Tanlanadigan kun. `today` — so'rovda `when` UMUMAN yuborilmaydi. */
type Day = "today" | "yesterday" | "week";

/** `when` uchun ISO 8601 qiymat — tanlangan kun uchun.
 *
 *  ⚠️ Ataylab **UTC** (`...Z`): API mintaqasiz qiymatni UTC deb o'qiydi
 *  (`staff_views.StaffEmailQuotaView._when`), kun chegarasi ham UTC
 *  (`mail_quota.day_start`). Mahalliy vaqt yuborilsa chegara 5 soatga
 *  siljib ketardi — o'lchandi 2026-09-17: `?when=` mahalliy bilan 698
 *  qaytardi, 299 o'rniga. `toISOString()` har doim `Z` beradi, ya'ni
 *  format va shartnoma bir xil manbadan.
 *
 *  ⚠️ Kun **UTC** bo'yicha hisoblanadi, Toshkent bo'yicha emas:
 *  `toISOString().slice(0,10)` — Toshkentda 00:00–05:00 oralig'ida bu
 *  «kecha»ni beradi, lekin panelning o'zi ham UTC kunini ko'rsatadi
 *  (izohda shunday yozilgan), ya'ni ikkisi mos keladi. Mahalliy sanani
 *  ishlatish aynan shu izohga zid bo'lardi.
 */
function whenValue(day: Day): string {
  if (day === "today") return "now";
  const d = new Date();
  const days = day === "yesterday" ? 1 : 6;
  return new Date(d.getTime() - days * 86_400_000).toISOString();
}

/** Kunni tanlash tugmalari. */
function DaySelector({ day, onPick }: { day: Day; onPick: (next: Day) => void }) {
  const locale = useLocale();
  return (
    <Segmented<Day>
      value={day}
      onChange={onPick}
      label={t(locale, "admin.quotaWindowLabel")}
      options={[
        { value: "today", label: t(locale, "admin.quotaWindowToday") },
        { value: "yesterday", label: t(locale, "admin.quotaWindowYesterday") },
        { value: "week", label: t(locale, "admin.quotaWindowWeek") },
      ]}
    />
  );
}

/** Kunlik email kvota paneli.
 *
 *  Nega kerak: zanjir bepul planlar ustiga qurilgan (`EMAIL_CHAIN`),
 *  ya'ni «kvota tugadi» kundalik hodisa. Ungacha bu HECH QAYERDA
 *  ko'rinmasdi — provayder jimgina tushib qolardi va faqat
 *  `EmailDelivery` jadvalida iz qolardi.
 *
 *  Ma'lumot `EmailDelivery` dan o'qiladi (alohida hisoblagich yo'q):
 *  ikkinchi haqiqat manbai vaqt o'tib ajralib ketardi.
 *
 *  Kun tanlagich (`when`) — API boshidan qo'llab-quvvatlardi, panel esa
 *  faqat bugunni ko'rsatardi. Ya'ni «kecha nechta ketdi» degan savolga
 *  javob bor edi, lekin uni ko'rish uchun `EmailDelivery` jadvalini
 *  qo'lda ochish kerak edi.
 */
export function EmailQuotaPanel() {
  const locale = useLocale();
  const [day, setDay] = useState<Day>("today");
  // Natija QAYSI so'rovga tegishli ekani bilan saqlanadi. `setResult({})`
  // ni effect ichida chaqirish taqiqlanadi (kaskad render), shuning uchun
  // eski natija o'chirilmaydi — shunchaki mos kelmasa ko'rsatilmaydi.
  // Bu bir vaqtda haqiqiy xatoni ham tuzatadi: aks holda kun
  // almashtirilganda bir zum OLDINGI kunning raqamlari ko'rinib qolardi.
  const [result, setResult] = useState<{ key: string; data?: Data; error?: string }>();

  useEffect(() => {
    let stale = false;
    const key = `${locale}:${day}`;
    // Bugun uchun `when` yuborilmaydi: `None` bilan API `timezone.now()`
    // oladi, ya'ni kun chegarasi so'rov paytida hisoblanadi. Mijozda
    // sanab yuborilsa, sahifa uzoq ochiq turganda eski «bugun» qotib
    // qolardi.
    staff
      .get<Data>(`/staff/email-quota/${day === "today" ? "" : `?when=${whenValue(day)}`}`)
      .then((data) => {
        if (!stale) setResult({ key, data });
      })
      .catch(() => {
        if (!stale) setResult({ key, error: t(locale, "admin.quotaLoadFail") });
      });
    return () => {
      stale = true;
    };
  }, [locale, day]);

  const picker = <DaySelector day={day} onPick={setDay} />;
  // Faqat joriy tanlovga tegishli natija ishlatiladi.
  const current = result?.key === `${locale}:${day}` ? result : undefined;

  if (current?.error) {
    return (
      <div className="space-y-4">
        {picker}
        <Status status="bad" variant="alert" label={current.error} />
      </div>
    );
  }
  if (!current?.data) {
    return (
      <div className="space-y-4">
        {picker}
        <Card>{t(locale, "settings.loading")}</Card>
      </div>
    );
  }

  const data = current.data;
  const past = day !== "today";

  return (
    <div className="space-y-4">
      {picker}

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
          <strong>{t(locale, past ? "admin.quotaSpent" : "admin.quotaTodayLeft")}</strong>{" "}
          <span className="tabular-nums">
            {past ? data.providers.reduce((n, p) => n + p.sent, 0) : data.total_remaining}
          </span>{" "}
          {/* O'tgan kun uchun «qoldi» ma'nosiz: kvota o'sha kuni tugagan
              bo'lishi mumkin, lekin bugun qayta to'ldi — ya'ni «kecha 12
              qoldi» degan raqam bugungi qarorga yaroqsiz. Shu sababli
              o'tgan kun uchun sarf ko'rsatiladi, qoldiq emas. */}
          {!past && (
            <span className="rw-dim">
              {t(locale, "admin.quotaWithQueue").replace("{n}", String(data.total_with_queue))}
            </span>
          )}
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
