/**
 * RankWant — "texnik ishlar" sahifasi.
 *
 * Preview bitta mashinada ishlaydi va tashqariga faqat Cloudflare Tunnel
 * orqali chiqadi. Mashina o'chsa yoki boshqa tizimga o'tsa, tunnelda ulagich
 * qolmaydi va Cloudflare xom "Error 1033" sahifasini (530) ko'rsatadi.
 *
 * Worker so'rovni o'zgartirmasdan origin'ga uzatadi va faqat origin YO'Q
 * bo'lgandagina o'z javobini beradi. Ilovaning o'z xatolari (404, 500, 503)
 * tegilmaydi — ular foydalanuvchiga kerakli ma'lumotni olib yuradi.
 */

// 502/504 — tunnel bor, lekin orqasidagi servis javob bermadi;
// 520–526 — Cloudflare origin bilan gaplasha olmadi;
// 530 — tunnelda ulagich yo'q (Error 1033).
const ORIGIN_DOWN = new Set([502, 504, 520, 521, 522, 523, 524, 525, 526, 530]);

const RETRY_AFTER_SECONDS = "300";

// Brend belgisi (docs/brand/mark-choqqi-params.md). Inline — origin o'chiq
// paytda /brand/mark-choqqi.svg ham ochilmaydi.
const LOGO = `<svg viewBox="0 0 1024 1024" aria-hidden="true">
<path class="navy" d="M116.5 799L420 294.5L559 501.5L649 396.5L914.5 798L649 799.5L595 826.5L365 826.5L313 799.5Z"/>
<path fill="#44A0FC" d="M159.5 771L420 323.5L553 558.5L648 421.5L860.5 764L666 709.5L565 776.5L378 776.5L325 707.5Z"/>
<path fill="#1074DC" d="M162 772L174 753L359 562L324 706Z"/>
<path fill="#1074DC" d="M569 774L671 584L860 764L667 708Z"/>
<circle cx="420.5" cy="206.76" r="44.1" fill="#44A0FC"/>
</svg>`;

const PAGE = `<!doctype html>
<html lang="uz">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="60">
<meta name="robots" content="noindex">
<title>RankWant — texnik ishlar</title>
<style>
  :root { --text: #102038; --muted: #4a5a70; --bg: #ffffff; --line: #dde4ee; --logo-navy: #102038; }
  @media (prefers-color-scheme: dark) {
    :root { --text: #e8eef7; --muted: #9fb0c6; --bg: #0d1726; --line: #22324a; --logo-navy: #33507e; }
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; min-height: 100vh; display: grid; place-items: center; padding: 24px;
    background: var(--bg); color: var(--text);
    font: 16px/1.55 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  }
  main { width: 100%; max-width: 560px; }
  svg { display: block; width: 72px; height: 72px; margin-bottom: 20px; }
  .navy { fill: var(--logo-navy); }
  .bar { width: 64px; height: 4px; border-radius: 2px; background: #44A0FC; margin-bottom: 24px; }
  h1 { margin: 0 0 8px; font-size: 1.5rem; line-height: 1.25; }
  p { margin: 0; color: var(--muted); }
  section + section { margin-top: 20px; padding-top: 20px; border-top: 1px solid var(--line); }
</style>
</head>
<body>
<main>
${LOGO}
<div class="bar"></div>
<section lang="uz">
  <h1>RankWant vaqtincha ishlamayapti</h1>
  <p>Server texnik ishlar uchun o'chirilgan. Sahifa har daqiqada o'zi yangilanadi va sayt qaytishi bilan ochiladi.</p>
</section>
<section lang="ru">
  <h1>RankWant временно недоступен</h1>
  <p>Сервер отключён на техническое обслуживание. Страница обновляется каждую минуту и откроет сайт, как только он вернётся.</p>
</section>
<section lang="en">
  <h1>RankWant is temporarily unavailable</h1>
  <p>The server is down for maintenance. This page refreshes every minute and opens the site as soon as it is back.</p>
</section>
</main>
</body>
</html>`;

export default {
  async fetch(request) {
    let response;
    try {
      response = await fetch(request);
    } catch {
      return maintenance(request);
    }
    if (!ORIGIN_DOWN.has(response.status)) return response;
    await response.body?.cancel();
    return maintenance(request);
  },
};

export function maintenance(request) {
  const headers = { "Cache-Control": "no-store", "Retry-After": RETRY_AFTER_SECONDS };
  if (new URL(request.url).pathname.startsWith("/api/")) {
    // Loyiha xato formati (docs/08-technical-spec) — barcha 4xx/5xx uchun bir xil.
    return Response.json(
      {
        error: {
          code: "maintenance",
          message: "RankWant vaqtincha ishlamayapti. Birozdan keyin qayta urinib ko'ring.",
          details: {},
        },
      },
      { status: 503, headers },
    );
  }
  return new Response(request.method === "HEAD" ? null : PAGE, {
    status: 503,
    headers: { ...headers, "Content-Type": "text/html; charset=utf-8" },
  });
}
