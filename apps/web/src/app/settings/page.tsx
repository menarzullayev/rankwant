import type { Route } from "next";
import { redirect } from "next/navigation";

type Props = { searchParams: Promise<{ social?: string }> };

/** Sozlamalar bo'limlarga bo'lingan. Eski havola (`/settings?social=…` —
 *  provayderdan qaytish) ijtimoiy bo'limga olib boradi. */
export default async function SettingsPage({ searchParams }: Props) {
  const { social } = await searchParams;
  redirect(
    (social
      ? `/settings/ijtimoiy?social=${encodeURIComponent(social)}`
      : "/settings/profil") as Route,
  );
}
