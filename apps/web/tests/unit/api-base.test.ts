import { describe, expect, it } from "vitest";

import { resolveBrowserApiBase, resolveBrowserRealtimeBase } from "@/lib/api-base";

const page = (hostname: string, port: string, protocol = "http:") =>
  ({
    hostname,
    port,
    protocol,
    origin: `${protocol}//${hostname}${port ? `:${port}` : ""}`,
    href: `${protocol}//${hostname}${port ? `:${port}` : ""}/login`,
  }) as Location;

describe("resolveBrowserApiBase", () => {
  it("keeps production URL when not on loopback preview port", () => {
    expect(
      resolveBrowserApiBase(
        "https://rankwant.uz/api/v1",
        page("rankwant.uz", ""),
      ),
    ).toBe("https://rankwant.uz/api/v1");
  });

  it("redirects loopback preview to local API", () => {
    expect(
      resolveBrowserApiBase(
        "https://rankwant.uz/api/v1",
        page("127.0.0.1", "8300"),
      ),
    ).toBe("http://127.0.0.1:8301/api/v1");
  });

  it("redirects local next dev port to API :8301", () => {
    expect(
      resolveBrowserApiBase(
        "https://rankwant.uz/api/v1",
        page("127.0.0.1", "8310"),
      ),
    ).toBe("http://127.0.0.1:8301/api/v1");
  });

  it("redirects RANKWANT_DEV_WEB_PORT (8312) to API :8301", () => {
    expect(
      resolveBrowserApiBase(
        "https://rankwant.uz/api/v1",
        page("127.0.0.1", "8312"),
      ),
    ).toBe("http://127.0.0.1:8301/api/v1");
  });

  it("does not override when baked origin matches page", () => {
    expect(
      resolveBrowserApiBase(
        "http://127.0.0.1:8300/api/v1",
        page("127.0.0.1", "8300"),
      ),
    ).toBe("http://127.0.0.1:8300/api/v1");
  });
});

describe("resolveBrowserRealtimeBase", () => {
  it("routes SSE to same-origin proxy on host next dev", () => {
    expect(
      resolveBrowserRealtimeBase(
        "https://rankwant.uz/api/v1",
        page("127.0.0.1", "8312"),
      ),
    ).toBe("http://127.0.0.1:8312/api/v1");
  });

  it("routes SSE to realtime :8302 on docker web loopback", () => {
    expect(
      resolveBrowserRealtimeBase(
        "https://rankwant.uz/api/v1",
        page("127.0.0.1", "8300"),
      ),
    ).toBe("http://127.0.0.1:8302/api/v1");
  });

  it("keeps production realtime on same base as API", () => {
    expect(
      resolveBrowserRealtimeBase(
        "https://rankwant.uz/api/v1",
        page("rankwant.uz", ""),
      ),
    ).toBe("https://rankwant.uz/api/v1");
  });
});
