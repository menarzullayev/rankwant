import { afterEach, describe, expect, it } from "vitest";

import { contentSecurityPolicy } from "@/lib/security-headers";

describe("contentSecurityPolicy connect-src", () => {
  const prev = process.env.NEXT_PUBLIC_API_BASE;

  afterEach(() => {
    if (prev === undefined) delete process.env.NEXT_PUBLIC_API_BASE;
    else process.env.NEXT_PUBLIC_API_BASE = prev;
  });

  it("allows local API origin in dev for split web/API ports", () => {
    process.env.NEXT_PUBLIC_API_BASE = "http://127.0.0.1:8301/api/v1";
    const csp = contentSecurityPolicy("test-nonce", true, false);
    expect(csp).toContain("connect-src 'self' ws: wss:");
    expect(csp).toContain("http://127.0.0.1:8301");
  });

  it("does not expose API origin in production CSP", () => {
    process.env.NEXT_PUBLIC_API_BASE = "http://127.0.0.1:8301/api/v1";
    const csp = contentSecurityPolicy("test-nonce", false, false);
    expect(csp).toContain("connect-src 'self'");
    expect(csp).not.toContain("8301");
  });

  it("allows local API in production CSP on loopback preview host", () => {
    process.env.NEXT_PUBLIC_API_BASE = "http://127.0.0.1:8301/api/v1";
    const csp = contentSecurityPolicy("test-nonce", false, false, true);
    expect(csp).toContain("http://127.0.0.1:8301");
    expect(csp).toContain("http://127.0.0.1:8302");
    expect(csp).not.toContain("ws:");
  });
});

describe("contentSecurityPolicy frame-src", () => {
  it("frames the Turnstile check and the two course video players, nothing else", () => {
    // Without the directive `default-src 'self'` blocks the frame: the
    // widget yields no token and the API refuses every sign-up. Course
    // lessons embed YouTube (no-cookie host) and Vimeo (ADR-0056).
    const csp = contentSecurityPolicy("test-nonce", false, true);
    expect(csp).toContain(
      "frame-src https://challenges.cloudflare.com https://www.youtube-nocookie.com https://player.vimeo.com;",
    );
    expect(csp).toContain("frame-ancestors 'none'");
  });
});

describe("contentSecurityPolicy media", () => {
  afterEach(() => {
    delete process.env.NEXT_PUBLIC_VIDEO_ORIGIN;
  });

  it("plays MSE video from blob: and adds nothing else by default", () => {
    const csp = contentSecurityPolicy("n", false, true);
    expect(csp).toContain("media-src 'self' blob:;");
  });

  it("lets the course video bucket in once its origin is configured", () => {
    process.env.NEXT_PUBLIC_VIDEO_ORIGIN = "https://video.example.uz/some/path, not a url";
    const csp = contentSecurityPolicy("n", false, true);
    expect(csp).toContain("media-src 'self' blob: https://video.example.uz;");
    expect(csp).toMatch(/connect-src 'self' https:\/\/video\.example\.uz[;\s]/);
  });
});
