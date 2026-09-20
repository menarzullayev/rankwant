/** Chiziq scroller — 2px rels, qisqa qizil belgi, overlay (joy yemaydi).
 *
 *  Eskiz plastina 09. Nativ yo'l CSS da o'chiriladi; bu modul faqat
 *  belgini joylashtiradi. DOM o'ralmaydi: flex/`overflow` buzilmasin. */

export const CHIZIQ_TICK = 22;
export const CHIZIQ_INSET = 8;
export const CHIZIQ_EDGE = 5;

const LAYER_ID = "rw-chiziq-layer";
const SKIP_TAGS = new Set([
  "SCRIPT",
  "STYLE",
  "LINK",
  "META",
  "HEAD",
  "BR",
  "IMG",
  "NOSCRIPT",
  "IFRAME",
  "CANVAS",
  "VIDEO",
  "AUDIO",
  "SOURCE",
  "TRACK",
  "COL",
  "COLGROUP",
]);

const SCROLL_OVERFLOW = new Set(["auto", "scroll", "overlay"]);

export type Box = {
  top: number;
  left: number;
  right: number;
  bottom: number;
  width: number;
  height: number;
};

export function tickSize(track: number, preferred = CHIZIQ_TICK): number {
  if (track <= 0) return 0;
  return Math.min(preferred, track);
}

export function tickOffset(
  scroll: number,
  maxScroll: number,
  track: number,
  tick = CHIZIQ_TICK,
): number {
  if (maxScroll <= 0 || track <= 0) return 0;
  const size = tickSize(track, tick);
  const range = Math.max(0, track - size);
  const t = Math.min(1, Math.max(0, scroll / maxScroll));
  return t * range;
}

export function axisOverflows(input: {
  overflowX: string;
  overflowY: string;
  scrollWidth: number;
  scrollHeight: number;
  clientWidth: number;
  clientHeight: number;
}): { x: boolean; y: boolean } {
  return {
    x:
      SCROLL_OVERFLOW.has(input.overflowX) &&
      input.scrollWidth > input.clientWidth + 1,
    y:
      SCROLL_OVERFLOW.has(input.overflowY) &&
      input.scrollHeight > input.clientHeight + 1,
  };
}

export function viewportOverflows(input: {
  scrollWidth: number;
  scrollHeight: number;
  clientWidth: number;
  clientHeight: number;
}): { x: boolean; y: boolean } {
  return {
    x: input.scrollWidth > input.clientWidth + 1,
    y: input.scrollHeight > input.clientHeight + 1,
  };
}

export function intersectBoxes(a: Box, b: Box): Box | null {
  const left = Math.max(a.left, b.left);
  const top = Math.max(a.top, b.top);
  const right = Math.min(a.right, b.right);
  const bottom = Math.min(a.bottom, b.bottom);
  const width = right - left;
  const height = bottom - top;
  if (width < 8 || height < 8) return null;
  return { left, top, right, bottom, width, height };
}

/** Overlay panel (customizer, dialog) viewport chetini yopsa, sahifa
 *  relsi shu panelning ichki chetiga suriladi — ikkala belgi ustma-ust
 *  tushmasin. */
export function shrinkPageClip(
  page: Box,
  overlay: Box,
  viewport: { width: number; height: number },
): Box | null {
  let box = { ...page };
  const coversRight =
    overlay.right >= viewport.width - 12 &&
    overlay.left > viewport.width * 0.35 &&
    overlay.top < box.bottom &&
    overlay.bottom > box.top;
  if (coversRight) {
    const right = Math.min(box.right, overlay.left);
    const width = right - box.left;
    if (width < 8) return null;
    box = { ...box, right, width };
  }
  const coversBottom =
    overlay.bottom >= viewport.height - 12 &&
    overlay.top > viewport.height * 0.35 &&
    overlay.left < box.right &&
    overlay.right > box.left;
  if (coversBottom) {
    const bottom = Math.min(box.bottom, overlay.top);
    const height = bottom - box.top;
    if (height < 8) return null;
    box = { ...box, bottom, height };
  }
  return box;
}

function boxFromDom(r: DOMRectReadOnly): Box {
  return {
    top: r.top,
    left: r.left,
    right: r.right,
    bottom: r.bottom,
    width: r.width,
    height: r.height,
  };
}

