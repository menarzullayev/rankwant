import type { Period } from "./api/billing";

/** Dictionary keys for plan and period names, shared by every billing page. */
export const PERIOD_KEYS: Record<Period, string> = {
  1: "billing.period.month",
  6: "billing.period.halfYear",
  12: "billing.period.year",
};

export const PLAN_KEYS: Record<string, string> = {
  free: "billing.plan.free",
  plus: "billing.plan.plus",
  pro: "billing.plan.pro",
  judge: "billing.plan.judge",
};
