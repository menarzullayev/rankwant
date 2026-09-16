import { afterEach, describe, expect, it, vi } from "vitest";
import { API_BASE, ApiError, getJson } from "@/lib/api";

const respond = (status: number, body: string, headers: Record<string, string> = {}) =>
  vi.fn(async () => new Response(body, { status, statusText: "Status text", headers }));

afterEach(() => {
  vi.unstubAllGlobals();
  vi.useRealTimers();
});

describe("getJson", () => {
  it("sends the session cookie to the API base and returns the parsed body", async () => {
    const fetchMock = respond(200, JSON.stringify({ ok: true }));
    vi.stubGlobal("fetch", fetchMock);
    await expect(getJson("/health/")).resolves.toEqual({ ok: true });
    expect(fetchMock).toHaveBeenCalledWith(
      `${API_BASE}/health/`,
      expect.objectContaining({ credentials: "include" }),
    );
  });

  it("turns the API error envelope into an ApiError with its fields", async () => {
    const body = { error: { code: "validation", message: "Bad input", details: { email: ["x"] } } };
    vi.stubGlobal("fetch", respond(400, JSON.stringify(body)));
    const error = await getJson("/me/").catch((e: unknown) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({
      status: 400,
      code: "validation",
      message: "Bad input",
      details: { email: ["x"] },
      retryAfter: 0,
    });
  });

  it("falls back to the status text when the error body is not JSON", async () => {
    vi.stubGlobal("fetch", respond(502, "<html>Bad gateway</html>"));
    await expect(getJson("/me/")).rejects.toMatchObject({
      status: 502,
      code: "error",
      message: "Status text",
    });
  });

  // 429 must tell the user how long to wait (decision 15): seconds or an HTTP date.
  it("reads Retry-After given in seconds", async () => {
    vi.stubGlobal("fetch", respond(429, "{}", { "Retry-After": "12.2" }));
    await expect(getJson("/submit/")).rejects.toMatchObject({ status: 429, retryAfter: 13 });
  });

  it("reads Retry-After given as an HTTP date", async () => {
    vi.useFakeTimers({ toFake: ["Date"] });
    vi.setSystemTime(new Date("2026-09-17T00:00:00Z"));
    vi.stubGlobal(
      "fetch",
      respond(429, "{}", { "Retry-After": "Thu, 17 Sep 2026 00:00:30 GMT" }),
    );
    await expect(getJson("/submit/")).rejects.toMatchObject({ retryAfter: 30 });
  });
});
