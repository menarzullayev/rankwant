"use client";

import { useState } from "react";

import {
  CrudPage,
  type ColumnDef,
  type FieldDef,
} from "@/components/admin/CrudPage";
import { Badge } from "@/components/ui/Badge";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText } from "@/i18n/messages";
import { ApiError } from "@/lib/api";
import { staff } from "@/lib/staff";

/** Changelog boshqaruvi — `/admin/updates`.
 *
 *  ⚠️ TARJIMALAR bu formada tahrirlanmaydi. Ular oqim bo'yicha AI dan
 *  keladi (qaror 16: AI qoralama → jamoa tahriri → AI tarjima ×10), ya'ni
 *  qo'lda yozish asosiy yo'l emas. Ustun qaysi tillar tayyor ekanini
 *  ko'rsatadi — bo'sh qolganini ko'rish uchun.
 *
 *  Forma `translations` yubormaydi, ya'ni serializer ularga TEGMAYDI
 *  (u faqat maydon berilganda sinxronlaydi) — mavjud tarjimalar saqlanadi.
 */

type UpdateKind =
  | "new"
  | "improved"
  | "fixed"
  | "performance"
  | "security"
  | "design"
  | "content"
  | "infrastructure"
  | "breaking"
  | "deprecated";

type UpdateModule =
  | "problems"
  | "contests"
  | "arena"
  | "judge"
  | "ratings"
  | "qvant"
  | "profile"
  | "classroom"
  | "quizzes"
  | "content"
  | "design"
  | "core";

type SystemUpdate = {
  id: number;
  kind: UpdateKind;
  module: UpdateModule;
  status: "draft" | "published" | "withdrawn";
  version: string;
  title: string;
  body: string;
  locale: string;
  image: string;
  source_repo: string;
  source_refs: string[];
  source_url: string;
  released_at: string;
  published_at: string | null;
  is_enabled: boolean;
  author: string | null;
  translations: { locale: string; is_machine: boolean }[];
  created_at: string;
  updated_at: string;
  [key: string]: unknown;
};

const PATH = "/staff/updates/";

/** `apps/api/updates/models.py` `Kind` bilan bir xil tartibda. */
const KIND: Record<UpdateKind, string> = {
  new: "Yangi",
  improved: "Yaxshilandi",
  fixed: "Tuzatildi",
  performance: "Tezlik",
  security: "Xavfsizlik",
  design: "Dizayn",
  content: "Kontent",
  infrastructure: "Infratuzilma",
  breaking: "Buzuvchi",
  deprecated: "Olib tashlanadi",
};

const MODULE: Record<UpdateModule, string> = {
  problems: "Masalalar",
  contests: "Musobaqalar",
  arena: "Bellashuvlar",
  judge: "Tekshiruv",
  ratings: "Reyting",
  qvant: "Qvant",
  profile: "Profil",
  classroom: "Sinf",
  quizzes: "Testlar",
  content: "Kontent",
  design: "Dizayn",
  core: "Umumiy",
};

const STATUS_LABEL: Record<SystemUpdate["status"], string> = {
  draft: "Qoralama",
  published: "Nashrda",
  withdrawn: "Nashrdan olingan",
};

const options = <T extends string>(table: Record<T, string>) =>
  (Object.keys(table) as T[]).map((value) => ({ value, label: table[value] }));

const FIELDS: FieldDef[] = [
  { name: "title", label: "Sarlavha", type: "text", required: true },
  {
    name: "kind",
    label: "Turi",
    type: "select",
    required: true,
    options: options(KIND),
  },
  {
    name: "module",
    label: "Modul",
    type: "select",
    required: true,
    options: options(MODULE),
  },
  {
    name: "status",
    label: "Holat",
    type: "select",
    required: true,
    options: options(STATUS_LABEL),
    help: "«Nashrda» qilib qo'yilsa `published_at` avtomatik yoziladi",
  },
  {
    name: "released_at",
    label: "Chiqarilgan sana",
    type: "datetime",
    required: true,
    help: "O'zgarishning HAQIQIY sanasi — yozuv kechroq yozilishi mumkin",
  },
  { name: "version", label: "Versiya", type: "text", help: "Ixtiyoriy, v1.4.0" },
  {
    name: "source_refs",
    label: "Manba havolalari",
    type: "list",
    help: "Commit SHA, PR raqami, release tegi — vergul bilan",
  },
  { name: "source_repo", label: "Repo", type: "text", help: "owner/repo" },
  { name: "source_url", label: "GitHub havolasi", type: "text" },
  {
    name: "image",
    label: "Rasm havolasi",
    type: "text",
    help: "Faqat kerak bo'lganda — dizayn o'zgarishlari uchun skrinshot",
  },
  { name: "is_enabled", label: "Yoqilgan", type: "checkbox" },
  { name: "body", label: "Matn (Markdown)", type: "textarea", rows: 12 },
];

