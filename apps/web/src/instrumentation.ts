/**
 * Next.js 16 dinamik sahifada `Cache-Control: private, no-store` yozadi
 * (`cookies()` layout'da). Proxy o'sha qiymatni qo'yadi, lekin render
 * oxirida Next kalitni qayta yozishi mumkin (`Vary` bilan o'lchandi).
 * Origin CDN'ga to'g'ri header yuborishi shart — shu hook javob
 * yozilishidan oldin qarorni qayta qo'llaydi.
 *
 * Qaror manbai — proxy qo'ygan `x-rw-home-cache` (Cookie `res.req` da
 * yo'qolishi mumkin). `node:http` faqat Node runtime'da yuklanadi.
 */

export async function register(): Promise<void> {
  if (process.env.NEXT_RUNTIME !== "nodejs") return;

  const { ServerResponse } = await import("node:http");
  const {
    HOME_CACHE_GUEST,
    HOME_CACHE_MARK_GUEST,
    HOME_CACHE_MARK_PRIVATE,
    HOME_CACHE_PRIVATE,
    HOME_CACHE_REQUEST_HEADER,
  } = await import("@/lib/home-cache");

  function headerGet(
    req: import("node:http").IncomingMessage,
    name: string,
  ): string | null {
    const value = req.headers[name.toLowerCase()];
    if (Array.isArray(value)) return value.join(",");
    return value ?? null;
  }

  function markOf(req: import("node:http").IncomingMessage): string | null {
    return headerGet(req, HOME_CACHE_REQUEST_HEADER);
  }

  const origSetHeader = ServerResponse.prototype.setHeader;
  const origWriteHead = ServerResponse.prototype.writeHead;

  function applyHomeCache(res: InstanceType<typeof ServerResponse>): void {
    const req = res.req;
    if (!req) return;
    const mark = markOf(req);
    if (mark === HOME_CACHE_MARK_GUEST) {
      origSetHeader.call(res, "Cache-Control", HOME_CACHE_GUEST);
      res.removeHeader("Set-Cookie");
      return;
    }
    if (mark === HOME_CACHE_MARK_PRIVATE) {
      origSetHeader.call(res, "Cache-Control", HOME_CACHE_PRIVATE);
    }
  }

  ServerResponse.prototype.setHeader = function (
    name: string,
    value: number | string | readonly string[],
  ) {
    const req = this.req;
    if (req && name.toLowerCase() === "cache-control") {
      const mark = markOf(req);
      if (mark === HOME_CACHE_MARK_GUEST) {
        return origSetHeader.call(this, name, HOME_CACHE_GUEST);
      }
      if (mark === HOME_CACHE_MARK_PRIVATE) {
        return origSetHeader.call(this, name, HOME_CACHE_PRIVATE);
      }
    }
    if (req && name.toLowerCase() === "set-cookie") {
      if (markOf(req) === HOME_CACHE_MARK_GUEST) return this;
    }
    return origSetHeader.call(this, name, value);
  };

  ServerResponse.prototype.writeHead = function (
    statusCode: number,
    ...rest: unknown[]
  ) {
    applyHomeCache(this);
    return (
      origWriteHead as (
        this: InstanceType<typeof ServerResponse>,
        code: number,
        ...args: unknown[]
      ) => InstanceType<typeof ServerResponse>
    ).call(this, statusCode, ...rest);
  };
}
