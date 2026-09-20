"use client";

import {
  Dialog,
  DialogBackdrop,
  DialogPanel,
  DialogTitle,
} from "@headlessui/react";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
  type RefObject,
} from "react";

import { Icon } from "@/components/ui/Icon";
import { HoldButton } from "@/components/kit/ConfirmExtras";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { clampTipKind, type ConfirmKind, type TipKind } from "@/lib/theme/kit";
import {
  currentOverlayVariant,
  lastOverlayAnchor,
  overlayPlace,
  placeForKind,
  placeTip,
  startOverlayAnchors,
  type Box,
  type OverlayKind,
} from "@/lib/theme/overlay";

const CONFIRM_MODAL: ConfirmKind = "modal";
const CONFIRM_POPOVER: ConfirmKind = "popover";
const CONFIRM_HOLD: ConfirmKind = "hold";
const CONFIRM_CMDK: ConfirmKind = "cmdk";

export type OverlayMenuItem = {
  id: string;
  label: string;
  danger?: boolean;
  onSelect: () => void;
};

export type ConfirmOptions = {
  body?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  danger?: boolean;
  kind?: Exclude<ConfirmKind, "inline">;
  origin?: HTMLElement | { x: number; y: number };
  holdMs?: number;
};

export type OverlayApi = {
  confirm: (title: string, options?: ConfirmOptions) => Promise<boolean>;
  openMenu: (
    items: OverlayMenuItem[],
    origin?: HTMLElement | { x: number; y: number },
  ) => void;
  close: () => void;
  toast: (message: string) => void;
};

const OverlayContext = createContext<OverlayApi | null>(null);

const FALLBACK: OverlayApi = {
  confirm: async (title) =>
    typeof window !== "undefined" ? window.confirm(title) : false,
  openMenu: () => {},
  close: () => {},
  toast: () => {},
};

export function useOverlay(): OverlayApi {
  return useContext(OverlayContext) ?? FALLBACK;
}

export function useConfirm(): OverlayApi["confirm"] {
  return useOverlay().confirm;
}

export function useToast(): OverlayApi["toast"] {
  return useOverlay().toast;
}

function originBox(
  origin?: HTMLElement | { x: number; y: number } | null,
): Box {
  if (origin instanceof HTMLElement) {
    const r = origin.getBoundingClientRect();
    return {
      left: r.left,
      top: r.top,
      right: r.right,
      bottom: r.bottom,
      width: r.width,
      height: r.height,
    };
  }
  if (origin && "x" in origin) {
    return {
      left: origin.x,
      top: origin.y,
      right: origin.x,
      bottom: origin.y,
      width: 0,
      height: 0,
    };
  }
  return lastOverlayAnchor();
}

function placePanel(
  el: HTMLElement,
  kind: OverlayKind,
  origin?: Box | null,
  forceAnchor = false,
): void {
  const variant = currentOverlayVariant();
  if (!forceAnchor && overlayPlace(variant, kind) !== "anchor") {
    el.style.removeProperty("left");
    el.style.removeProperty("top");
    el.style.removeProperty("transform");
    return;
  }
  const size = el.getBoundingClientRect();
  const pos = placeForKind(
    kind,
    origin ?? lastOverlayAnchor(),
    size,
    { width: window.innerWidth, height: window.innerHeight },
  );
  el.style.left = `${pos.x}px`;
  el.style.top = `${pos.y}px`;
  el.style.transform = "none";
}

function usePlacedPanel(
  open: boolean,
  kind: OverlayKind,
  origin?: Box | null,
  forceAnchor = false,
): {
  bind: (el: HTMLElement | null) => void;
  node: RefObject<HTMLElement | null>;
} {
  const node = useRef<HTMLElement | null>(null);
  const bind = useCallback(
    (el: HTMLElement | null) => {
      node.current = el;
      if (el && open) {
        placePanel(el, kind, origin, forceAnchor);
        requestAnimationFrame(() => {
          if (node.current === el) placePanel(el, kind, origin, forceAnchor);
        });
      }
    },
    [open, kind, origin, forceAnchor],
  );
  useLayoutEffect(() => {
    if (!open || !node.current) return;
    placePanel(node.current, kind, origin, forceAnchor);
  }, [open, kind, origin, forceAnchor]);
  return { bind, node };
}

