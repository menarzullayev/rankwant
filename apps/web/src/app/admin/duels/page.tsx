import type { Metadata } from "next";

import { DuelsAdmin } from "@/components/admin/DuelsAdmin";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · duels" };

export default function AdminDuelsPage() {
  return <DuelsAdmin />;
}
