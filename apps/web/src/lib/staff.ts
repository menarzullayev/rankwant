/** Staff (admin UI) mijozi — sessiya + CSRF bilan, brauzerda. */

import { API_BASE, ApiError, type Paginated } from "@/lib/api";

function csrf(): Record<string, string> {
  const m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
  return m ? { "X-CSRFToken": decodeURIComponent(m[1]) } : {};
}

export async function staffFetch<T>(
  method: "GET" | "POST" | "PATCH" | "PUT" | "DELETE",
  path: string,
  body?: unknown,
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    credentials: "include",
    headers: {
      Accept: "application/json",
      ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
      ...csrf(),
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
    cache: "no-store",
  });
  const raw = await res.text();
  const parsed = raw ? JSON.parse(raw) : null;
  if (!res.ok) {
    // Maydon xatolari `details` da keladi, `message` esa umumiy
    // («Kiritilgan ma'lumot noto'g'ri»). Umumiysi birinchi bo'lsa
    // xodim aynan qaysi maydon xato ekanini ko'rmasdi.
    const details = parsed?.error?.details ?? {};
    const fields =
      details && typeof details === "object"
        ? Object.entries(details)
            .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : String(v)}`)
            .slice(0, 3)
            .join(" · ")
        : "";
    throw new ApiError(
      res.status,
      parsed?.error?.code ?? "error",
      fields || parsed?.error?.message || res.statusText,
    );
  }
  return parsed as T;
}

export const staff = {
  list: <T>(path: string, params: Record<string, string | number> = {}) => {
    const q = new URLSearchParams(
      Object.fromEntries(Object.entries(params).map(([k, v]) => [k, String(v)])),
    ).toString();
    return staffFetch<Paginated<T>>("GET", `${path}${q ? `?${q}` : ""}`);
  },
  get: <T>(path: string) => staffFetch<T>("GET", path),
  create: <T>(path: string, body: unknown) => staffFetch<T>("POST", path, body),
  update: <T>(path: string, body: unknown) => staffFetch<T>("PATCH", path, body),
  remove: (path: string) => staffFetch<void>("DELETE", path),
  action: <T>(path: string, body: unknown = {}) => staffFetch<T>("POST", path, body),
};
