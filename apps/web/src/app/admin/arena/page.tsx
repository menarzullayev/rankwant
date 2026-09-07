import type { Metadata } from "next";

import { ArenaAdmin } from "@/components/admin/ArenaAdmin";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · arena" };

export default function AdminArenaPage() {
  return <ArenaAdmin />;
}
