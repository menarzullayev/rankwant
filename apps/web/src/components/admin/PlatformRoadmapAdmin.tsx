"use client";

import { useState } from "react";

import {
  CrudPage,
  type ColumnDef,
  type FieldDef,
} from "@/components/admin/CrudPage";
import { Badge, type BadgeColor } from "@/components/ui/Badge";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText } from "@/i18n/messages";
import { ApiError } from "@/lib/api";
import { staff } from "@/lib/staff";

/** Yo'l xaritasi boshqaruvi — `/admin/platform-roadmap`.
 *
 *  ⚠️ `status` FORMADA YO'Q, ataylab: u `set-status` amali orqali
 *  o'zgaradi, chunki o'sha amal o'tish vaqtini ham yozadi
 *  (`planned_at`/`started_at`/`released_at`). To'g'ridan-to'g'ri yozish
 *  batafsil sahifadagi "holat tarixi" ni bo'sh qoldirardi.
 *
 *  Jamoa taklifni shu yerdan `planned` ga o'tkazadi — bu tasdiqning o'zi
 *  (alohida "nashr qilish" amali yo'q).
 */

type RoadmapStatus =
  | "suggested"
  | "planned"
  | "in_progress"
  | "released"
  | "declined";

type RoadmapItem = {
  id: number;
  title: string;
  body: string;
  status: RoadmapStatus;
  target_quarter: string;
  update: number | null;
  planned_at: string | null;
  started_at: string | null;
  released_at: string | null;
  is_enabled: boolean;
  author: string | null;
  vote_count: number;
  comment_count: number;
  created_at: string;
  updated_at: string;
  [key: string]: unknown;
};

const PATH = "/staff/platform-roadmap/";

/** `apps/api/roadmap/models.py` `Status` bilan bir xil. */
const STATUS: Record<RoadmapStatus, { label: string; color: BadgeColor }> = {
  suggested: { label: "Ko'rib chiqilmoqda", color: "info" },
  planned: { label: "Rejalashtirilgan", color: "brand" },
  in_progress: { label: "Ishlanmoqda", color: "warning" },
  released: { label: "Chiqarildi", color: "success" },
  declined: { label: "Rad etilgan", color: "neutral" },
};

const FIELDS: FieldDef[] = [
  { name: "title", label: "Sarlavha", type: "text", required: true },
  {
    name: "target_quarter",
    label: "Muddat",
    type: "text",
    help: "Chorak darajasida (2026-Q4). ANIQ SANA YOZILMAYDI — bajarilmasa ishonch buziladi",
  },
  {
    name: "update",
    label: "Changelog yozuvi ID",
    type: "number",
    help: "Chiqarilganda bog'lanadigan yozuv raqami. Batafsil sahifada havola bo'ladi",
  },
  {
    name: "is_enabled",
    label: "Yoqilgan",
    type: "checkbox",
    help: "O'chirilsa band ko'rinmaydi, lekin ovozlari bilan bazada qoladi",
  },
  { name: "body", label: "Tavsif (Markdown)", type: "textarea", rows: 10 },
];

/** Holatni o'zgartirish — `set-status` amali orqali. */
function StatusSelect({
  row,
  reload,
}: {
  row: RoadmapItem;
  reload?: () => void;
}) {
  const locale = useLocale();
  const [status, setStatus] = useState<RoadmapStatus>(row.status);
  const [error, setError] = useState("");

  async function change(next: RoadmapStatus) {
    if (next === status) return;
    setError("");
    try {
      const updated = await staff.action<RoadmapItem>(`${PATH}${row.id}/set-status/`, {
        status: next,
      });
      setStatus(updated.status);
      reload?.();
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? errorText(locale, caught.code, caught.message)
          : String(caught),
      );
    }
  }

  if (error) {
    return (
      <span title={error}>
        <Badge color="error">Xato</Badge>
      </span>
    );
  }

  return (
    <select
      value={status}
      onChange={(event) => void change(event.target.value as RoadmapStatus)}
      className="rw-radius-sm border rw-line rw-field-bg px-2 py-1 text-theme-xs rw-strong"
    >
      {(Object.keys(STATUS) as RoadmapStatus[]).map((value) => (
        <option key={value} value={value}>
          {STATUS[value].label}
        </option>
      ))}
    </select>
  );
}

const COLUMNS: ColumnDef<RoadmapItem>[] = [
  { key: "title", label: "Sarlavha" },
  {
    key: "status",
    label: "Holat",
    render: (row, reload) => (
      <StatusSelect key={`${row.id}-${row.status}`} row={row} reload={reload} />
    ),
  },
  { key: "target_quarter", label: "Muddat" },
  { key: "vote_count", label: "Ovoz", align: "right" },
  { key: "comment_count", label: "Izoh", align: "right" },
  {
    key: "author",
    label: "Muallif",
    render: (row) => row.author ?? "—",
  },
  {
    key: "is_enabled",
    label: "Flag",
    render: (row) => (
      <Badge color={row.is_enabled ? "success" : "warning"}>
        {row.is_enabled ? "Yoqilgan" : "O'chirilgan"}
      </Badge>
    ),
  },
];

export function PlatformRoadmapAdmin() {
  return (
    <CrudPage<RoadmapItem>
      title="Yo'l xaritasi"
      path={PATH}
      idField="id"
      columns={COLUMNS}
      fields={FIELDS}
      searchable
      ordering="-created_at"
      // O'chirish RUXSAT ETILGAN, lekin u spam va haqorat uchun —
      // "kerak emas" degan taklif uchun emas. Ular `declined` bo'ladi va
      // ro'yxatda ko'rinib turadi: aks holda odam "yozdim, javob
      // bo'lmadi" degan taassurot bilan qoladi.
    />
  );
}
