"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
} from "react";

import { Button } from "@/components/ui/Button";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";

/** One editable thing on a settings page: a form, a table of switches.
 *
 *  `save` resolves to `false` when nothing was written (validation failed,
 *  the request was refused) — the slot then stays dirty and the bar stays. */
type Slot = {
  dirty: boolean;
  save: () => Promise<boolean>;
  reset: () => void;
};

type Registry = {
  set: (id: string, slot: Slot) => void;
  drop: (id: string) => void;
};

const RegistryContext = createContext<Registry | null>(null);
const SlotsContext = createContext<Map<string, Slot>>(new Map());

/** Holds every slot of the page and draws one bar for all of them
 *  (decision of 2026-10-05).
 *
 *  Before this each card had its own Save button — two on the longest page
 *  — and pressing one left the other card's edits behind without a word.
 *  Actions that are not "edit, then save" keep their own button: changing
 *  the password, the username, joining a team. */
export function SaveBarProvider({ children }: { children: React.ReactNode }) {
  const [slots, setSlots] = useState<Map<string, Slot>>(() => new Map());

  const registry = useMemo<Registry>(
    () => ({
      set: (id, slot) =>
        setSlots((current) => {
          const known = current.get(id);
          if (known && known.dirty === slot.dirty && known.save === slot.save && known.reset === slot.reset)
            return current;
          return new Map(current).set(id, slot);
        }),
      drop: (id) =>
        setSlots((current) => {
          if (!current.has(id)) return current;
          const next = new Map(current);
          next.delete(id);
          return next;
        }),
    }),
    [],
  );

  return (
    <RegistryContext.Provider value={registry}>
      <SlotsContext.Provider value={slots}>{children}</SlotsContext.Provider>
    </RegistryContext.Provider>
  );
}

/** Registers something editable with the page's save bar. Outside a
 *  provider it does nothing, so a section still renders on its own. */
export function useSaveSlot(dirty: boolean, save: () => Promise<boolean>, reset: () => void) {
  const id = useId();
  const registry = useContext(RegistryContext);
  // The latest handlers without re-registering on every render.
  const handlers = useRef({ save, reset });
  useEffect(() => {
    handlers.current = { save, reset };
  });
  const stable = useMemo(
    () => ({
      save: () => handlers.current.save(),
      reset: () => handlers.current.reset(),
    }),
    [],
  );

  useEffect(() => {
    registry?.set(id, { dirty, ...stable });
  }, [registry, id, dirty, stable]);
  useEffect(() => () => registry?.drop(id), [registry, id]);
}

/** What a form would send right now, as one comparable string. */
function snapshot(form: HTMLFormElement): string {
  return JSON.stringify(
    [...new FormData(form)].map(([key, value]) => [
      key,
      typeof value === "string" ? value : `${value.name}:${value.size}`,
    ]),
  );
}

/** A `<form>` whose Save button is the page's bar.
 *
 *  Dirty means "would send something different from what it showed first",
 *  measured on the form's own data — so a custom select that keeps its
 *  value in a hidden input counts, and typing a value back to what it was
 *  clears the bar again. `dirty` adds what the form's data cannot show: rows
 *  kept only in React state.
 *
 *  Reset remounts the form. `form.reset()` restores native inputs only; a
 *  custom select holds its choice in component state and would stay put. */
export function SavedForm({
  onSubmit,
  onReset,
  dirty: extraDirty = false,
  children,
  ...rest
}: Omit<React.ComponentProps<"form">, "onSubmit" | "onReset"> & {
  /** Resolve to `false` when nothing was saved. */
  onSubmit: (event: React.FormEvent<HTMLFormElement>) => Promise<boolean | void>;
  onReset?: () => void;
  dirty?: boolean;
}) {
  const ref = useRef<HTMLFormElement>(null);
  const base = useRef<string | null>(null);
  const [epoch, setEpoch] = useState(0);
  const [touched, setTouched] = useState(false);
  const pending = useRef<((ok: boolean) => void) | null>(null);

  // The baseline is what the form holds right after it mounts.
  useEffect(() => {
    if (ref.current) base.current = snapshot(ref.current);
  }, [epoch]);

  // After the event's own state updates have rendered: a custom control
  // writes its hidden input on the render that follows the click.
  const check = useCallback(() => {
    window.setTimeout(() => {
      if (ref.current && base.current !== null)
        setTouched(snapshot(ref.current) !== base.current);
    }, 0);
  }, []);

  const save = useCallback(() => {
    const form = ref.current;
    // `requestSubmit` fires no event on an invalid form — without this
    // check the promise below would never settle.
    if (!form || !form.reportValidity()) return Promise.resolve(false);
    return new Promise<boolean>((resolve) => {
      pending.current = resolve;
      form.requestSubmit();
    });
  }, []);

  const reset = useCallback(() => {
    onReset?.();
    setTouched(false);
    setEpoch((n) => n + 1);
  }, [onReset]);

  useSaveSlot(touched || extraDirty, save, reset);

  return (
    <form
      {...rest}
      key={epoch}
      ref={ref}
      onInput={check}
      onChange={check}
      onClick={check}
      onKeyUp={check}
      onSubmit={async (event) => {
        event.preventDefault();
        let ok = false;
        try {
          ok = (await onSubmit(event)) !== false;
        } finally {
          if (ok) {
            // What was just saved is the new baseline.
            if (ref.current) base.current = snapshot(ref.current);
            setTouched(false);
          }
          pending.current?.(ok);
          pending.current = null;
        }
      }}
    >
      {children}
    </form>
  );
}

/** The bar itself: shown only while something is unsaved. */
export function SaveBar() {
  const locale = useLocale();
  const slots = useContext(SlotsContext);
  const [busy, setBusy] = useState(false);
  const dirty = [...slots.values()].filter((slot) => slot.dirty);

  // Leaving with unsaved edits asks first; the browser words the question.
  useEffect(() => {
    if (dirty.length === 0) return;
    const warn = (event: BeforeUnloadEvent) => event.preventDefault();
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [dirty.length]);

  if (dirty.length === 0) return null;

  async function saveAll() {
    setBusy(true);
    try {
      // One after another: two sections may write the same record.
      for (const slot of dirty) await slot.save();
    } finally {
      setBusy(false);
    }
  }

  return (
    <div
      role="region"
      data-save-bar
      aria-label={t(locale, "settings.unsaved")}
      className="sticky bottom-4 z-10 flex flex-wrap items-center justify-between gap-3 rw-radius border rw-line rw-surface px-4 py-3 rw-shadow"
    >
      <p className="text-theme-sm font-medium rw-strong" aria-live="polite">
        {fill(t(locale, "settings.unsavedCount"), { count: String(dirty.length) })}
      </p>
      <div className="flex gap-3">
        <Button
          variant="outline"
          disabled={busy}
          onClick={() => dirty.forEach((slot) => slot.reset())}
        >
          {t(locale, "settings.discard")}
        </Button>
        <Button busy={busy} onClick={saveAll}>
          {t(locale, "settings.save")}
        </Button>
      </div>
    </div>
  );
}
