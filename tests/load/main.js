/**
 * k6 yuklama stsenariylari — test-strategy.md § 7–10.
 *
 * Ishga tushirish:
 *   k6 run -e SCENARIO=load        tests/load/main.js
 *   k6 run -e SCENARIO=spike       tests/load/main.js
 *   k6 run -e SCENARIO=leaderboard tests/load/main.js
 *   k6 run -e SCENARIO=contest-spike tests/load/main.js
 *
 * Chegaralar 04-prd NFR dan: p50 < 5s, p95 < 15s (judge),
 * sahifa p95 < 1s, standings < 300 ms.
 */
import http from "k6/http";
import { check, sleep } from "k6";
import { Trend, Rate } from "k6/metrics";

const API = __ENV.API_BASE || "http://localhost:8000/api/v1";
const SCENARIO = __ENV.SCENARIO || "load";

const standingsLatency = new Trend("standings_latency", true);
const problemsLatency = new Trend("problems_latency", true);
const leaderboardLatency = new Trend("leaderboard_latency", true);
const judgeLatency = new Trend("judge_latency", true);
const throttled = new Rate("throttled");

/**
 * Measured per-minute submission counts, Codeforces Div. 3 #1996
 * (Codeforces Round 962), read from the public API on 2026-09-20.
 *
 * The contest ran 150 minutes and took 122,242 in-window submissions.
 * `contest.status` also returns practice and virtual submissions (294,656
 * rows), so the profile is filtered to
 * `startTimeSeconds <= t <= startTimeSeconds + durationSeconds`.
 *
 * Peak is index 2: 4,568/min = 76.1/s, two minutes in. That is 1.5x the
 * 50/s the platform's own design assumes (`judging/services.py`).
 *
 * The 60-minute dip (minutes 10, 70, 130) is a property of the source
 * data, not a transcription error. It is reproduced as measured.
 */
const PROFILE_MINUTES = [
  83, 3578, 4568, 3434, 2918, 2466, 2157, 2012, 1826, 1364, 636, 1190,
  2204, 1887, 1529, 1447, 1247, 1296, 1321, 1226, 1195, 1068, 1104, 1059,
  1084, 1063, 1033, 1061, 1030, 1038, 964, 986, 958, 1021, 953, 914,
  966, 889, 895, 894, 859, 868, 839, 801, 844, 805, 859, 774,
  815, 820, 802, 738, 729, 712, 743, 747, 739, 747, 692, 647,
  685, 642, 651, 695, 700, 637, 648, 656, 665, 451, 329, 766,
  748, 655, 590, 641, 634, 579, 595, 623, 576, 548, 596, 564,
  529, 485, 565, 521, 484, 553, 566, 515, 494, 526, 525, 522,
  540, 505, 481, 514, 500, 463, 474, 477, 527, 511, 496, 507,
  500, 512, 495, 501, 463, 495, 452, 442, 479, 460, 476, 508,
  458, 467, 481, 429, 479, 474, 460, 461, 485, 386, 313, 584,
  526, 548, 522, 534, 410, 564, 512, 520, 499, 473, 534, 517,
  520, 545, 496, 559, 566, 839,
];

/**
 * Personal access tokens for the submit scenarios (ADR-0008), as a JSON
 * array of `rw_...` strings. Read once, in the init context.
 *
 * Mint them without going through `auth/login/` — that endpoint is
 * throttled and would take hours for the 760+ tokens a real spike needs:
 *
 *   python manage.py shell -c "
 *   import json, secrets
 *   from core.models import ApiToken, User
 *   raw, out = [], []
 *   for u in User.objects.filter(username__startswith='neytron_')[:2000]:
 *       t = secrets.token_urlsafe(32)
 *       out.append('rw_' + t)
 *       raw.append(ApiToken(user=u, name='loadtest', prefix='rw_',
 *                           token_hash=ApiToken.hash_token('rw_' + t),
 *                           scopes=['submit']))
 *   ApiToken.objects.bulk_create(raw)
 *   open('/tmp/tokens.json','w').write(json.dumps(out))"
 */
const TOKENS = __ENV.SPIKE_TOKENS_FILE
  ? JSON.parse(open(__ENV.SPIKE_TOKENS_FILE))
  : [];

const SPIKE_PROBLEM = __ENV.SPIKE_PROBLEM || "";
const SPIKE_LANGUAGE = __ENV.SPIKE_LANGUAGE || "cpp23";
const SPIKE_CONTEST = __ENV.SPIKE_CONTEST || "";
const SPIKE_POLL = __ENV.SPIKE_POLL === "1";

