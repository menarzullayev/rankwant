import type { Metadata } from "next";

import { Card } from "@/components/ui/Card";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · quests" };

// STUB — admin/quests bo'limi alohida agent tomonidan to'ldiriladi.
export default function AdminQuestsPage() {
  return (
    <Card>
      <p className="text-theme-sm text-gray-400">quests — tez orada</p>
    </Card>
  );
}
