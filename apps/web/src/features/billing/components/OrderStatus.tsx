"use client";

import type { Route } from "next";
import { useEffect, useState } from "react";

import { ButtonLink } from "@/components/ui/Button";
import { Status } from "@/components/ui/Status";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { getJson } from "@/lib/api";

import type { BillingOrder } from "../api/billing";

/** Polls for ~1 minute: the provider calls our API, not this page. */
const POLL_MS = 3000;
const POLL_TIMES = 20;

const TONES: Record<string, string> = { paid: "ok", pending: "info", cancelled: "bad", refunded: "warn" };

const MESSAGES: Record<string, string> = {
  pending: "billing.return.pending",
  paid: "billing.return.paid",
  cancelled: "billing.return.cancelled",
  refunded: "billing.return.refunded",
};

/** After the provider's page: wait for its callback to mark the order. */
export function OrderStatus({ initial }: { initial: BillingOrder }) {
  const locale = useLocale();
  const [order, setOrder] = useState(initial);
  const [tries, setTries] = useState(0);

  useEffect(() => {
    if (order.status !== "pending" || tries >= POLL_TIMES) return;
    const timer = window.setTimeout(() => {
      getJson<BillingOrder>(`/billing/orders/${order.id}/`)
        .then(setOrder)
        .catch(() => {})
        .finally(() => setTries((n) => n + 1));
    }, POLL_MS);
    return () => window.clearTimeout(timer);
  }, [order, tries]);

  const tone = TONES[order.status] ?? "info";
  const slow = order.status === "pending" && tries >= POLL_TIMES;

  return (
    <div className="space-y-4">
      <Status status={tone} variant="alert" live label={t(locale, MESSAGES[order.status] ?? "billing.return.pending")} />
      {slow && <p className="text-theme-sm rw-dim">{t(locale, "billing.return.slow")}</p>}
      <div className="flex flex-wrap gap-3">
        {order.status === "paid" && order.course && (
          <ButtonLink href={`/courses/${encodeURIComponent(order.course.slug)}` as Route}>
            {t(locale, "billing.return.toCourse")}
          </ButtonLink>
        )}
        <ButtonLink href={"/plans" as Route} variant={order.status === "paid" && order.course ? "outline" : "primary"}>
          {t(locale, "billing.return.toPlans")}
        </ButtonLink>
      </div>
    </div>
  );
}
