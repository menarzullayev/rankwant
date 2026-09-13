(() => {
  const q = (sel) => [...document.querySelectorAll(sel)];
  const clean = (s) => (s || "").replace(/\s+/g, " ").trim();

  // Next.js SSR streaming'i Suspense chegarasini `<div hidden id="S:0">`
  // ichiga yozadi va React uni keyin joyiga ko'chiradi. Capture shu
  // oynada bo'lsa, forma IKKI MARTA sanaladi — o'lchandi: register
  // sahifasida 16 maydon chiqdi, aslida 8. Shu sababli yashirin
  // daraxt tashlab yuboriladi.
  const inHidden = (el) => el.closest("[hidden]") !== null;
  const qv = (sel) => q(sel).filter((el) => !inHidden(el));

  const meta = {};
  for (const m of q("meta")) {
    const k = m.getAttribute("name") || m.getAttribute("property");
    if (k) meta[k] = m.getAttribute("content") || "";
  }

  const fields = qv("input, select, textarea").map((el) => ({
    tag: el.tagName.toLowerCase(),
    type: el.type || "",
    name: el.name || "",
    id: el.id || "",
    placeholder: el.placeholder || "",
    autocomplete: el.autocomplete || "",
    required: !!el.required,
    label:
      el.labels && el.labels[0] ? clean(el.labels[0].textContent) : "",
    options:
      el.tagName === "SELECT"
        ? [...el.options].slice(0, 12).map((o) => clean(o.textContent))
        : undefined,
  }));

  const buttons = qv("button, [role=button], input[type=submit]").map((b) => ({
    text: clean(b.textContent || b.value),
    type: b.type || "",
    aria: b.getAttribute("aria-label") || "",
  }));

  const links = qv("a[href]")
    .map((a) => ({ text: clean(a.textContent).slice(0, 80), href: a.getAttribute("href") }))
    .filter((l) => l.text || l.href);

  // Resurslar — nima yuklanganini va hajmini ko'rish uchun.
  const res = performance.getEntriesByType("resource");
  const byType = {};
  for (const r of res) {
    const t = r.initiatorType || "other";
    byType[t] = byType[t] || { count: 0, bytes: 0 };
    byType[t].count += 1;
    byType[t].bytes += r.transferSize || 0;
  }

  const nav = performance.getEntriesByType("navigation")[0] || {};

  // Tashqi domenlar — loyiha "hammasi self-host" qoidasiga zid joylar.
  const hosts = {};
  for (const r of res) {
    try {
      const h = new URL(r.name).host;
      if (h && h !== location.host) hosts[h] = (hosts[h] || 0) + 1;
    } catch {}
  }

  return JSON.stringify({
    url: location.href,
    title: document.title,
    lang: document.documentElement.lang,
    meta,
    fields,
    buttons,
    links: links.slice(0, 120),
    counts: {
      nodes: document.querySelectorAll("*").length,
      forms: q("form").length,
      fields: fields.length,
      buttons: buttons.length,
      links: links.length,
      scripts: q("script").length,
      stylesheets: q('link[rel=stylesheet]').length,
      images: q("img").length,
      svg: q("svg").length,
    },
    perf: {
      domContentLoaded: Math.round(nav.domContentLoadedEventEnd || 0),
      load: Math.round(nav.loadEventEnd || 0),
      transferKB: Math.round(res.reduce((a, r) => a + (r.transferSize || 0), 0) / 1024),
      resources: res.length,
      byType,
    },
    externalHosts: hosts,
    bodyText: clean(document.body.innerText).slice(0, 3000),
  });
})()
