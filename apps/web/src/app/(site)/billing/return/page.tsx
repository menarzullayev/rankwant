import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { OrderStatus, type BillingOrder } from "@/features/billing";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";
import { ApiError } from "@/lib/api";
import { requireUser } from "@/lib/access.server";
import { getWithSession } from "@/lib/api.server";
import { isOnServer } from "@/lib/flags";

export const dynamic = "force-dynamic";

type Props = { searchParams: Promise<{ order?: string }> };

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "billing.return.title"), robots: { index: false } };
}

/** Where Click and Payme send the buyer back. The provider tells our API,
 *  not this page, whether the payment went through; the page waits for it. */
export default async function BillingReturnPage({ searchParams }: Props) {
  if (!isOnServer("billing", undefined)) notFound();
  const { order: raw } = await searchParams;
  const id = Number(raw);
  await requireUser(`/billing/return?order=${Number.isInteger(id) ? id : ""}`);
  if (!Number.isInteger(id) || id <= 0) notFound();
  let order: BillingOrder;
  try {
    order = await getWithSession<BillingOrder>(`/billing/orders/${id}/`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }
  const locale = await getLocale();
  return (
    <div className="mx-auto max-w-xl space-y-6">
      <h1 className="text-title-sm font-bold rw-strong">{t(locale, "billing.return.title")}</h1>
      <OrderStatus initial={order} />
    </div>
  );
}