type ConfirmState = ConfirmOptions & {
  title: string;
  resolve: (ok: boolean) => void;
};

type MenuState = { items: OverlayMenuItem[]; origin: Box };
type TipState = {
  text: string;
  title?: string;
  kbd?: string;
  kind: TipKind;
  origin: Box;
  follow?: { x: number; y: number };
};

export function OverlayProvider({ children }: { children: ReactNode }) {
  const locale = useLocale();
  const [confirm, setConfirm] = useState<ConfirmState | null>(null);
  const [menu, setMenu] = useState<MenuState | null>(null);
  const [tip, setTip] = useState<TipState | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const blocking = Boolean(confirm || menu);

  useEffect(() => startOverlayAnchors(), []);

  const close = useCallback(() => {
    setConfirm((prev) => {
      prev?.resolve(false);
      return null;
    });
    setMenu(null);
    setTip(null);
  }, []);

  const api = useMemo<OverlayApi>(
    () => ({
      confirm: (title, options) =>
        new Promise((resolve: (ok: boolean) => void) => {
          setTip(null);
          setMenu(null);
          setConfirm({ title, ...options, resolve });
        }),
      openMenu: (items, origin) => {
        setTip(null);
        setConfirm((prev) => {
          prev?.resolve(false);
          return null;
        });
        setMenu({ items, origin: originBox(origin) });
      },
      close,
      toast: (message) => {
        setToast(message);
      },
    }),
    [close],
  );

  useEffect(() => {
    if (!toast) return;
    const id = window.setTimeout(() => setToast(null), 1800);
    return () => window.clearTimeout(id);
  }, [toast]);

  useEffect(() => {
    let timer = 0;
    let current: HTMLElement | null = null;
    let follow = false;

    function restore(el: HTMLElement | null) {
      if (!el) return;
      const saved = el.getAttribute("data-tip-restore");
      if (saved !== null) {
        el.setAttribute("title", saved);
        el.removeAttribute("data-tip-restore");
      }
    }

    function hide() {
      window.clearTimeout(timer);
      restore(current);
      current = null;
      follow = false;
      setTip(null);
    }

    function source(target: EventTarget | null): HTMLElement | null {
      if (!(target instanceof Element)) return null;
      const el = target.closest("[title], [data-tip]");
      if (!(el instanceof HTMLElement)) return null;
      if (el.closest("#rw-overlay-layer, #rw-chiziq-layer, [data-ov-skip]")) {
        return null;
      }
      return el;
    }

    function kindOf(el: HTMLElement): TipKind {
      if (el.hasAttribute("data-tip-follow")) return "follow";
      if (el.hasAttribute("data-tip-title")) return "rich";
      if (el.hasAttribute("data-tip-kbd")) return "kbd";
      return clampTipKind(el.getAttribute("data-tip-kind"));
    }

    function show(el: HTMLElement, pointer?: { x: number; y: number }) {
      const text =
        el.getAttribute("data-tip") ||
        el.getAttribute("title") ||
        el.getAttribute("data-tip-restore") ||
        "";
      if (!text.trim() && kindOf(el) !== "skeleton") return;
      if (el.hasAttribute("title")) {
        el.setAttribute("data-tip-restore", el.getAttribute("title") ?? "");
        el.removeAttribute("title");
      }
      current = el;
      const kind = kindOf(el);
      follow = kind === "follow" || el.hasAttribute("data-tip-follow");
      setTip({
        text,
        title: el.getAttribute("data-tip-title") ?? undefined,
        kbd: el.getAttribute("data-tip-kbd") ?? undefined,
        kind,
        origin: originBox(el),
        follow: follow && pointer ? pointer : undefined,
      });
    }

    function onOver(event: PointerEvent) {
      if (blocking) return;
      const el = source(event.target);
      if (!el) return;
      if (el === current) return;
      hide();
      timer = window.setTimeout(
        () => show(el, { x: event.clientX, y: event.clientY }),
        180,
      );
    }

    function onMove(event: PointerEvent) {
      if (!follow || !current) return;
      setTip((prev) =>
        prev
          ? { ...prev, follow: { x: event.clientX, y: event.clientY } }
          : prev,
      );
    }

    function onOut(event: PointerEvent) {
      const el = source(event.target);
      const next = source(event.relatedTarget);
      if (el && next === el) return;
      if (el === current || !source(event.relatedTarget)) hide();
    }

    function onFocus(event: FocusEvent) {
      if (blocking) return;
      const el = source(event.target);
      if (!el) return;
      hide();
      timer = window.setTimeout(() => show(el), 180);
    }

    function onBlur(event: FocusEvent) {
      if (source(event.relatedTarget)) return;
      hide();
    }

    document.addEventListener("pointerover", onOver, true);
    document.addEventListener("pointermove", onMove, true);
    document.addEventListener("pointerout", onOut, true);
    document.addEventListener("focusin", onFocus, true);
    document.addEventListener("focusout", onBlur, true);
    return () => {
      window.clearTimeout(timer);
      restore(current);
      document.removeEventListener("pointerover", onOver, true);
      document.removeEventListener("pointermove", onMove, true);
      document.removeEventListener("pointerout", onOut, true);
      document.removeEventListener("focusin", onFocus, true);
      document.removeEventListener("focusout", onBlur, true);
    };
  }, [blocking]);

  const cancelLabel = confirm?.cancelLabel ?? t(locale, "admin.cancel");
  const confirmLabel =
    confirm?.confirmLabel ??
    (confirm?.danger ? t(locale, "admin.delete") : t(locale, "common.yes"));
  const kind = confirm?.kind ?? CONFIRM_MODAL;
  const origin = confirm ? originBox(confirm.origin) : null;

  function finish(ok: boolean) {
    confirm?.resolve(ok);
    setConfirm(null);
  }

  return (
    <OverlayContext.Provider value={api}>
      {children}
      <div id="rw-overlay-layer" data-ov-skip>
        {tip && !blocking ? (
          <OverlayTip
            text={tip.text}
            title={tip.title}
            kbd={tip.kbd}
            kind={tip.kind}
            origin={tip.origin}
            follow={tip.follow}
          />
        ) : null}
        <ConfirmDialog
          open={Boolean(confirm) && kind === CONFIRM_MODAL}
          title={confirm?.title ?? ""}
          body={confirm?.body}
          cancelLabel={cancelLabel}
          confirmLabel={confirmLabel}
          danger={Boolean(confirm?.danger)}
          onCancel={() => finish(false)}
          onOk={() => finish(true)}
        />
        <ConfirmDialog
          open={Boolean(confirm) && kind === CONFIRM_POPOVER}
          title={confirm?.title ?? ""}
          body={confirm?.body}
          cancelLabel={cancelLabel}
          confirmLabel={confirmLabel}
          danger={Boolean(confirm?.danger)}
          popover
          origin={origin}
          onCancel={() => finish(false)}
          onOk={() => finish(true)}
        />
        <HoldConfirmDialog
          open={Boolean(confirm) && kind === CONFIRM_HOLD}
          title={confirm?.title ?? ""}
          body={confirm?.body}
          confirmLabel={confirmLabel}
          cancelLabel={cancelLabel}
          danger={Boolean(confirm?.danger)}
          holdMs={confirm?.holdMs ?? 900}
          onCancel={() => finish(false)}
          onOk={() => finish(true)}
        />
        <CmdkConfirm
          open={Boolean(confirm) && kind === CONFIRM_CMDK}
          title={confirm?.title ?? ""}
          confirmLabel={confirmLabel}
          cancelLabel={cancelLabel}
          danger={Boolean(confirm?.danger)}
          onCancel={() => finish(false)}
          onOk={() => finish(true)}
        />
        {menu ? (
          <OverlayMenu
            items={menu.items}
            origin={menu.origin}
            onClose={() => setMenu(null)}
          />
        ) : null}
        {toast ? (
          <div className="rw-kit-toast" role="status">
            {toast}
          </div>
        ) : null}
      </div>
    </OverlayContext.Provider>
  );
}

