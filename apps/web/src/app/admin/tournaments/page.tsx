import type { Metadata } from "next";

import { Card } from "@/components/ui/Card";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · tournaments" };

// STUB — admin/tournaments bo'limi alohida agent tomonidan to'ldiriladi.
export default function AdminTournamentsPage() {
  return (
    <Card>
      <p className="text-theme-sm text-gray-400">tournaments — tez orada</p>
    </Card>
  );
}