const LEADERBOARD_PAGES = (__ENV.LB_PAGES || "1,1000")
  .split(",")
  .map((p) => Number(p.trim()))
  .filter((p) => Number.isFinite(p) && p > 0);

/**
 * Turn the measured per-minute profile into `ramping-arrival-rate` stages.
 *
 * One stage per minute, targeting that minute's rate in submissions/second.
 * k6 interpolates linearly inside a stage, so the curve comes out
 * piecewise-linear — close enough to the real spike, and it reaches the
 * measured peak exactly.
 */
function spikeStages(minutes) {
  const capped = Math.min(minutes, PROFILE_MINUTES.length);
  const stages = [];
  for (let i = 0; i < capped; i++) {
    stages.push({ duration: "1m", target: PROFILE_MINUTES[i] / 60 });
  }
  // Drain, so the queue is not left full when the run ends.
  stages.push({ duration: "30s", target: 0 });
  return stages;
}

/**
 * Distinct users a spike needs, given the `submit` throttle of 6/min per
 * user: a single account cannot send more than one submission per 10 s.
 */
function usersNeeded(peakPerSecond) {
  return Math.ceil((peakPerSecond * 60) / 6);
}

const SPIKE_MINUTES = Number(__ENV.SPIKE_MINUTES || 10);
const SPIKE_PEAK = Math.max(...PROFILE_MINUTES.slice(0, SPIKE_MINUTES)) / 60;

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
  // CI uchun: haqiqiy o'lchov beradi, lekin runner'ni yiqitmaydi.
  // `--vus 1 --duration 1s` sintaksis tekshiruvi edi, o'lchov emas.
  ci: {
    executor: "constant-vus",
    vus: Number(__ENV.CI_VUS || 20),
    duration: __ENV.CI_DURATION || "30s",
  },
  soak: {
    executor: "constant-vus",
    vus: 100,
    duration: __ENV.SOAK_DURATION || "12h",
  },
  /**
   * Leaderboard read — the endpoint that carries the imported Codeforces
   * rows. Measured 2026-09-20 against 974,498 rows: a single request takes
   * 322 ms, but 50 concurrent requests push p95 to 8,532 ms against an NFR
   * of 1,000 ms. `LB_PAGES` walks the OFFSET depth, which is where the
   * degradation lives (page 1000 is 3.5x slower than page 1).
   *
   *   k6 run -e SCENARIO=leaderboard -e LB_VUS=50 -e LB_PAGES=1,1000,10000 tests/load/main.js
   */
  leaderboard: {
    executor: "constant-vus",
    vus: Number(__ENV.LB_VUS || 20),
    duration: __ENV.LB_DURATION || "30s",
    exec: "leaderboardRead",
  },
  /**
   * Faithful replay of the measured Codeforces spike. `SPIKE_MINUTES`
   * defaults to 10, which covers the peak and the ten busiest minutes;
   * set it to 150 to replay the whole contest.
   *
   *   k6 run -e SCENARIO=contest-spike \
   *     -e SPIKE_TOKENS_FILE=/tmp/tokens.json \
   *     -e SPIKE_PROBLEM=two-sum -e SPIKE_CONTEST=div3-demo \
   *     -e SPIKE_MAX_VUS=1200 tests/load/main.js
   */
  "contest-spike": {
    executor: "ramping-arrival-rate",
    startRate: 0,
    timeUnit: "1s",
    preAllocatedVUs: Number(__ENV.SPIKE_MAX_VUS || 1200),
    maxVUs: Number(__ENV.SPIKE_MAX_VUS || 1200) * 2,
    stages: spikeStages(SPIKE_MINUTES),
    exec: "contestSpike",
  },
};

const THRESHOLDS = {
  load: {
    "http_req_duration{name:problems}": ["p(95)<1000"],
    standings_latency: ["p(95)<300"],
    http_req_failed: ["rate<0.01"],
  },
  leaderboard: {
    // 04-prd NFR: sahifa p95 < 1000 ms. Fails today at 20+ VUs — that is
    // the point of the scenario, not a broken threshold.
    "http_req_duration{name:leaderboard}": ["p(95)<1000"],
    "http_req_duration{name:leaderboard-deep}": ["p(95)<1000"],
    http_req_failed: ["rate<0.01"],
  },
  "contest-spike": {
    // 04-prd NFR: judge p50 < 5 s, p95 < 15 s. Only meaningful with
    // SPIKE_POLL=1, which waits for a verdict instead of just enqueuing.
    judge_latency: ["p(50)<5000", "p(95)<15000"],
    http_req_failed: ["rate<0.01"],
  },
};

