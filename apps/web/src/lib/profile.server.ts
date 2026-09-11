import "server-only";

import { cache } from "react";

import { api, type PublicProfile } from "./api";
import { getWithSession } from "./api.server";

/** Layout va tab sahifasi bir so'rovda bir xil ma'lumotni so'raydi —
 *  `cache` uni bitta chaqiruvga birlashtiradi. */
export const loadUser = cache((username: string) => api.user(username));

export const loadProfile = cache((username: string) =>
  getWithSession<PublicProfile>(`/users/${username}/profile/`),
);