function OverlayTip({
  text,
  title,
  kbd,
  kind,
  origin,
  follow,
}: {
  text: string;
  title?: string;
  kbd?: string;
  kind: TipKind;
  origin: Box;
  follow?: { x: number; y: number };
}) {
  const node = useRef<HTMLDivElement | null>(null);
  useLayoutEffect(() => {
    const el = node.current;
    if (!el) return;
    const size = el.getBoundingClientRect();
    const viewport = { width: window.innerWidth, height: window.innerHeight };
    let mode: "follow" | "flip" | "anchor" = "anchor";
    if (follow) mode = "follow";
    else if (kind === "flip") mode = "flip";
    const pos = placeTip(mode, origin, size, viewport, follow);
    el.style.left = `${pos.x}px`;
    el.style.top = `${pos.y}px`;
    el.dataset.tipSide = pos.side;
  }, [kind, origin, follow, text, title, kbd]);
  return (
    <div
      ref={node}
      className="rw-ov-tip"
      data-kit-tip={kind}
      role="tooltip"
    >
      {kind === "skeleton" ? (
        <span className="rw-kit-skel">
          <i />
          <i />
          <i />
        </span>
      ) : (
        <>
          {title ? <strong className="rw-kit-tip-h">{title}</strong> : null}
          {text ? <span>{text}</span> : null}
          {kbd ? <kbd className="rw-kit-kbd">{kbd}</kbd> : null}
        </>
      )}
    </div>
  );
}

