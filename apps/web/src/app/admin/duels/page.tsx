import type { Metadata } from "next";

import { Card } from "@/components/ui/Card";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · duels" };

// STUB — admin/duels bo'limi alohida agent tomonidan to'ldiriladi.
export default function AdminDuelsPage() {
  return (
    <Card>
      <p className="text-theme-sm text-gray-400">duels — tez orada</p>
    </Card>
  );
}