/** Nashr / nashrdan olish — bitta tugma, jadvalni yangilaydi.
 *
 *  `reload` SHART: usiz qator eski `status` bilan qolardi va keyingi
 *  tahrir shu eski qiymatni yuborib, nashrni jimgina qaytarib qo'yardi. */
function PublishToggle({
  row,
  reload,
}: {
  row: SystemUpdate;
  reload?: () => void;
}) {
  const locale = useLocale();
  const [status, setStatus] = useState(row.status);
  const [error, setError] = useState("");

  async function toggle() {
    setError("");
    try {
      const updated = await staff.action<SystemUpdate>(
        `${PATH}${row.id}/${status === "published" ? "withdraw" : "publish"}/`,
      );
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

  const color = error
    ? "error"
    : status === "published"
      ? "success"
      : status === "withdrawn"
        ? "warning"
        : "neutral";

  return (
    <button
      type="button"
      onClick={toggle}
      title={error || (status === "published" ? "Nashrdan olish" : "Nashr qilish")}
    >
      <Badge color={color}>{error ? "Xato" : STATUS_LABEL[status]}</Badge>
    </button>
  );
}

/** Feature flag — modul darajasidagi rollback (qaror 17). */
function EnabledToggle({
  row,
  reload,
}: {
  row: SystemUpdate;
  reload?: () => void;
}) {
  const locale = useLocale();
  const [enabled, setEnabled] = useState(row.is_enabled);
  const [error, setError] = useState("");

  async function toggle() {
    setError("");
    try {
      const updated = await staff.action<SystemUpdate>(
        `${PATH}${row.id}/${enabled ? "disable" : "enable"}/`,
      );
      setEnabled(updated.is_enabled);
      reload?.();
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? errorText(locale, caught.code, caught.message)
          : String(caught),
      );
    }
  }

  return (
    <button
      type="button"
      onClick={toggle}
      title={error || (enabled ? "O'chirish (rollback)" : "Yoqish")}
    >
      <Badge color={error ? "error" : enabled ? "success" : "warning"}>
        {error ? "Xato" : enabled ? "Yoqilgan" : "O'chirilgan"}
      </Badge>
    </button>
  );
}

const COLUMNS: ColumnDef<SystemUpdate>[] = [
  { key: "title", label: "Sarlavha" },
  {
    key: "kind",
    label: "Turi",
    render: (row) => (
      <Badge color={row.kind === "breaking" || row.kind === "deprecated" ? "error" : "info"}>
        {KIND[row.kind] ?? row.kind}
      </Badge>
    ),
  },
  {
    key: "module",
    label: "Modul",
    render: (row) => MODULE[row.module] ?? row.module,
  },
  {
    key: "status",
    label: "Holat",
    render: (row, reload) => (
      <PublishToggle key={`${row.id}-${row.status}`} row={row} reload={reload} />
    ),
  },
  {
    key: "is_enabled",
    label: "Flag",
    render: (row, reload) => (
      <EnabledToggle key={`${row.id}-${row.is_enabled}`} row={row} reload={reload} />
    ),
  },
  { key: "released_at", label: "Sana" },
  {
    key: "translations",
    label: "Tarjima",
    render: (row) => (
      <span title={row.translations.map((tr) => tr.locale).join(", ")}>
        {row.translations.length}/10
      </span>
    ),
  },
];

export function UpdatesAdmin() {
  return (
    <CrudPage<SystemUpdate>
      title="O'zgarishlar"
      path={PATH}
      idField="id"
      columns={COLUMNS}
      fields={FIELDS}
      searchable
      ordering="-released_at"
    />
  );
}
