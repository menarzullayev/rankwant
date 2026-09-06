/**
 * k6 yuklama stsenariylari — test-strategy.md § 7–10.
 *
 * Ishga tushirish:
 *   k6 run -e SCENARIO=load  tests/load/main.js
 *   k6 run -e SCENARIO=spike tests/load/main.js
 *
 * Chegaralar 04-prd NFR dan: p50 < 5s, p95 < 15s (judge),
 * sahifa p95 < 1s, standings < 300 ms.
 */
import http from "k6/http";
import { check, sleep } from "k6";
import { Trend } from "k6/metrics";

const API = __ENV.API_BASE || "http://localhost:8000/api/v1";
const SCENARIO = __ENV.SCENARIO || "load";

const standingsLatency = new Trend("standings_latency", true);
const problemsLatency = new Trend("problems_latency", true);

/**
 * Spike — RankWant uchun eng real ssenariy: contest boshlanishi.
 * 10 soniya ichida 500 submit (04-prd NFR).
 */
const SCENARIOS = {
  load: {
    executor: "ramping-vus",
    stages: [
      { duration: "30s", target: 100 },
      { duration: "1m", target: 500 },
      { duration: "30s", target: 0 },
    ],
  },
  spike: {
    executor: "ramping-arrival-rate",
    startRate: 0,
    timeUnit: "1s",
    preAllocatedVUs: 200,
    maxVUs: 800,
    stages: [
      { duration: "5s", target: 0 },
      { duration: "10s", target: 50 }, // 500 submit / 10 s
      { duration: "30s", target: 50 },
      { duration: "10s", target: 0 },
    ],
  },
  stress: {
    executor: "ramping-vus",
    stages: [
      { duration: "1m", target: 250 },
      { duration: "1m", target: 500 },
      { duration: "1m", target: 1000 },
      { duration: "1m", target: 2000 },
    ],
  },
  soak: {
    executor: "constant-vus",
    vus: 100,
    duration: __ENV.SOAK_DURATION || "12h",
  },
};

export const options = {
  scenarios: { [SCENARIO]: SCENARIOS[SCENARIO] },
  thresholds: {
    // 04-prd NFR
    "http_req_duration{name:problems}": ["p(95)<1000"],
    standings_latency: ["p(95)<300"],
    http_req_failed: ["rate<0.01"],
  },
};

export default function () {
  const problems = http.get(`${API}/problems/`, { tags: { name: "problems" } });
  check(problems, { "problems 200": (r) => r.status === 200 });
  problemsLatency.add(problems.timings.duration);

  const contests = http.get(`${API}/contests/`, { tags: { name: "contests" } });
  check(contests, { "contests 200": (r) => r.status === 200 });

  const body = contests.json();
  if (body && body.results && body.results.length > 0) {
    const slug = body.results[0].slug;
    const standings = http.get(`${API}/contests/${slug}/standings/`, {
      tags: { name: "standings" },
    });
    check(standings, { "standings 200": (r) => r.status === 200 });
    standingsLatency.add(standings.timings.duration);
  }

  sleep(1);
}
