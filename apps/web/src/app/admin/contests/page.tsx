import type { Metadata } from "next";

import { Card } from "@/components/ui/Card";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · contests" };

// STUB — admin/contests bo'limi alohida agent tomonidan to'ldiriladi.
export default function AdminContestsPage() {
  return (
    <Card>
      <p className="text-theme-sm text-gray-400">contests — tez orada</p>
    </Card>
  );
}
