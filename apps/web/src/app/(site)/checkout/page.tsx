import { numericDate } from "@rankwant/shared/format";
import type { Metadata, Route } from "next";
import Link from "next/link";
import { notFound, redirect } from "next/navigation";

import {
  CheckoutForm,
  isPeriod,
  periodStart,
  type BillingOverview,
  type CheckoutItem,
  type PaidPlan,
} from "@/features/billing";
import { langQuery, type CourseDetail } from "@/features/courses";
import { getLocale } from "@/i18n/server";
import { fill, t } from "@/i18n/messages";
import { ApiError } from "@/lib/api";
import { requireUser } from "@/lib/access.server";
import { getWithSession } from "@/lib/api.server";
import { isOnServer } from "@/lib/flags";

export const dynamic = "force-dynamic";

type Props = { searchParams: Promise<Record<string, string | string[] | undefined>> };

const PERIOD_KEYS: Record<number, string> = { 1: "billing.period.month", 6: "billing.period.halfYear", 12: "billing.period.year" };
const PLAN_KEYS: Record<string, string> = { plus: "billing.plan.plus", pro: "billing.plan.pro", judge: "billing.plan.judge" };

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "billing.checkout.title"), robots: { index: false } };
}

function one(value: string | string[] | undefined): string {
  return Array.isArray(value) ? (value[0] ?? "") : (value ?? "");
}

export default async function CheckoutPage({ searchParams }: Props) {
  if (!isOnServer("billing", undefined)) notFound();
  const query = await searchParams;
  const plan = one(query.plan);
  const months = Number(one(query.months));
  const courseSlug = one(query.course);
  const back = courseSlug
    ? `/checkout?course=${encodeURIComponent(courseSlug)}`
    : `/checkout?plan=${encodeURIComponent(plan)}&months=${months}`;
  await requireUser(back);
  const locale = await getLocale();
  const lang = langQuery(locale);
  const overview = await getWithSession<BillingOverview>(`/billing/plans/${lang ? `?${lang}` : ""}`);

  let item: CheckoutItem;
  let title: string;
  let amount: number;
  let startsAt: string | undefined;
  if (courseSlug) {
    let course: CourseDetail;
    try {
      course = await getWithSession<CourseDetail>(
        `/courses/${encodeURIComponent(courseSlug)}/${lang ? `?${lang}` : ""}`,
      );
    } catch (error) {
      if (error instanceof ApiError && error.status === 404) notFound();
      throw error;
    }
    if (course.access !== "paid" || !course.price_uzs) notFound();
    // Already bought: nothing to pay for.
    if (course.enrollment?.source === "purchase") {
      redirect(`/courses/${encodeURIComponent(course.slug)}` as Route);
    }
    item = { kind: "course", course: course.slug };
    title = course.title;
    amount = course.price_uzs;
  } else {
    const offer = overview.plans.find((p) => p.code === plan);
    const price = offer?.is_on_sale && isPeriod(months) ? offer.prices.find((p) => p.months === months) : undefined;
    if (!offer || !price || !isPeriod(months)) notFound();
    item = { kind: "plan", plan: plan as PaidPlan, months };
    title = fill(t(locale, "billing.checkout.plan"), {
      plan: t(locale, PLAN_KEYS[plan] ?? "billing.plan.pro"),
      period: t(locale, PERIOD_KEYS[months] ?? "billing.period.month"),
    });
    amount = price.amount_uzs;
    const start = periodStart(overview, plan);
    if (start) startsAt = numericDate(start);
  }

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <header className="space-y-2">
        <Link href={"/plans" as Route} className="inline-flex min-h-11 items-center text-theme-sm rw-accent-ink hover:underline">
          {t(locale, "billing.checkout.back")}
        </Link>
        <h1 className="text-title-sm font-bold rw-strong">{t(locale, "billing.checkout.title")}</h1>
      </header>
      <CheckoutForm item={item} title={title} amount={amount} providers={overview.providers} startsAt={startsAt} />
    </div>
  );
}
