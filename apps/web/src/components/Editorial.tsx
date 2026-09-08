"use client";

import { useState } from "react";

import { Markdown } from "@/components/Markdown";
import { Card } from "@/components/ui/Card";

/** Yechim tahlili yopiq turadi: masalani hali yechmagan foydalanuvchi
 * uni tasodifan ko'rib qo'ysa, mashq ma'nosini yo'qotadi. */
export function Editorial({ text }: { text: string }) {
  const [open, setOpen] = useState(false);

  return (
    <Card
      title="Yechim tahlili"
      action={
        <button
          type="button"
          onClick={() => setOpen((value) => !value)}
          className="rw-radius-sm px-2.5 py-1 text-theme-sm font-medium rw-accent-ink transition rw-hover-accent"
        >
          {open ? "Yashirish" : "Ko'rsatish"}
        </button>
      }
    >
      {open ? (
        <Markdown>{text}</Markdown>
      ) : (
        <p className="text-theme-sm rw-faint">
          Bu yerda tayyor yechim bor. O&apos;zingiz urinib ko&apos;rgach oching
          — aks holda mashqdan foyda qolmaydi.
        </p>
      )}
    </Card>
  );
}