function skipHost(el: HTMLElement): boolean {
  if (SKIP_TAGS.has(el.tagName)) return true;
  if (el.id === LAYER_ID) return true;
  if (el.dataset.chiziqSkip != null) return true;
  if (el.closest("#" + LAYER_ID)) return true;
  if (el.closest("[data-chiziq-skip], .monaco-editor, .monaco-diff-editor")) {
    return true;
  }
  return false;
}

function hasFixedAncestor(el: HTMLElement): boolean {
  let node: HTMLElement | null = el;
  while (node && node !== document.documentElement) {
    if (getComputedStyle(node).position === "fixed") return true;
    node = node.parentElement;
  }
  return false;
}

function overflowFlags(el: HTMLElement, isPage: boolean): { x: boolean; y: boolean } {
  const node = isPage
    ? ((document.scrollingElement as HTMLElement | null) ?? el)
    : el;
  if (isPage) return viewportOverflows(node);
  const style = getComputedStyle(el);
  return axisOverflows({
    overflowX: style.overflowX,
    overflowY: style.overflowY,
    scrollWidth: node.scrollWidth,
    scrollHeight: node.scrollHeight,
    clientWidth: node.clientWidth,
    clientHeight: node.clientHeight,
  });
}

function visibleClip(el: HTMLElement, isPage: boolean): Box | null {
  const viewport: Box = {
    top: 0,
    left: 0,
    right: window.innerWidth,
    bottom: window.innerHeight,
    width: window.innerWidth,
    height: window.innerHeight,
  };
  let box = isPage ? viewport : intersectBoxes(boxFromDom(el.getBoundingClientRect()), viewport);
  if (!box) return null;
  if (isPage) return box;

  let node = el.parentElement;
  while (node && node !== document.documentElement) {
    const style = getComputedStyle(node);
    const clipX = SCROLL_OVERFLOW.has(style.overflowX) || style.overflowX === "hidden";
    const clipY = SCROLL_OVERFLOW.has(style.overflowY) || style.overflowY === "hidden";
    if (clipX || clipY) {
      box = intersectBoxes(box, boxFromDom(node.getBoundingClientRect()));
      if (!box) return null;
    }
    node = node.parentElement;
  }
  return box;
}

type Rails = {
  host: HTMLElement;
  isPage: boolean;
  y: HTMLElement;
  x: HTMLElement;
  yThumb: HTMLElement;
  xThumb: HTMLElement;
  ro: ResizeObserver;
};

function makeTrack(axis: "x" | "y"): { track: HTMLElement; thumb: HTMLElement } {
  const track = document.createElement("div");
  track.className = axis === "y" ? "rw-chiziq-y" : "rw-chiziq-x";
  track.setAttribute("aria-hidden", "true");
  const thumb = document.createElement("div");
  thumb.className = axis === "y" ? "rw-chiziq-y-thumb" : "rw-chiziq-x-thumb";
  track.append(thumb);
  return { track, thumb };
}

function bindDrag(
  host: HTMLElement,
  isPage: boolean,
  track: HTMLElement,
  thumb: HTMLElement,
  axis: "x" | "y",
): void {
  const scroller = () => (isPage ? document.scrollingElement ?? host : host);

  thumb.addEventListener("pointerdown", (event) => {
    event.preventDefault();
    event.stopPropagation();
    thumb.setPointerCapture(event.pointerId);
    const node = scroller();
    const start = axis === "y" ? event.clientY : event.clientX;
    const startScroll = axis === "y" ? node.scrollTop : node.scrollLeft;
    const trackSize = axis === "y" ? track.clientHeight : track.clientWidth;
    const thumbSize = axis === "y" ? thumb.offsetHeight : thumb.offsetWidth;
    const scrollMax =
      axis === "y"
        ? node.scrollHeight - node.clientHeight
        : node.scrollWidth - node.clientWidth;
    const range = Math.max(1, trackSize - thumbSize);

    const move = (ev: PointerEvent) => {
      const delta = (axis === "y" ? ev.clientY : ev.clientX) - start;
      const next = startScroll + (delta / range) * scrollMax;
      if (axis === "y") node.scrollTop = next;
      else node.scrollLeft = next;
    };
    const up = () => {
      thumb.removeEventListener("pointermove", move);
      thumb.removeEventListener("pointerup", up);
    };
    thumb.addEventListener("pointermove", move);
    thumb.addEventListener("pointerup", up);
  });

  track.addEventListener("pointerdown", (event) => {
    if (event.target === thumb) return;
    const node = scroller();
    const rect = track.getBoundingClientRect();
    if (axis === "y") {
      const ratio = (event.clientY - rect.top) / Math.max(1, rect.height);
      node.scrollTop = ratio * (node.scrollHeight - node.clientHeight);
    } else {
      const ratio = (event.clientX - rect.left) / Math.max(1, rect.width);
      node.scrollLeft = ratio * (node.scrollWidth - node.clientWidth);
    }
  });
}

