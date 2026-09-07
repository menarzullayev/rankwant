import type { Metadata } from "next";

import { Card } from "@/components/ui/Card";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · users" };

// STUB — admin/users bo'limi alohida agent tomonidan to'ldiriladi.
export default function AdminUsersPage() {
  return (
    <Card>
      <p className="text-theme-sm text-gray-400">users — tez orada</p>
    </Card>
  );
}
