import { afterEach, test } from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.js";

const realFetch = globalThis.fetch;
afterEach(() => {
  globalThis.fetch = realFetch;
});

function origin(status, body = "origin body") {
  globalThis.fetch = async () => new Response(body, { status });
}

const request = (path = "/", init) => new Request(`https://rankwant.uz${path}`, init);

test("sog' javob o'zgarishsiz o'tadi", async () => {
  origin(200, "hello");
  const res = await worker.fetch(request());
  assert.equal(res.status, 200);
  assert.equal(await res.text(), "hello");
});

test("ilovaning o'z xatolari tegilmaydi", async () => {
  for (const status of [404, 500, 503]) {
    origin(status, `app ${status}`);
    const res = await worker.fetch(request());
    assert.equal(res.status, status);
    assert.equal(await res.text(), `app ${status}`);
  }
});

test("tunnel o'chiq (530) — texnik ishlar sahifasi", async () => {
  origin(530, "error code: 1033");
  const res = await worker.fetch(request("/problems/"));
  assert.equal(res.status, 503);
  assert.equal(res.headers.get("retry-after"), "300");
  assert.equal(res.headers.get("cache-control"), "no-store");
  assert.match(res.headers.get("content-type"), /text\/html/);
  const html = await res.text();
  assert.match(html, /RankWant vaqtincha ishlamayapti/);
  assert.doesNotMatch(html, /1033/);
});

test("origin xatolari 502, 504, 520–526 ham sahifaga aylanadi", async () => {
  for (const status of [502, 504, 520, 521, 522, 523, 524, 525, 526]) {
    origin(status);
    assert.equal((await worker.fetch(request())).status, 503, `status ${status}`);
  }
});

test("/api/* loyiha xato formatini oladi", async () => {
  origin(530);
  const res = await worker.fetch(request("/api/v1/problems/"));
  assert.equal(res.status, 503);
  assert.match(res.headers.get("content-type"), /application\/json/);
  const body = await res.json();
  assert.equal(body.error.code, "maintenance");
  assert.equal(typeof body.error.message, "string");
  assert.deepEqual(body.error.details, {});
});

test("tarmoq xatosi ham sahifaga aylanadi", async () => {
  globalThis.fetch = async () => {
    throw new TypeError("network down");
  };
  assert.equal((await worker.fetch(request())).status, 503);
});

test("HEAD so'roviga tanasiz javob", async () => {
  origin(530);
  const res = await worker.fetch(request("/", { method: "HEAD" }));
  assert.equal(res.status, 503);
  assert.equal(await res.text(), "");
});
