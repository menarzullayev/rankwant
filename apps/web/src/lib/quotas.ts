/** Plan quotas (ADR-0061 § 2): how much the signed-in user may own.
 *
 *  The limit comes from `/me/quotas/` — the admin can change it, so a page
 *  never keeps its own copy of the number. Each kind counts everything
 *  owned, published or not.
 */

export type QuotaKey =
  | "problems"
  | "contests"
  | "quizzes"
  | "classrooms"
  | "class_members"
  | "storage_mb";

/** `limit: null` — no limit (staff). */
export type Quota = { key: QuotaKey; limit: number | null; used: number };
export type Quotas = { plan: string; quotas: Quota[] };

/** One kind's row; a kind the server did not report is not limited here —
 *  the server still refuses past the plan. */
export function quotaOf(all: Quotas | null, key: QuotaKey): Quota {
  return all?.quotas.find((row) => row.key === key) ?? { key, limit: null, used: 0 };
}

export function quotaFull(quota: Quota): boolean {
  return quota.limit !== null && quota.used >= quota.limit;
}
