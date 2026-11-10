"use client";

import { numericDate } from "@rankwant/shared/format";
import type { Route } from "next";
import { useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { ButtonLink } from "@/components/ui/Button";
import { Segmented } from "@/components/ui/Segmented";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import { loginHref } from "@/lib/access";

import { PERIODS, PLANS_WITH_COURSES, type BillingOverview, type Period, type PlanOffer } from "../api/billing";
import { discountPercent, groupDigits } from "../format";

const PERIOD_KEYS: Record<Period, string> = {
  1: "billing.period.month",
  6: "billing.period.halfYear",
  12: "billing.period.year",
};
const PLAN_KEYS: Record<string, string> = {
  free: "billing.plan.free",
  plus: "billing.plan.plus",
  pro: "billing.plan.pro",
  judge: "billing.plan.judge",
};
/** Buying the current plan again adds a period after the running one. */
const ACTION_KEYS = { guest: "billing.signIn", extend: "billing.extend", choose: "billing.choose" } as const;

function actionKey(signedIn: boolean, current: boolean): string {
  if (!signedIn) return ACTION_KEYS.guest;
  return current ? ACTION_KEYS.extend : ACTION_KEYS.choose;
}
const FREE_FEATURES = ["billing.free.f1", "billing.free.f2", "billing.free.f3", "billing.free.f4"];

/** Four plans side by side; the period switch changes every price at once.
 *  A plan or a period without a price says "soon" instead of a button. */
export function PlanCards({ overview, signedIn }: { overview: BillingOverview; signedIn: boolean }) {
  const locale = useLocale();
  const [months, setMonths] = useState<Period>(12);
  const current = overview.plan;
  const upcoming = overview.periods.filter((p) => !p.running);

  return (
    <div className="space-y-6">
      {current !== "free" && overview.plan_expires_at && (
        <div className="rw-radius border rw-line rw-surface p-4 text-theme-sm">
          <p className="font-medium rw-strong">
            {t(locale, "billing.current")}:{" "}
            {fill(t(locale, "billing.currentUntil"), {
              plan: t(locale, PLAN_KEYS[current] ?? "billing.plan.free"),
              date: numericDate(overview.plan_expires_at),
            })}
          </p>
          {upcoming.map((p) => (
            <p key={`${p.plan}-${p.starts_at}`} className="mt-1 rw-dim">
              {fill(t(locale, "billing.upcoming"), {
                plan: t(locale, PLAN_KEYS[p.plan] ?? "billing.plan.free"),
                start: numericDate(p.starts_at),
                end: numericDate(p.ends_at),
              })}
            </p>
          ))}
        </div>
      )}

      <Segmented<string>
        label={t(locale, "billing.periodLabel")}
        value={String(months)}
        onChange={(next) => setMonths(Number(next) as Period)}
        options={PERIODS.map((m) => ({ value: String(m), label: t(locale, PERIOD_KEYS[m]) }))}
      />

      <ul className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <li className="flex flex-col gap-4 rw-radius border rw-line rw-surface p-5">
          <PlanHead name={t(locale, "billing.plan.free")} current={current === "free"} />
          <p className="text-title-sm font-bold rw-strong">{fill(t(locale, "billing.som"), { price: 0 })}</p>
          <Features lines={FREE_FEATURES.map((key) => t(locale, key))} />
        </li>
        {overview.plans.map((plan) => (
          <PlanCard
            key={plan.code}
            plan={plan}
            months={months}
            current={current === plan.code}
            signedIn={signedIn}
          />
        ))}
      </ul>

      <p className="text-theme-xs rw-faint">{t(locale, "billing.noAutoRenew")}</p>
    </div>
  );
}

function PlanHead({ name, current }: { name: string; current: boolean }) {
  const locale = useLocale();
  return (
    <div className="flex items-center justify-between gap-2">
      <h2 className="text-theme-lg font-semibold rw-strong">{name}</h2>
      {current && <Badge color="brand">{t(locale, "billing.current")}</Badge>}
    </div>
  );
}

function Features({ lines }: { lines: string[] }) {
  return (
    <ul className="space-y-1.5 text-theme-sm rw-dim">
      {lines.map((line) => (
        <li key={line} className="flex gap-2">
          <span aria-hidden="true" className="rw-ok-ink">
            ✓
          </span>
          <span>{line}</span>
        </li>
      ))}
    </ul>
  );
}

function PlanCard({
  plan,
  months,
  current,
  signedIn,
}: {
  plan: PlanOffer;
  months: Period;
  current: boolean;
  signedIn: boolean;
}) {
  const locale = useLocale();
  const price = plan.is_on_sale ? plan.prices.find((p) => p.months === months) : undefined;
  const checkout = `/checkout?plan=${plan.code}&months=${months}`;
  const lines = [
    // Guaranteed by the code, not by the staff-written text.
    ...(PLANS_WITH_COURSES.includes(plan.code) ? [t(locale, "billing.coursesIncluded")] : []),
    ...plan.features,
  ];
  const off = price ? discountPercent(price.amount_uzs, price.list_amount_uzs) : 0;

  return (
    <li className="flex flex-col gap-4 rw-radius border rw-line rw-surface p-5">
      <PlanHead name={t(locale, PLAN_KEYS[plan.code] ?? "billing.plan.free")} current={current} />
      {price ? (
        <div className="space-y-1">
          {price.list_amount_uzs > price.amount_uzs && (
            <p className="text-theme-sm line-through rw-faint">
              {fill(t(locale, "billing.som"), { price: groupDigits(price.list_amount_uzs) })}
            </p>
          )}
          <p className="text-title-sm font-bold rw-strong">
            {fill(t(locale, "billing.som"), { price: groupDigits(price.amount_uzs) })}
          </p>
          <p className="text-theme-xs rw-dim">
            {[
              t(locale, PERIOD_KEYS[months]),
              months > 1
                ? fill(t(locale, "billing.perMonth"), { price: groupDigits(price.amount_uzs / months) })
                : "",
              off ? fill(t(locale, "billing.discount"), { percent: off }) : "",
            ]
              .filter(Boolean)
              .join(" · ")}
          </p>
        </div>
      ) : (
        <p className="text-theme-sm rw-faint">{t(locale, "billing.soon")}</p>
      )}
      <Features lines={lines} />
      {price && (
        <div className="mt-auto">
          <ButtonLink href={(signedIn ? checkout : loginHref(checkout)) as Route} className="w-full">
            {t(locale, actionKey(signedIn, current))}
          </ButtonLink>
        </div>
      )}
    </li>
  );
}
