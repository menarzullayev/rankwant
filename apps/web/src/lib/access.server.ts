import "server-only";

import type { Route } from "next";
import { notFound, redirect } from "next/navigation";

import type { Me } from "@/lib/api";
import { getSessionUser } from "@/lib/api.server";

import { loginHref } from "./access";

/** The server half of the access list (`lib/access.ts`, ADR-0054).
 *
 *  `proxy.ts` already turns away a request that carries no session cookie
 *  at all; these two answer the case it cannot see — a cookie that is
 *  there but no longer valid, or valid but not staff. Both end the render:
 *  nothing of the page is sent.
 */

/** The signed-in user, or a redirect to sign in and come back to `next`. */
export async function requireUser<T extends Me = Me>(next: string): Promise<T> {
  const me = await getSessionUser<T>();
  if (!me) redirect(loginHref(next) as Route);
  return me;
}

/** A staff member; a guest signs in, anybody else gets "not found". */
export async function requireStaff(next: string): Promise<Me> {
  const me = await requireUser(next);
  if (!me.is_staff) notFound();
  return me;
}