function place(rails: Rails, overlays: Iterable<HTMLElement>): void {
  const node = rails.isPage
    ? (document.scrollingElement as HTMLElement | null) ?? rails.host
    : rails.host;
  const flags = overflowFlags(rails.host, rails.isPage);

  let clip = flags.x || flags.y ? visibleClip(rails.host, rails.isPage) : null;
  if (clip && rails.isPage) {
    const viewport = { width: window.innerWidth, height: window.innerHeight };
    for (const host of overlays) {
      if (host === rails.host) continue;
      if (!hasFixedAncestor(host)) continue;
      const next = shrinkPageClip(clip, boxFromDom(host.getBoundingClientRect()), viewport);
      if (!next) {
        clip = null;
        break;
      }
      clip = next;
    }
  }
  if (!clip) {
    rails.y.hidden = true;
    rails.x.hidden = true;
    return;
  }

  const yH = Math.max(0, clip.height - CHIZIQ_INSET * 2 - (flags.x ? 10 : 0));
  const xW = Math.max(0, clip.width - CHIZIQ_INSET * 2 - (flags.y ? 10 : 0));

  rails.y.hidden = !flags.y || yH < 12;
  rails.x.hidden = !flags.x || xW < 12;
  rails.y.classList.toggle("is-page", rails.isPage);
  rails.x.classList.toggle("is-page", rails.isPage);

  if (!rails.y.hidden) {
    rails.y.style.top = `${clip.top + CHIZIQ_INSET}px`;
    rails.y.style.height = `${yH}px`;
    rails.y.style.right = `${Math.max(0, window.innerWidth - clip.right + CHIZIQ_EDGE)}px`;
    const maxY = Math.max(1, node.scrollHeight - node.clientHeight);
    const tick = tickSize(yH);
    rails.yThumb.style.height = `${tick}px`;
    rails.yThumb.style.transform = `translate3d(0, ${tickOffset(node.scrollTop, maxY, yH, tick)}px, 0)`;
  }

  if (!rails.x.hidden) {
    rails.x.style.left = `${clip.left + CHIZIQ_INSET}px`;
    rails.x.style.width = `${xW}px`;
    rails.x.style.bottom = `${Math.max(0, window.innerHeight - clip.bottom + CHIZIQ_EDGE)}px`;
    const maxX = Math.max(1, node.scrollWidth - node.clientWidth);
    const tick = tickSize(xW);
    rails.xThumb.style.width = `${tick}px`;
    rails.xThumb.style.transform = `translate3d(${tickOffset(node.scrollLeft, maxX, xW, tick)}px, 0, 0)`;
  }
}

function pageHost(): HTMLElement {
  return document.documentElement;
}

function isPageHost(el: HTMLElement): boolean {
  const scrolling = document.scrollingElement;
  return el === document.documentElement || el === scrolling || el === document.body;
}

/** Sahifa skrolleri bitta. `html` va `body` ni alohida tutmaslik. */
function shouldTrack(el: HTMLElement): boolean {
  if (skipHost(el)) return false;
  if (isPageHost(el)) return el === pageHost();
  const style = getComputedStyle(el);
  if (style.display === "none" || style.visibility === "hidden") return false;
  const flags = overflowFlags(el, false);
  return flags.x || flags.y;
}

function walk(root: ParentNode, into: HTMLElement[]): void {
  const visit = (el: HTMLElement) => {
    if (el.id === LAYER_ID) return;
    if (el.matches(".monaco-editor, .monaco-diff-editor, [data-chiziq-skip]")) {
      return;
    }
    if (shouldTrack(el)) into.push(el);
    const children = el.children;
    for (let i = 0; i < children.length; i += 1) {
      const child = children[i];
      if (child instanceof HTMLElement) visit(child);
    }
  };
  if (root instanceof HTMLElement) visit(root);
  else {
    const children = root.childNodes;
    for (let i = 0; i < children.length; i += 1) {
      const child = children[i];
      if (child instanceof HTMLElement) visit(child);
    }
  }
}

