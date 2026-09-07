"use client";

import {
  CrudPage,
  type ColumnDef,
  type FieldDef,
} from "@/components/admin/CrudPage";
import { Badge } from "@/components/ui/Badge";

type ShopItem = {
  id: number;
  code: string;
  category:
    "streak_freeze" | "avatar_frame" | "profile_cover" | "username_badge";
  title_uz: string;
  title_ru: string;
  title_en: string;
  price: number;
  asset_ref: string;
  is_active: boolean;
  is_consumable: boolean;
  owner_count: number;
  [key: string]: unknown;
};

const CATEGORY_LABEL: Record<ShopItem["category"], string> = {
  streak_freeze: "Streak freeze",
  avatar_frame: "Avatar ramka",
  profile_cover: "Profil cover",
  username_badge: "Username badge",
};

const columns: ColumnDef<ShopItem>[] = [
  {
    key: "code",
    label: "Kod",
    render: (i) => <span className="font-mono">{i.code}</span>,
  },
  {
    key: "category",
    label: "Kategoriya",
    render: (i) => CATEGORY_LABEL[i.category],
  },
  { key: "title_uz", label: "Nomi" },
  {
    key: "price",
    label: "Narx",
    align: "right",
    render: (i) => `${i.price} Qvant`,
  },
  {
    key: "is_consumable",
    label: "Takroriy",
    render: (i) => (i.is_consumable ? <Badge color="info">Ha</Badge> : "—"),
  },
  { key: "owner_count", label: "Egalari", align: "right" },
  {
    key: "is_active",
    label: "Holat",
    render: (i) => (
      <Badge color={i.is_active ? "success" : "neutral"}>
        {i.is_active ? "Faol" : "O'chiq"}
      </Badge>
    ),
  },
];

const fields: FieldDef[] = [
  {
    name: "code",
    label: "Kod",
    type: "slug",
    required: true,
    readonlyOnEdit: true,
  },
  {
    name: "category",
    label: "Kategoriya",
    type: "select",
    required: true,
    options: Object.entries(CATEGORY_LABEL).map(([value, label]) => ({
      value,
      label,
    })),
    help: "ADR-0002: v1 da faqat kosmetika va qulaylik",
  },
  {
    name: "price",
    label: "Narx (Qvant)",
    type: "number",
    required: true,
    min: 0,
  },
  {
    name: "asset_ref",
    label: "Asset",
    help: "Ramka/cover fayliga havola yoki kalit",
  },
  { name: "is_active", label: "Faol", type: "checkbox" },
  {
    name: "is_consumable",
    label: "Takroriy sotib olinadi",
    type: "checkbox",
    help: "Streak freeze — ha, ramka — yo'q",
  },
  { name: "title_uz", label: "Nomi (uz)", required: true },
  { name: "title_ru", label: "Nomi (ru)" },
  { name: "title_en", label: "Nomi (en)" },
];

export function ShopAdmin() {
  return (
    <CrudPage<ShopItem>
      title="Do'kon"
      path="/staff/shop-items/"
      idField="code"
      columns={columns}
      fields={fields}
      fromItem={(i) => ({ ...i })}
    />
  );
}
