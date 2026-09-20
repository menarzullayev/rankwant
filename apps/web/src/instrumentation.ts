/**
 * Next.js 16 dinamik sahifada `Cache-Control: private, no-store` yozadi
 * (`cookies()` layout'da). Proxy o'sha qiymatni qo'yadi, lekin render
 * oxirida Next kalitni qayta yozishi mumkin (`Vary` bilan o'lchandi).
 * Origin CDN'ga to'g'ri header yuborishi shart — shu hook javob
 * yozilishidan oldin qarorni qayta qo'llaydi.
 *
 * Qaror manbai — proxy qo'ygan `x-rw-home-cache` (Cookie `res.req` da
 * yo'qolishi mumkin). `node:http` faqat Node runtime'da yuklanadi.
 *
 * `guest-al` (`/problems`): origin `Vary` ga `Accept-Language` qo'shiladi.
 * CF Free `Vary` ni o'zi kalitlamaydi — Cache Rule `vary.normalize` ham
 * origin header'ni ko'rishi shart. Transform Rule brauzerga kech qo'shadi.
 */

export async function register(): Promise<void> {
  if (process.env.NEXT_RUNTIME !== "nodejs") return;

  const { ServerResponse } = await import("node:http");
  const {
    HOME_CACHE_GUEST,
    HOME_CACHE_MARK_GUEST,
    HOME_CACHE_MARK_GUEST_LOCALE,
    HOME_CACHE_MARK_PRIVATE,
    HOME_CACHE_PRIVATE,
    HOME_CACHE_REQUEST_HEADER,
  } = await import("@/lib/home-cache");

  const guestMarks = new Set<string>([
    HOME_CACHE_MARK_GUEST,
    HOME_CACHE_MARK_GUEST_LOCALE,
  ]);

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

  function withAcceptLanguage(
    value: number | string | readonly string[] | undefined,
  ): string {
    const raw =
      value === undefined
        ? ""
        : Array.isArray(value)
          ? value.join(",")
          : String(value);
    const parts = raw
      .split(",")
      .map((part) => part.trim())
      .filter(Boolean);
    if (!parts.some((part) => part.toLowerCase() === "accept-language")) {
      parts.push("Accept-Language");
    }
    return parts.join(", ");
  }

  const origSetHeader = ServerResponse.prototype.setHeader;
  const origWriteHead = ServerResponse.prototype.writeHead;

  function applyHomeCache(res: InstanceType<typeof ServerResponse>): void {
    const req = res.req;
    if (!req) return;
    const mark = markOf(req);
    if (mark && guestMarks.has(mark)) {
      origSetHeader.call(res, "Cache-Control", HOME_CACHE_GUEST);
      res.removeHeader("Set-Cookie");
      if (mark === HOME_CACHE_MARK_GUEST_LOCALE) {
        origSetHeader.call(
          res,
          "Vary",
          withAcceptLanguage(res.getHeader("Vary")),
        );
      }
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
    const mark = req ? markOf(req) : null;
    if (req && name.toLowerCase() === "cache-control") {
      if (mark && guestMarks.has(mark)) {
        return origSetHeader.call(this, name, HOME_CACHE_GUEST);
      }
      if (mark === HOME_CACHE_MARK_PRIVATE) {
        return origSetHeader.call(this, name, HOME_CACHE_PRIVATE);
      }
    }
    if (req && name.toLowerCase() === "set-cookie") {
      if (mark && guestMarks.has(mark)) return this;
    }
    if (req && name.toLowerCase() === "vary") {
      if (mark === HOME_CACHE_MARK_GUEST_LOCALE) {
        return origSetHeader.call(this, name, withAcceptLanguage(value));
      }
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
