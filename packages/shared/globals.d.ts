/**
 * Minimal host globals for `@rankwant/shared`.
 *
 * WHY NOT `lib: ["dom"]` OR `@types/node`: this package must not know which
 * host it runs on. Pulling in the DOM lib would let a contributor write
 * `document.querySelector` here and only find out when a worker crashed;
 * pulling in `@types/node` points the dependency arrow at one specific
 * runtime, which is exactly the coupling the `packages/` split exists to
 * remove.
 *
 * So the tiny surface the code actually touches is declared here, by hand,
 * and it is deliberately small:
 *
 *   - `window`  — read ONLY by `evictOtherLocales` as a proxy for "is this a
 *                 browser?" Its absence is the feature.
 *   - `process` — read once, for `NODE_ENV` (the dev-throw policy).
 *   - `console` — the missing-property warning in production.
 *   - `TextEncoder` — the `sourceSchema` byte-length rule. Web, Node and
 *                 workers all ship it; it is the one encoding primitive the
 *                 validation layer genuinely needs, and hard-coding it here
 *                 keeps the size check host-independent.
 *
 * Adding a name here is a design decision, not a convenience: if a module
 * needs more of the DOM, that module belongs in the app.
 */

declare const window: { document?: unknown } | undefined;

declare const process: { env: Record<string, string | undefined> };

declare const console: {
  error(...args: unknown[]): void;
  warn(...args: unknown[]): void;
};

declare class TextEncoder {
  encode(input?: string): Uint8Array;
}
