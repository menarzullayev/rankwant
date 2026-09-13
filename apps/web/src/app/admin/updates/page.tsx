import type { Metadata } from "next";

import { UpdatesAdmin } from "@/components/admin/UpdatesAdmin";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · O'zgarishlar" };

export default function AdminUpdatesPage() {
  return <UpdatesAdmin />;
}
