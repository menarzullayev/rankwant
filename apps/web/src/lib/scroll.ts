/** Scrolling — the one place that moves or locks a scroll position.
 *
 *  The boxes themselves are CSS: `rw-scroll-x`, `rw-scroll-y`, `rw-scroll`
 *  (both axes), `rw-scroll-trap` and `rw-snap-x` in `app/theme.css`. This
 *  module is the script half: locking the page under an overlay and
 *  bringing an element into view. `tools/check_scroll.py` keeps both
 *  halves the only way to do it — a scroll box written by hand is how
 *  forty-four of them ended up behaving forty-four ways.
 */

const INSTANT: ScrollBehavior = "auto";
const SMOOTH: ScrollBehavior = "smooth";

let locks = 0;
let before = "";

/** Stop the page behind an overlay from scrolling. Returns the release.
 *
 *  Counted: the search palette can open over the mobile drawer. Each of
 *  them used to save and restore `body.style.overflow` on its own, so the
 *  one closing last restored the other's `hidden` and left the page
 *  locked. The first lock records the value; the last release restores it.
 */
export function lockBodyScroll(): () => void {
  if (locks === 0) {
    before = document.body.style.overflow;
    document.body.style.overflow = "hidden";
  }
  locks += 1;
  let released = false;
  return () => {
    if (released) return;
    released = true;
    locks -= 1;
    if (locks === 0) document.body.style.overflow = before;
  };
}

/** The viewer asked for less motion — in the customizer (D49) or in the
 *  system. An explicit customizer level wins over the system setting. */
export function prefersReducedMotion(): boolean {
  const level = document.documentElement.dataset.motion;
  if (level === "off" || level === "reduce") return true;
  if (level) return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

/** Bring an element into view.
 *
 *  `smooth` is a request, not a promise: it is dropped when the viewer
 *  asked for less motion. The sticky header is accounted for by
 *  `scroll-padding-top` on the root, not here.
 */
export function revealElement(
  target: string | Element | null | undefined,
  options: { block?: ScrollLogicalPosition; smooth?: boolean } = {},
): void {
  const element = typeof target === "string" ? document.getElementById(target) : target;
  if (!element) return;
  // Named, not inline: `check_hardcoded.py` reads a string in a ternary
  // branch as text that skipped translation.
  let behavior: ScrollBehavior = INSTANT;
  if (options.smooth && !prefersReducedMotion()) behavior = SMOOTH;
  element.scrollIntoView({ block: options.block ?? "nearest", behavior });
}
