"use client";

import Link from "next/link";

import {
  CrudPage,
  type ColumnDef,
  type FieldDef,
} from "@/components/admin/CrudPage";
import { Badge } from "@/components/ui/Badge";
import { date } from "@/i18n/messages";

type Report = {
  id: number;
  problem: string;
  username: string;
  reason: string;
  comment: string;
  status: "open" | "accepted" | "rejected";
  created_at: string;
  [key: string]: unknown;
};

const REASON_LABEL: Record<string, string> = {
  statement: "Matnda xato",
  tests: "Testlar noto'g'ri",
  translation: "Tarjima xato",
  duplicate: "Takroriy masala",
  other: "Boshqa",
};

const STATUS_LABEL: Record<Report["status"], string> = {
  open: "Ochiq",
  accepted: "Qabul qilindi",
  rejected: "Rad etildi",
};

const columns: ColumnDef<Report>[] = [
  {
    key: "problem",
    label: "Masala",
    render: (r) => (
      <Link
        href={`/problems/${r.problem}`}
        className="font-mono text-theme-xs rw-accent-ink hover:underline"
      >
        {r.problem}
      </Link>
    ),
  },
  {
    key: "reason",
    label: "Sabab",
    render: (r) => <Badge>{REASON_LABEL[r.reason] ?? r.reason}</Badge>,
  },
  {
    key: "comment",
    label: "Izoh",
    // Izoh uzun bo'lishi mumkin — ro'yxatda kesiladi, to'lig'i hoverda.
    render: (r) =>
      r.comment ? (
        <span title={r.comment} className="line-clamp-2 rw-dim">
          {r.comment}
        </span>
      ) : (
        <span className="rw-faint">—</span>
      ),
  },
  { key: "username", label: "Kim" },
  {
    key: "status",
    label: "Holat",
    render: (r) => (
      <Badge
        color={
          r.status === "open"
            ? "warning"
            : r.status === "accepted"
              ? "success"
              : "neutral"
        }
      >
        {STATUS_LABEL[r.status]}
      </Badge>
    ),
  },
  {
    key: "created_at",
    label: "Sana",
    align: "right",
    render: (r, _reload, locale) => (
      <span className="rw-faint tabular-nums">
        {date(r.created_at, locale)}
      </span>
    ),
  },
];

/** Faqat holat tahrirlanadi: sabab va izoh — xabar beruvchining so'zi,
 *  uni o'zgartirish yozuvni ma'nosiz qilardi (backend ham rad etadi). */
const fields: FieldDef[] = [
  {
    name: "status",
    label: "Holat",
    type: "select",
    required: true,
    options: (["open", "accepted", "rejected"] as const).map((value) => ({
      value,
      label: STATUS_LABEL[value],
    })),
  },
];

export function ReportsAdmin() {
  return (
    <CrudPage<Report>
      title="Nuqson xabarlari"
      path="/staff/problem-reports/"
      columns={columns}
      fields={fields}
      canCreate={false}
      fromItem={(r) => ({ status: r.status })}
    />
  );
}
