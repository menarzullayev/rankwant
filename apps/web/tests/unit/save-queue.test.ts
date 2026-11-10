import { describe, expect, it } from "vitest";

import { shownDirty, startAll } from "@/features/account/save-queue";

/** A save whose answer the test hands out later. */
function deferred() {
  let answer!: (ok: boolean) => void;
  let fail!: (err: unknown) => void;
  const promise = new Promise<boolean>((resolve, reject) => {
    answer = resolve;
    fail = reject;
  });
  return { promise, answer, fail };
}

describe("startAll — optimistic save", () => {
  it("starts every save in the same tick, before any answer", () => {
    const started: string[] = [];
    const a = deferred();
    const b = deferred();
    void startAll(
      [
        { id: "a", save: () => (started.push("a"), a.promise) },
        { id: "b", save: () => (started.push("b"), b.promise) },
      ],
      () => {},
    );
    // Both requests are out although neither has answered: a section that
    // unmounts now has already sent its payload.
    expect(started).toEqual(["a", "b"]);
  });

  it("reports each outcome, a thrown save as refused", async () => {
    const settled: [string, boolean][] = [];
    await startAll(
      [
        { id: "ok", save: async () => true },
        { id: "refused", save: async () => false },
        {
          id: "threw",
          save: async () => {
            throw new Error("network");
          },
        },
      ],
      (id, ok) => settled.push([id, ok]),
    );
    expect(Object.fromEntries(settled)).toEqual({ ok: true, refused: false, threw: false });
  });

  it("reports a fast answer without waiting for a slow one", async () => {
    const slow = deferred();
    const settled: string[] = [];
    const all = startAll(
      [
        { id: "slow", save: () => slow.promise },
        { id: "fast", save: async () => true },
      ],
      (id) => settled.push(id),
    );
    await Promise.resolve();
    await Promise.resolve();
    expect(settled).toEqual(["fast"]);
    slow.answer(true);
    await all;
    expect(settled).toEqual(["fast", "slow"]);
  });
});

describe("shownDirty — what the bar still asks for", () => {
  const slots = new Map([
    ["clean", { dirty: false }],
    ["edited", { dirty: true }],
    ["sending", { dirty: true }],
  ]);

  it("leaves out clean slots and slots in flight", () => {
    expect(shownDirty(slots, new Set(["sending"])).map(([id]) => id)).toEqual(["edited"]);
  });

  it("brings a refused slot back once it is no longer in flight", () => {
    expect(shownDirty(slots, new Set()).map(([id]) => id)).toEqual(["edited", "sending"]);
  });
});
