/** Brauzer API manzili — preview stack uchun loopback override.
 *
 * `docker-compose.public.yml` web obrazini `${PUBLIC_ORIGIN}/api/v1` bilan
 * quradi (tunnel same-origin). Brauzer esa ko'pincha `http://127.0.0.1:8300`
 * dan ochiladi — shunda baked URL production API ga ketadi va lokal login
 * ishlamaydi. Loopback preview portida lokal `:8301` ga yo'naltiramiz
 * (`8300` docker web, `8310`/`8312` host `next dev`).
 *
 * SSE (`/api/v1/events/`) prod'da tunnel orqali same-origin; split-stack
 * dev'da alohida `realtime` `:8302` — `resolveBrowserRealtimeBase`.
 */
export const LOOPBACK_PREVIEW_PORTS = ["8300", "8310", "8312"] as const;

export function isLoopbackPreviewPage(
  page: Pick<Location, "hostname" | "port">,
): boolean {
  return (
    (page.hostname === "127.0.0.1" || page.hostname === "localhost") &&
    (LOOPBACK_PREVIEW_PORTS as readonly string[]).includes(page.port)
  );
}

export function resolveBrowserApiBase(
  baked: string | undefined,
  page: Pick<Location, "hostname" | "port" | "protocol" | "origin" | "href">,
): string {
  const fallback = baked ?? "http://localhost:8000/api/v1";
  if (!isLoopbackPreviewPage(page)) return fallback;
  try {
    const bakedOrigin = new URL(fallback, page.href ?? page.origin).origin;
    if (bakedOrigin === page.origin) return fallback;
  } catch {
    return fallback;
  }
  const host = page.hostname === "localhost" ? "127.0.0.1" : page.hostname;
  return `${page.protocol}//${host}:8301/api/v1`;
}

/** Loopback host `next dev`: SSE same-origin proxy (next.config rewrites → :8302). */
export function resolveBrowserRealtimeBase(
  baked: string | undefined,
  page: Pick<Location, "hostname" | "port" | "protocol" | "origin" | "href">,
): string {
  if (!isLoopbackPreviewPage(page)) {
    return resolveBrowserApiBase(baked, page);
  }
  if (page.port === "8310" || page.port === "8312") {
    return `${page.origin}/api/v1`;
  }
  const host = page.hostname === "localhost" ? "127.0.0.1" : page.hostname;
  return `${page.protocol}//${host}:8302/api/v1`;
}

export function publicApiBase(): string {
  return process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000/api/v1";
}

export function serverApiBase(): string {
  return process.env.API_BASE_INTERNAL || publicApiBase();
}
