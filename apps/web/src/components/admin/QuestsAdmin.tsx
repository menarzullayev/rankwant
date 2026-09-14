"use client";

import { useState } from "react";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, type MessageKey, errorText } from "@/i18n/messages";

import {
  CrudPage,
  type ColumnDef,
  type FieldDef,
} from "@/components/admin/CrudPage";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { ApiError } from "@/lib/api";
import { staff } from "@/lib/staff";

type Quest = {
  id: number;
  code: string;
  type: "daily" | "weekly" | "achievement";
  title_uz: string;
  title_ru: string;
  title_en: string;
  reward: number;
  is_active: boolean;
  completion_count: number;
  [key: string]: unknown;
};

const TYPE_LABEL: Record<Quest["type"], MessageKey> = {
  daily: "admin.label.misc.questDaily",
  weekly: "admin.label.misc.questWeekly",
  achievement: "admin.label.misc.questAchievement",
};

const columns: ColumnDef<Quest>[] = [
  {
    key: "code",
    labelKey: "admin.label.text.code",
    render: (q) => <span className="font-mono">{q.code}</span>,
  },
  {
    key: "type",
    labelKey: "admin.label.text.type",
    render: (q, _reload, locale) => (
      <Badge
        color={
          q.type === "achievement"
            ? "warning"
            : q.type === "weekly"
              ? "info"
              : "brand"
        }
      >
        {t(locale, TYPE_LABEL[q.type])}
      </Badge>
    ),
  },
  { key: "title_uz", labelKey: "admin.label.text.name" },
  {
    key: "reward",
    labelKey: "admin.label.text.reward",
    align: "right",
    render: (q) => `+${q.reward}`,
  },
  { key: "completion_count", labelKey: "admin.label.status.doneShort", align: "right" },
  {
    key: "is_active",
    labelKey: "admin.label.text.status",
    render: (q) => (
      <Badge color={q.is_active ? "success" : "neutral"}>
        {q.is_active ? "Faol" : "O'chiq"}
      </Badge>
    ),
  },
];

const fields: FieldDef[] = [
  {
    name: "code",
    labelKey: "admin.label.text.code",
    type: "slug",
    required: true,
    readonlyOnEdit: true,
    helpKey: "admin.help.questCodeMatch",
  },
  {
    name: "type",
    labelKey: "admin.label.text.type",
    type: "select",
    required: true,
    options: Object.entries(TYPE_LABEL).map(([value, labelKey]) => ({
      value,
      labelKey,
    })),
  },
  {
    name: "reward",
    labelKey: "admin.label.value.rewardQvant",
    type: "number",
    required: true,
    min: 0,
  },
  { name: "is_active", labelKey: "admin.label.flag.active", type: "checkbox" },
  { name: "title_uz", labelKey: "admin.label.name.uz", required: true },
  { name: "title_ru", labelKey: "admin.label.name.ru" },
  { name: "title_en", labelKey: "admin.label.name.en" },
];

/** ADR-0002 earn jadvalini qayta yozish — katalogdagi questlar asl holiga qaytadi. */
function SyncCatalogue() {
  const locale = useLocale();
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");

  async function sync() {
    if (
      !window.confirm(
        "Katalogdagi questlar (mukofot, nom, faollik) asl holiga qaytariladi. Davom etilsinmi?",
      )
    )
      return;
    setBusy(true);
    try {
      const res = await staff.action<{ synced: number }>("/staff/quests/sync/");
      setMsg(`${res.synced} ta quest tiklandi — sahifani yangilang`);
    } catch (e) {
      setMsg(
        e instanceof ApiError
          ? errorText(locale, e.code, e.message)
          : String(e),
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex items-center justify-end gap-3">
      {msg && <span className="text-theme-xs rw-dim">{msg}</span>}
      <Button variant="outline" className="h-9" disabled={busy} onClick={sync}>
        Katalogni tiklash
      </Button>
    </div>
  );
}

export function QuestsAdmin() {
  const locale = useLocale();
  return (
    <div className="space-y-4">
      <SyncCatalogue />
      <CrudPage<Quest>
        title="Questlar"
        path="/staff/quests/"
        idField="code"
        columns={columns}
        fields={fields}
        fromItem={(q) => ({ ...q })}
      />
    </div>
  );
}