const base = {
  "http_req_duration{name:problems}": ["p(95)<1000"],
  standings_latency: ["p(95)<300"],
  http_req_failed: ["rate<0.01"],
};

export const options = {
  scenarios: { [SCENARIO]: SCENARIOS[SCENARIO] },
  thresholds: THRESHOLDS[SCENARIO] || base,
};

export function setup() {
  if (SCENARIO !== "contest-spike") return {};

  const problems = [];
  if (!SPIKE_PROBLEM) {
    throw new Error("SPIKE_PROBLEM berilmagan — qaysi masalaga yuborishni ko'rsating");
  }
  problems.push(SPIKE_PROBLEM);

  if (TOKENS.length === 0) {
    throw new Error(
      "SPIKE_TOKENS_FILE bo'sh yoki berilmagan. `submit` throttle 6/min — " +
        `${usersNeeded(SPIKE_PEAK)} ta token kerak. Minting retsepti main.js izohida.`,
    );
  }
  const needed = usersNeeded(SPIKE_PEAK);
  if (TOKENS.length < needed) {
    console.warn(
      `⚠️  ${TOKENS.length} token bor, ${needed} kerak. ` +
        `Har bir hisob 10 soniyada faqat bitta submit yubora oladi (submit 6/min), ` +
        `shuning uchun cho'qqi ${SPIKE_PEAK.toFixed(1)}/s ga YETMAYDI — ` +
        `natija past chiqadi.`,
    );
  }
  console.log(
    `contest-spike: ${SPIKE_MINUTES} daqiqa, cho'qqi ${SPIKE_PEAK.toFixed(1)}/s ` +
      `(daqiqa ${PROFILE_MINUTES.indexOf(Math.max(...PROFILE_MINUTES.slice(0, SPIKE_MINUTES))) + 1}), ` +
      `${TOKENS.length} token`,
  );
  return {};
}

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

/**
 * Walk the leaderboard at several OFFSET depths.
 *
 * Depth is the variable that matters: `OFFSET 200000` makes Postgres sort
 * 974,497 tied rows and spill 7.5 MB to disk per request, so the deep page
 * is where the NFR breaks first.
 */
export function leaderboardRead() {
  for (const page of LEADERBOARD_PAGES) {
    const deep = page > 1;
    const res = http.get(`${API}/users/?page=${page}`, {
      tags: { name: deep ? "leaderboard-deep" : "leaderboard" },
    });
    check(res, { "leaderboard 200": (r) => r.status === 200 });
    leaderboardLatency.add(res.timings.duration);
  }
  sleep(Number(__ENV.LB_SLEEP || 0));
}

/**
 * Replay the measured Codeforces spike against the submit endpoint.
 *
 * Each VU holds its own token, because `submit` is throttled at 6/min per
 * user: a VU that reuses one account would spend the run collecting 429s
 * instead of load. Rotating by `__VU` keeps each account to roughly one
 * submission per iteration.
 */
export function contestSpike() {
  const token = TOKENS[(__VU - 1) % TOKENS.length];
  const payload = JSON.stringify({
    problem: SPIKE_PROBLEM,
    language: SPIKE_LANGUAGE,
    source_code:
      "#include <bits/stdc++.h>\nusing namespace std;\n" +
      "int main(){ios::sync_with_stdio(false);cin.tie(nullptr);return 0;}\n",
    ...(SPIKE_CONTEST ? { contest: SPIKE_CONTEST } : {}),
  });
  const params = {
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    tags: { name: "submit" },
  };

  const started = Date.now();
  const res = http.post(`${API}/judging/attempts/`, payload, params);
  throttled.add(res.status === 429);

  const accepted = check(res, {
    "submit accepted": (r) => r.status === 201 || r.status === 202,
  });
  if (!accepted || !SPIKE_POLL) return;

  const created = res.json();
  const id = created && (created.id || created.pk);
  if (!id) return;

  // Wait for a verdict so `judge_latency` measures the NFR end to end
  // (submit -> verdict), not just the enqueue.
  for (let attempt = 0; attempt < 60; attempt++) {
    sleep(0.5);
    const poll = http.get(`${API}/judging/attempts/${id}/`, {
      headers: { Authorization: `Bearer ${token}` },
      tags: { name: "verdict" },
    });
    if (poll.status !== 200) return;
    const verdict = poll.json().verdict;
    if (verdict && verdict !== "PENDING" && verdict !== "RUNNING") {
      judgeLatency.add(Date.now() - started);
      return;
    }
  }
}
