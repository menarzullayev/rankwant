import type { Metadata } from "next";

import { PlatformRoadmapAdmin } from "@/components/admin/PlatformRoadmapAdmin";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · Yo'l xaritasi" };

export default function AdminPlatformRoadmapPage() {
  return <PlatformRoadmapAdmin />;
}
