import type { Metadata } from "next";

import { QuestsAdmin } from "@/components/admin/QuestsAdmin";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · Questlar" };

export default function AdminQuestsPage() {
  return <QuestsAdmin />;
}