function ConfirmDialog({
  open,
  title,
  body,
  cancelLabel,
  confirmLabel,
  danger,
  popover,
  origin,
  onCancel,
  onOk,
}: {
  open: boolean;
  title: string;
  body?: string;
  cancelLabel: string;
  confirmLabel: string;
  danger: boolean;
  popover?: boolean;
  origin?: Box | null;
  onCancel: () => void;
  onOk: () => void;
}) {
  const { bind } = usePlacedPanel(open, "confirm", origin, Boolean(popover));
  let confirmChrome = CONFIRM_MODAL;
  if (popover) confirmChrome = CONFIRM_POPOVER;
  return (
    <Dialog open={open} onClose={onCancel} className="relative z-[80]">
      <DialogBackdrop className={popover ? "rw-ov-scrim opacity-0" : "rw-ov-scrim"} />
      <DialogPanel
        ref={bind}
        className="rw-ov-panel"
        data-kit-confirm={confirmChrome}
      >
        <DialogTitle className="rw-ov-title">{title}</DialogTitle>
        {body ? <p className="rw-ov-copy">{body}</p> : null}
        <div className="rw-ov-acts">
          <button type="button" className="rw-ov-btn" onClick={onCancel}>
            {cancelLabel}
          </button>
          <button
            type="button"
            className={`rw-ov-btn rw-ov-go${danger ? " is-danger" : ""}`}
            onClick={onOk}
          >
            {confirmLabel}
          </button>
        </div>
      </DialogPanel>
    </Dialog>
  );
}

function HoldConfirmDialog({
  open,
  title,
  body,
  confirmLabel,
  cancelLabel,
  danger,
  holdMs,
  onCancel,
  onOk,
}: {
  open: boolean;
  title: string;
  body?: string;
  confirmLabel: string;
  cancelLabel: string;
  danger: boolean;
  holdMs: number;
  onCancel: () => void;
  onOk: () => void;
}) {
  const { bind } = usePlacedPanel(open, "confirm");
  return (
    <Dialog open={open} onClose={onCancel} className="relative z-[80]">
      <DialogBackdrop className="rw-ov-scrim" />
      <DialogPanel ref={bind} className="rw-ov-panel" data-kit-confirm="hold">
        <DialogTitle className="rw-ov-title">{title}</DialogTitle>
        {body ? <p className="rw-ov-copy">{body}</p> : null}
        <div className="mt-3 grid gap-2">
          <HoldButton
            label={confirmLabel}
            danger={danger}
            holdMs={holdMs}
            onConfirm={onOk}
          />
          <button type="button" className="rw-ov-btn" onClick={onCancel}>
            {cancelLabel}
          </button>
        </div>
      </DialogPanel>
    </Dialog>
  );
}

function CmdkConfirm({
  open,
  title,
  confirmLabel,
  cancelLabel,
  danger,
  onCancel,
  onOk,
}: {
  open: boolean;
  title: string;
  confirmLabel: string;
  cancelLabel: string;
  danger: boolean;
  onCancel: () => void;
  onOk: () => void;
}) {
  const { bind } = usePlacedPanel(open, "confirm");
  return (
    <Dialog open={open} onClose={onCancel} className="relative z-[80]">
      <DialogBackdrop className="rw-ov-scrim" />
      {open ? (
        <CmdkConfirmBody
          bind={bind}
          title={title}
          confirmLabel={confirmLabel}
          cancelLabel={cancelLabel}
          danger={danger}
          onCancel={onCancel}
          onOk={onOk}
        />
      ) : null}
    </Dialog>
  );
}

