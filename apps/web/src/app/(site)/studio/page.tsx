import { redirect } from "next/navigation";

import { requireUser } from "@/lib/access.server";

export const dynamic = "force-dynamic";

/** `/studio` has no page of its own yet: problems are its first section. */
export default async function StudioPage() {
  await requireUser("/studio/problems");
  redirect("/studio/problems");
}
