"use client";

import { useState } from "react";

import {
  CrudPage,
  type ColumnDef,
  type FieldDef,
} from "@/components/admin/CrudPage";
import { Badge, type BadgeColor } from "@/components/ui/Badge";
import { ApiError } from "@/lib/api";
import { staff } from "@/lib/staff";

type PostKind = "news" | "announcement" | "editorial";

type Post = {
  slug: string;
  kind: PostKind;
  title: string;
  summary: string;
  body: string;
  locale: string;
  author: string | null;
  is_published: boolean;
  published_at: string | null;
  notify_users: boolean;
  notified_at: string | null;
  created_at: string;
  updated_at: string;
  [key: string]: unknown;
};

const PATH = "/staff/posts/";

const KIND: Record<PostKind, { label: string; color: BadgeColor }> = {
  news: { label: "Yangilik", color: "info" },
  announcement: { label: "E'lon", color: "warning" },
  editorial: { label: "Muharrir maqolasi", color: "brand" },
};

const FIELDS: FieldDef[] = [
  {
    name: "slug",
    label: "Slug",
    type: "slug",
    required: true,
    readonlyOnEdit: true,
  },
  {
    name: "kind",
    label: "Turi",
    type: "select",
    required: true,
    options: (Object.keys(KIND) as PostKind[]).map((k) => ({
      value: k,
      label: KIND[k].label,
    })),
  },
  { name: "title", label: "Sarlavha", type: "text", required: true },
  { name: "summary", label: "Qisqacha", type: "text", help: "300 belgigacha" },
  {
    name: "locale",
    label: "Til",
    type: "select",
    required: true,
    options: [
      { value: "uz", label: "uz" },
      { value: "ru", label: "ru" },
      { value: "en", label: "en" },
    ],
  },
  { name: "is_published", label: "Nashr qilingan", type: "checkbox" },
  {
    name: "published_at",
    label: "Nashr sanasi",
    type: "datetime",
    help: "Bo'sh qolsa — birinchi nashrda avtomatik qo'yiladi",
  },
  {
    name: "notify_users",
    label: "Foydalanuvchilarga xabar berish",
    type: "checkbox",
    help: "Nashrdan keyin barcha foydalanuvchiga bir marta bildirishnoma yuboriladi",
  },
  {
    name: "body",
    label: "Matn (Markdown)",
    type: "textarea",
    required: true,
    rows: 14,
  },
];

function fmtDate(iso: string | null): string {
  return iso
    ? new Date(iso).toLocaleString("uz-UZ", {
        dateStyle: "short",
        timeStyle: "short",
      })
    : "—";
}

/** Nashr holati tugmasi.
 *
 * Jadvalni ham qayta yuklaydi: aks holda faqat tugma yangilanib, qator
 * eski `is_published` bilan qolardi va keyingi «Tahrirlash» formasi shu
 * eski qiymatni yuborib nashrni jimgina qaytarib qo'yardi. */
function PublishToggle({ post, reload }: { post: Post; reload?: () => void }) {
  const [published, setPublished] = useState(post.is_published);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function toggle() {
    setBusy(true);
    setError("");
    try {
      const updated = await staff.action<Post>(
        `${PATH}${post.slug}/${published ? "unpublish" : "publish"}/`,
      );
      setPublished(updated.is_published);
      reload?.();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <button
      type="button"
      onClick={toggle}
      disabled={busy}
      title={error || (published ? "Nashrdan olish" : "Nashr qilish")}
      className="disabled:opacity-60"
    >
      <Badge color={error ? "error" : published ? "success" : "neutral"}>
        {error ? "Xato" : published ? "Nashrda" : "Qoralama"}
      </Badge>
    </button>
  );
}

const COLUMNS: ColumnDef<Post>[] = [
  { key: "slug", label: "Slug" },
  {
    key: "kind",
    label: "Turi",
    render: (p) => (
      <Badge color={KIND[p.kind]?.color}>{KIND[p.kind]?.label ?? p.kind}</Badge>
    ),
  },
  { key: "title", label: "Sarlavha" },
  { key: "locale", label: "Til" },
  {
    key: "is_published",
    label: "Holat",
    // key: holat formadan o'zgarsa tugma qayta o'rnatiladi
    render: (p, reload) => (
      <PublishToggle
        key={`${p.slug}-${p.is_published}`}
        post={p}
        reload={reload}
      />
    ),
  },
  {
    key: "published_at",
    label: "Nashr sanasi",
    render: (p) => fmtDate(p.published_at),
  },
  {
    key: "notify_users",
    label: "Xabar",
    render: (p) =>
      !p.notify_users ? (
        "—"
      ) : p.notified_at ? (
        <Badge color="success">Yuborildi</Badge>
      ) : (
        <Badge color="warning">Kutilmoqda</Badge>
      ),
  },
];

export function PostsAdmin() {
  return (
    <CrudPage<Post>
      title="Yangiliklar"
      path={PATH}
      idField="slug"
      columns={COLUMNS}
      fields={FIELDS}
      ordering="-created_at"
    />
  );
}
