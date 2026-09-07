import type { Metadata } from "next";

import { Card } from "@/components/ui/Card";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · arena" };

// STUB — admin/arena bo'limi alohida agent tomonidan to'ldiriladi.
export default function AdminArenaPage() {
  return (
    <Card>
      <p className="text-theme-sm text-gray-400">arena — tez orada</p>
    </Card>
  );
}