function CmdkConfirmBody({
  bind,
  title,
  confirmLabel,
  cancelLabel,
  danger,
  onCancel,
  onOk,
}: {
  bind: (el: HTMLElement | null) => void;
  title: string;
  confirmLabel: string;
  cancelLabel: string;
  danger: boolean;
  onCancel: () => void;
  onOk: () => void;
}) {
  const locale = useLocale();
  const [q, setQ] = useState("");
  const [sel, setSel] = useState(0);
  const items = [
    { id: "ok", label: confirmLabel, run: onOk, danger },
    { id: "no", label: cancelLabel, run: onCancel, danger: false },
  ];
  const needle = q.trim().toLocaleLowerCase();
  const shown = items.filter((item) =>
    needle ? item.label.toLocaleLowerCase().includes(needle) : true,
  );
  const current = shown[Math.min(sel, Math.max(0, shown.length - 1))];

  return (
    <DialogPanel ref={bind} className="rw-ov-panel" data-kit-confirm="cmdk">
      <DialogTitle className="rw-ov-title">{title}</DialogTitle>
      <input
        autoFocus
        className="rw-kit-cmdk-in"
        value={q}
        placeholder={t(locale, "kit.cmdkPlaceholder")}
        onChange={(event) => {
          setQ(event.target.value);
          setSel(0);
        }}
        onKeyDown={(event) => {
          if (event.key === "ArrowDown") {
            event.preventDefault();
            setSel((i) => Math.min(shown.length - 1, i + 1));
          } else if (event.key === "ArrowUp") {
            event.preventDefault();
            setSel((i) => Math.max(0, i - 1));
          } else if (event.key === "Enter" && current) {
            event.preventDefault();
            current.run();
          }
        }}
      />
      <div className="rw-kit-cmdk-list" role="listbox">
        {shown.map((item, i) => (
          <button
            key={item.id}
            type="button"
            role="option"
            aria-selected={item === current}
            className={item.danger ? "is-danger" : undefined}
            onMouseEnter={() => setSel(i)}
            onClick={item.run}
          >
            {item.label}
          </button>
        ))}
      </div>
    </DialogPanel>
  );
}

function OverlayMenu({
  items,
  origin,
  onClose,
}: {
  items: OverlayMenuItem[];
  origin: Box;
  onClose: () => void;
}) {
  const { bind, node } = usePlacedPanel(true, "menu", origin);
  const variant = currentOverlayVariant();
  const centred = overlayPlace(variant, "menu") === "center";

  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
      }
    }
    function onDown(event: PointerEvent) {
      const target = event.target;
      if (target instanceof Node && node.current?.contains(target)) return;
      onClose();
    }
    document.addEventListener("keydown", onKey);
    document.addEventListener("pointerdown", onDown, true);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.removeEventListener("pointerdown", onDown, true);
    };
  }, [onClose, node]);

  return (
    <>
      {centred ? (
        <div className="rw-ov-scrim" onClick={onClose} />
      ) : null}
      <div ref={bind} className="rw-ov-menu" role="menu">
        {items.map((item) => (
          <button
            key={item.id}
            type="button"
            role="menuitem"
            className={item.danger ? "is-danger" : undefined}
            onClick={() => {
              onClose();
              item.onSelect();
            }}
          >
            {item.label}
          </button>
        ))}
      </div>
    </>
  );
}

export function OverlayDialog({
  open,
  onClose,
  title,
  children,
  footer,
}: {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  footer?: ReactNode;
}) {
  const locale = useLocale();
  const { bind } = usePlacedPanel(open, "modal");
  return (
    <Dialog open={open} onClose={onClose} className="relative z-[80]">
      <DialogBackdrop className="rw-ov-scrim" />
      <DialogPanel ref={bind} className="rw-ov-panel">
        <div className="rw-ov-head">
          <DialogTitle className="rw-ov-title">{title}</DialogTitle>
          <button
            type="button"
            className="rw-ov-x"
            onClick={onClose}
            aria-label={t(locale, "nav.close")}
          >
            <Icon name="nav.close" />
          </button>
        </div>
        <div className="rw-ov-body">{children}</div>
        {footer ? <div className="rw-ov-acts">{footer}</div> : null}
      </DialogPanel>
    </Dialog>
  );
}
