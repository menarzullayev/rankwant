import type { Metadata } from "next";

import { Card } from "@/components/ui/Card";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · hackathons" };

// STUB — admin/hackathons bo'limi alohida agent tomonidan to'ldiriladi.
export default function AdminHackathonsPage() {
  return (
    <Card>
      <p className="text-theme-sm text-gray-400">hackathons — tez orada</p>
    </Card>
  );
}
