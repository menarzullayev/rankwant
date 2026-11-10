/** The alphabet of the request being rendered (ADR-0059).
 *
 *  `t()` is synchronous and the dictionary registry is one per process, yet
 *  the server renders Uzbek readers in both alphabets at the same time. So
 *  the choice travels with the request: `instrumentation.ts` wraps every
 *  incoming request in this store (from its `rw_alphabet` cookie), and the
 *  variant resolver installed by `messages.server.ts` reads it during
 *  rendering — server components and the SSR of client components alike,
 *  because both run inside that request's async context.
 *
 *  ⚠️ On `globalThis`: Next evaluates server modules more than once
 *  (instrumentation, server components, SSR). Each copy must see the same
 *  store, the same trick the dictionary registry uses.
 */

import { AsyncLocalStorage } from "node:async_hooks";

import type { Alphabet } from "./alphabet";

type Store = AsyncLocalStorage<Alphabet>;
const realm = globalThis as typeof globalThis & { __rwAlphabetStore?: Store };
const store: Store = (realm.__rwAlphabetStore ??= new AsyncLocalStorage<Alphabet>());

/** Runs `fn` — a whole request — with `alphabet` as its alphabet. */
export function runWithAlphabet<T>(alphabet: Alphabet, fn: () => T): T {
  return store.run(alphabet, fn);
}

/** The current request's alphabet, or `undefined` outside a request. */
export function requestAlphabet(): Alphabet | undefined {
  return store.getStore();
}
