"use client";

import type { Route } from "next";
import Link from "next/link";
import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, fill, t } from "@/i18n/messages";
import { ApiError } from "@/lib/api";

import { createOrder, type PaidPlan, type PaymentProvider, type Period } from "../api/billing";
import { groupDigits } from "../format";

const PROVIDER_KEYS: Record<string, string> = {
  click: "billing.provider.click",
  payme: "billing.provider.payme",
};

export type CheckoutItem =
  | { kind: "plan"; plan: PaidPlan; months: Period }
  | { kind: "course"; course: string };

/** Confirm and go to the provider's page. Nothing is charged here: the
 *  order is created, then Click or Payme takes the card on their own page,
 *  and the access opens when they call back (ADR-0057). */
export function CheckoutForm({
  item,
  title,
  amount,
  providers,
  startsAt,
}: {
  item: CheckoutItem;
  title: string;
  amount: number;
  providers: string[];
  /** A plan period that begins after the current one, if so. */
  startsAt?: string;
}) {
  const locale = useLocale();
  const [provider, setProvider] = useState<string>(providers[0] ?? "");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function pay(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!provider) return;
    setBusy(true);
    setError("");
    try {
      const order = await createOrder({ ...item, provider: provider as PaymentProvider });
      if (!order.pay_url) throw new Error(t(locale, "error.error"));
      window.location.assign(order.pay_url);
    } catch (err) {
      setError(err instanceof ApiError ? errorText(locale, err.code, err.message) : String(err));
      setBusy(false);
    }
  }

  return (
    <form onSubmit={pay} className="space-y-5 rw-radius border rw-line rw-surface p-5">
      <dl className="space-y-3 text-theme-sm">
        <div className="flex justify-between gap-4">
          <dt className="rw-dim">{t(locale, "billing.checkout.item")}</dt>
          <dd className="text-right font-medium rw-strong">{title}</dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="rw-dim">{t(locale, "billing.checkout.amount")}</dt>
          <dd className="text-right text-theme-lg font-bold rw-strong">
            {fill(t(locale, "billing.som"), { price: groupDigits(amount) })}
          </dd>
        </div>
      </dl>
      {startsAt && <p className="text-theme-sm rw-dim">{fill(t(locale, "billing.checkout.startsLater"), { date: startsAt })}</p>}

      {providers.length === 0 ? (
        <p role="alert" className="text-theme-sm rw-bad-ink">
          {t(locale, "billing.checkout.noProvider")}
        </p>
      ) : (
        <fieldset className="space-y-2">
          <legend className="mb-2 text-theme-sm font-medium rw-strong">{t(locale, "billing.checkout.provider")}</legend>
          {providers.map((code) => (
            <label
              key={code}
              className="flex min-h-11 cursor-pointer items-center gap-3 rw-radius border rw-line px-4 py-2 rw-focus-ring"
            >
              <input
                type="radio"
                name="provider"
                value={code}
                checked={provider === code}
                onChange={() => setProvider(code)}
              />
              <span className="font-medium rw-strong">{t(locale, PROVIDER_KEYS[code] ?? "billing.provider.click")}</span>
            </label>
          ))}
        </fieldset>
      )}

      <div className="space-y-1.5 text-theme-xs rw-dim">
        <p>{t(locale, "billing.noAutoRenew")}</p>
        <p>{t(locale, "billing.minorConsent")}</p>
        <p>
          {t(locale, "billing.termsAccept")}{" "}
          <Link href={"/terms" as Route} className="rw-accent-ink hover:underline">
            {t(locale, "billing.terms")}
          </Link>
        </p>
      </div>

      {error && (
        <p role="alert" className="text-theme-sm rw-bad-ink">
          {error}
        </p>
      )}
      <Button type="submit" busy={busy} disabled={!provider} className="w-full">
        {fill(t(locale, "billing.checkout.pay"), { price: groupDigits(amount) })}
      </Button>
    </form>
  );
}
