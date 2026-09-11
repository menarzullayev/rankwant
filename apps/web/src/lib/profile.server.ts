import "server-only";

import type { Metadata } from "next";
import { cache } from "react";

import { t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";

import { api, type PublicProfile } from "./api";
import { getWithSession } from "./api.server";

/** Layout va tab sahifasi bir so'rovda bir xil ma'lumotni so'raydi —
 *  `cache` uni bitta chaqiruvga birlashtiradi. */
export const loadUser = cache((username: string) => api.user(username));

export const loadProfile = cache((username: string) =>
  getWithSession<PublicProfile>(`/users/${username}/profile/`),
);

/** Tab sarlavhasi egasining ismi bilan — «Urinishlar — Ali Valiyev»:
 *  bir nechta profil ochiq bo'lsa, brauzer tablari farqlanadi. */
export async function tabMetadata(
  params: Promise<{ username: string }>,
  key: string,
): Promise<Metadata> {
  const username = decodeURIComponent((await params).username);
  const [locale, user] = await Promise.all([getLocale(), loadUser(username).catch(() => null)]);
  return { title: user ? `${t(locale, key)} — ${user.display_name || user.username}` : "404" };
}