function ensureLayer(): HTMLElement {
  let layer = document.getElementById(LAYER_ID);
  if (layer instanceof HTMLElement) return layer;
  layer = document.createElement("div");
  layer.id = LAYER_ID;
  layer.setAttribute("aria-hidden", "true");
  document.documentElement.append(layer);
  return layer;
}

let refs = 0;
let engine: { stop: () => void } | null = null;

export function startChiziq(): () => void {
  refs += 1;
  try {
    if (!engine) engine = boot();
  } catch {
    refs -= 1;
    return () => undefined;
  }
  return () => {
    refs -= 1;
    if (refs > 0) return;
    engine?.stop();
    engine = null;
    refs = 0;
  };
}

function boot(): { stop: () => void } {
  const layer = ensureLayer();
  const railsByHost = new Map<HTMLElement, Rails>();
  const scrollCleanups = new Map<HTMLElement, () => void>();
  let scanTimer = 0;
  let placeQueued = false;

  const queuePlace = () => {
    if (placeQueued) return;
    placeQueued = true;
    requestAnimationFrame(() => {
      placeQueued = false;
      railsByHost.forEach((entry) => place(entry, railsByHost.keys()));
    });
  };

  const attach = (host: HTMLElement) => {
    if (railsByHost.has(host)) return;
    const yPair = makeTrack("y");
    const xPair = makeTrack("x");
    const isPage = host === pageHost();
    bindDrag(host, isPage, yPair.track, yPair.thumb, "y");
    bindDrag(host, isPage, xPair.track, xPair.thumb, "x");
    layer.append(yPair.track, xPair.track);
    const listen: EventTarget = isPage ? window : host;
    const onScroll = () => queuePlace();
    listen.addEventListener("scroll", onScroll, { passive: true });
    const ro = new ResizeObserver(queuePlace);
    ro.observe(host);
    scrollCleanups.set(host, () => listen.removeEventListener("scroll", onScroll));
    const rails: Rails = {
      host,
      isPage,
      y: yPair.track,
      x: xPair.track,
      yThumb: yPair.thumb,
      xThumb: xPair.thumb,
      ro,
    };
    railsByHost.set(host, rails);
    place(rails, railsByHost.keys());
  };

  const detach = (host: HTMLElement) => {
    const rails = railsByHost.get(host);
    if (!rails) return;
    rails.ro.disconnect();
    scrollCleanups.get(host)?.();
    scrollCleanups.delete(host);
    rails.y.remove();
    rails.x.remove();
    railsByHost.delete(host);
  };

  const scan = () => {
    scanTimer = 0;
    try {
      const wanted = new Set<HTMLElement>();
      const found: HTMLElement[] = [];
      walk(document.body, found);
      found.push(pageHost());
      for (const el of found) {
        if (el === pageHost() || shouldTrack(el)) wanted.add(el);
      }

      railsByHost.forEach((_, host) => {
        if (!host.isConnected || !wanted.has(host)) detach(host);
      });
      wanted.forEach(attach);
      queuePlace();
    } catch {
      /* bitta buzuq tugun butun overlayni o'chirmasin */
    }
  };

  const queueScan = () => {
    if (scanTimer) return;
    scanTimer = window.setTimeout(scan, 48);
  };

  const mo = new MutationObserver(queueScan);
  mo.observe(document.documentElement, { subtree: true, childList: true });

  window.addEventListener("scroll", queuePlace, true);
  window.addEventListener("resize", queueScan);
  visualViewport?.addEventListener("resize", queuePlace);
  visualViewport?.addEventListener("scroll", queuePlace);

  scan();

  return {
    stop() {
      window.clearTimeout(scanTimer);
      mo.disconnect();
      window.removeEventListener("scroll", queuePlace, true);
      window.removeEventListener("resize", queueScan);
      visualViewport?.removeEventListener("resize", queuePlace);
      visualViewport?.removeEventListener("scroll", queuePlace);
      railsByHost.forEach((_, host) => detach(host));
      layer.remove();
    },
  };
}
