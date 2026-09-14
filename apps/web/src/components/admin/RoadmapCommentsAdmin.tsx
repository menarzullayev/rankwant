"use client";

import { useState } from "react";

import {
  CrudPage,
  type ColumnDef,
} from "@/components/admin/CrudPage";
import { Badge } from "@/components/ui/Badge";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText } from "@/i18n/messages";
import { ApiError } from "@/lib/api";
import { staff } from "@/lib/staff";

/** Izohlar moderatsiyasi — `/admin/roadmap-comments`.
 *
 *  Moderatsiya KEYIN (post-moderation): izoh darhol ko'rinadi, xodim
 *  kerak bo'lsa yashiradi. Shuning uchun bu sahifada "tasdiqlash"
 *  tugmasi yo'q — faqat "Yashirish" / "Qaytarish".
 *
 *  Yashirish — O'CHIRISH EMAS: izoh bazada qoladi va keyin qarorni
 *  qayta ko'rib chiqish mumkin. O'chirish faqat spam uchun.
 */

type RoadmapComment = {
  id: number;
  item: number;
  item_title: string;
  author: string | null;
  body: string;
  is_hidden: boolean;
  created_at: string;
  [key: string]: unknown;
};

const PATH = "/staff/platform-roadmap-comments/";

function HiddenToggle({
  row,
  reload,
}: {
  row: RoadmapComment;
  reload?: () => void;
}) {
  const locale = useLocale();
  const [hidden, setHidden] = useState(row.is_hidden);
  const [error, setError] = useState("");

  async function toggle() {
    setError("");
    try {
      const updated = await staff.action<RoadmapComment>(
        `${PATH}${row.id}/${hidden ? "unhide" : "hide"}/`,
      );
      setHidden(updated.is_hidden);
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
      title={error || (hidden ? "Qaytarish" : "Yashirish")}
    >
      <Badge color={error ? "error" : hidden ? "warning" : "success"}>
        {error ? "Xato" : hidden ? "Yashirilgan" : "Ko'rinadi"}
      </Badge>
    </button>
  );
}

const COLUMNS: ColumnDef<RoadmapComment>[] = [
  { key: "item_title", labelKey: "admin.label.status.busy" },
  {
    key: "author",
    labelKey: "admin.label.text.author",
    render: (row) => row.author ?? "—",
  },
  {
    key: "body",
    labelKey: "admin.label.text.comment",
    render: (row) => (
      <span className="line-clamp-2 max-w-md" title={row.body}>
        {row.body}
      </span>
    ),
  },
  {
    key: "is_hidden",
    labelKey: "admin.label.text.status",
    render: (row, reload) => (
      <HiddenToggle key={`${row.id}-${row.is_hidden}`} row={row} reload={reload} />
    ),
  },
  {
    key: "created_at",
    labelKey: "admin.label.text.date",
    render: (row) => new Date(row.created_at).toLocaleDateString("uz-UZ"),
  },
];

export function RoadmapCommentsAdmin() {
  return (
    <CrudPage<RoadmapComment>
      title="Yo'l xaritasi izohlari"
      path={PATH}
      idField="id"
      columns={COLUMNS}
      fields={[]}
      searchable
      ordering="-created_at"
      // Izoh FAQAT foydalanuvchi tomonidan tug'iladi: xodim uni
      // tahrirlamaydi (bu boshqa odamning so'zi) — faqat yashiradi.
      canCreate={false}
      readOnly
    />
  );
}
