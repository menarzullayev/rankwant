import { postJson } from "@/lib/api/client";
import type { components } from "@/lib/api/generated/schema";

type Schemas = components["schemas"];

export type BillingOverview = Schemas["BillingOverview"];
export type PlanOffer = Schemas["PlanOffer"];
export type BillingOrder = Schemas["Order"];
export type PaidPlan = Schemas["PlanCodeEnum"];
export type PaymentProvider = Schemas["PaymentProviderEnum"];

/** Periods sold (ADR-0057): one prepaid payment each, no renewal. */
export const PERIODS = [1, 6, 12] as const;
export type Period = (typeof PERIODS)[number];

export const isPeriod = (value: unknown): value is Period => PERIODS.includes(Number(value) as Period);

/** Higher includes everything below it (`billing.models.RANK`). */
export const PLAN_RANK: Record<string, number> = { free: 0, plus: 1, pro: 2, judge: 3 };

/** Plans that open every paid course (owner decision 2026-11-10). */
export const PLANS_WITH_COURSES: readonly string[] = ["pro", "judge"];

type OrderInput =
  | { kind: "plan"; plan: PaidPlan; months: Period; provider: PaymentProvider }
  | { kind: "course"; course: string; provider: PaymentProvider };

export const createOrder = (body: OrderInput) => postJson<BillingOrder>("/billing/orders/", body);

/** When a new period of `plan` would begin: after any period of the same
 *  or a higher plan still to run (`billing.services.period_start`). */
export function periodStart(overview: BillingOverview, plan: string, now = Date.now()): Date | null {
  const rank = PLAN_RANK[plan] ?? 0;
  const ends = overview.periods
    .filter((p) => (PLAN_RANK[p.plan] ?? 0) >= rank)
    .map((p) => new Date(p.ends_at).getTime())
    .filter((end) => end > now);
  return ends.length ? new Date(Math.max(...ends)) : null;
}
