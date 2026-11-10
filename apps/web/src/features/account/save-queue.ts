/** Optimistic save (`optimisticSave` flag): the bar does not wait.
 *
 *  Every save is STARTED in the same tick. That is what makes leaving the
 *  page safe: a section reads its form and sends the request before its
 *  first `await`, so once `startAll` returns every payload is already on
 *  the wire — a section that unmounts a moment later loses nothing.
 *
 *  Sending them together instead of one after another is safe because the
 *  writes do not overlap: `MeSerializer.update` saves only the fields the
 *  client sent (`update_fields`), and the other sections write their own
 *  resources (`/me/skills/`, `/me/career/…`). Measured in the code on
 *  2026-11-10 before the sequential loop was dropped for this path.
 */

export type QueuedSave = {
  id: string;
  save: () => Promise<boolean>;
};

/** Starts every save now and reports each one as it settles.
 *
 *  A save that throws counts as refused (`ok = false`): an exception must
 *  not leave the bar thinking the write went through. The returned promise
 *  settles when all of them have — callers may ignore it. */
export function startAll(
  items: readonly QueuedSave[],
  onSettled: (id: string, ok: boolean) => void,
): Promise<void> {
  return Promise.all(
    items.map(async ({ id, save }) => {
      let ok = false;
      try {
        ok = await save();
      } catch {
        ok = false;
      }
      onSettled(id, ok);
    }),
  ).then(() => undefined);
}

/** The slots the bar still has to show: dirty ones that are not in flight.
 *
 *  A slot in flight keeps its own `dirty` until the server answers (the
 *  section clears it on success), so the bar would come straight back
 *  without this filter — the opposite of not waiting. */
export function shownDirty<T extends { dirty: boolean }>(
  slots: ReadonlyMap<string, T>,
  inFlight: ReadonlySet<string>,
): [string, T][] {
  return [...slots].filter(([id, slot]) => slot.dirty && !inFlight.has(id));
}
