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

import { useToast } from "@/components/overlay/OverlayHost";
import { Button } from "@/components/ui/Button";
import { Status } from "@/components/ui/Status";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import { isOn } from "@/lib/flags";
import { shownDirty, startAll } from "../save-queue";

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

/** Optimistic saves in flight (`optimisticSave` flag) and the last outcome.
 *
 *  `notice` is what the bar says once it has nothing left to ask for:
 *  "saved" right after the click (the optimism), "failed" when the server
 *  turned a write down — that replaces "saved" and brings the bar back. */
type Flight = {
  inFlight: ReadonlySet<string>;
  notice: "saved" | "failed" | null;
  start: (entries: [string, Slot][]) => void;
  dismiss: () => void;
};

const RegistryContext = createContext<Registry | null>(null);
const SlotsContext = createContext<Map<string, Slot>>(new Map());
const FlightContext = createContext<Flight | null>(null);

/** How long the optimistic "Saved" stays up when nothing goes wrong. */
const SAVED_NOTICE_MS = 2500;

/** Holds every slot of the page and draws one bar for all of them
 *  (decision of 2026-10-05).
 *
 *  Before this each card had its own Save button — two on the longest page
 *  — and pressing one left the other card's edits behind without a word.
 *  Actions that are not "edit, then save" keep their own button: changing
 *  the password, the username, joining a team. */
export function SaveBarProvider({ children }: { children: React.ReactNode }) {
  const locale = useLocale();
  const toast = useToast();
  const [slots, setSlots] = useState<Map<string, Slot>>(() => new Map());
  const [inFlight, setInFlight] = useState<ReadonlySet<string>>(() => new Set());
  const [notice, setNotice] = useState<Flight["notice"]>(null);
  // Read when a save settles, possibly after this page has gone: a refusal
  // nobody can see on the page goes to the site-wide toast instead.
  const mounted = useRef(true);
  const registered = useRef(new Set<string>());
  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
    };
  }, []);

  useEffect(() => {
    if (notice !== "saved") return;
    const timer = window.setTimeout(
      () => setNotice((current) => (current === "saved" ? null : current)),
      SAVED_NOTICE_MS,
    );
    return () => window.clearTimeout(timer);
  }, [notice]);

  const flight = useMemo<Flight>(
    () => ({
      inFlight,
      notice,
      start: (entries) => {
        setInFlight((current) => new Set([...current, ...entries.map(([id]) => id)]));
        setNotice("saved");
        void startAll(
          entries.map(([id, slot]) => ({ id, save: slot.save })),
          (id, ok) => {
            setInFlight((current) => {
              const next = new Set(current);
              next.delete(id);
              return next;
            });
            if (ok) return;
            // Rollback: the optimistic "Saved" is withdrawn and the slot,
            // still dirty, brings the bar back with the edits in place.
            setNotice("failed");
            // The page or the section is gone (the person moved on): the
            // edits went with it, so say so where it is still seen.
            if (!mounted.current || !registered.current.has(id))
              toast(t(locale, "settings.saveFailedGone"));
          },
        );
      },
      dismiss: () => setNotice(null),
    }),
    [inFlight, notice, locale, toast],
  );

  const registry = useMemo<Registry>(
    () => ({
      set: (id, slot) => {
        registered.current.add(id);
        setSlots((current) => {
          const known = current.get(id);
          if (known && known.dirty === slot.dirty && known.save === slot.save && known.reset === slot.reset)
            return current;
          return new Map(current).set(id, slot);
        });
      },
      drop: (id) => {
        registered.current.delete(id);
        setSlots((current) => {
          if (!current.has(id)) return current;
          const next = new Map(current);
          next.delete(id);
          return next;
        });
      },
    }),
    [],
  );

  return (
    <RegistryContext.Provider value={registry}>
      <SlotsContext.Provider value={slots}>
        <FlightContext.Provider value={flight}>{children}</FlightContext.Provider>
      </SlotsContext.Provider>
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
        // What leaves now is what the server will hold. Typing on while the
        // request is out must stay unsaved — with an optimistic save the
        // form is never locked, so the snapshot cannot be taken later.
        const sent = snapshot(event.currentTarget);
        let ok = false;
        try {
          ok = (await onSubmit(event)) !== false;
        } finally {
          if (ok) {
            // What was just saved is the new baseline.
            base.current = sent;
            setTouched(ref.current ? snapshot(ref.current) !== sent : false);
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

const NO_FLIGHT: ReadonlySet<string> = new Set();

/** The bar itself: shown only while something is unsaved.
 *
 *  With the `optimisticSave` flag the click does not wait for the server:
 *  the bar steps aside at once and says "Saved", the requests go out
 *  together, and a refusal brings it back with the edits still in their
 *  fields and an alert in place of "Saved". Without the flag it saves one
 *  section after another and holds the button busy until the last reply. */
export function SaveBar() {
  const locale = useLocale();
  const slots = useContext(SlotsContext);
  const flight = useContext(FlightContext);
  const [busy, setBusy] = useState(false);
  const inFlight = flight?.inFlight ?? NO_FLIGHT;
  const shown = shownDirty(slots, inFlight);
  const dirty = shown.map(([, slot]) => slot);

  // Leaving with unsaved edits asks first; the browser words the question.
  // A request still out counts too: a full unload would cancel it.
  const holding = dirty.length + inFlight.size;
  useEffect(() => {
    if (holding === 0) return;
    const warn = (event: BeforeUnloadEvent) => event.preventDefault();
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [holding]);

  if (dirty.length === 0) {
    if (flight?.notice !== "saved") return null;
    return (
      <div className="sticky bottom-4 z-10 flex justify-end">
        <div className="rw-radius border rw-line rw-surface px-4 py-3 rw-shadow">
          {/* `iconText`, not the style's responsive default: on a phone that is a
              bare circle, and this line must be read. */}
          <Status status="ok" variant="iconText" live label={t(locale, "settings.saved")} />
        </div>
      </div>
    );
  }

  async function saveAll() {
    // Read at the click, not at render: the flag changes nothing the server
    // drew, so the page hydrates the same either way.
    if (flight && isOn("optimisticSave")) {
      flight.start(shown);
      return;
    }
    flight?.dismiss();
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
      {/* `min-w-0` + a basis: the alert line wraps inside the bar instead of
          pushing it past a 320 px screen (measured: 449 px before). */}
      <div className="flex min-w-0 flex-1 basis-48 flex-col gap-1">
        <p className="text-theme-sm font-medium rw-strong" aria-live="polite">
          {fill(t(locale, "settings.unsavedCount"), { count: String(dirty.length) })}
        </p>
        {flight?.notice === "failed" && (
          // Always words, never the phone's bare circle: an error
          // must be read, and the circle drops `role="alert"`.
          <Status
            status="bad"
            variant="iconText"
            alert
            label={t(locale, "settings.saveFailed")}
            className="rw-status-wrap"
          />
        )}
      </div>
      <div className="flex gap-3">
        <Button
          variant="outline"
          disabled={busy}
          onClick={() => {
            flight?.dismiss();
            dirty.forEach((slot) => slot.reset());
          }}
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
