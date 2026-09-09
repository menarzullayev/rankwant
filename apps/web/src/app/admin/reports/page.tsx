import type { Metadata } from "next";

import { ReportsAdmin } from "@/components/admin/ReportsAdmin";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · Nuqson xabarlari" };

export default function AdminReportsPage() {
  return <ReportsAdmin />;
}
