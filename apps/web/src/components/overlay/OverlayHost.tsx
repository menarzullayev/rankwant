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
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import {
  currentOverlayVariant,
  lastOverlayAnchor,
  overlayPlace,
  placeForKind,
  startOverlayAnchors,
  type Box,
  type OverlayKind,
} from "@/lib/theme/overlay";

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
};

export type OverlayApi = {
  confirm: (title: string, options?: ConfirmOptions) => Promise<boolean>;
  openMenu: (
    items: OverlayMenuItem[],
    origin?: HTMLElement | { x: number; y: number },
  ) => void;
  close: () => void;
};

const OverlayContext = createContext<OverlayApi | null>(null);

const FALLBACK: OverlayApi = {
  confirm: async (title) =>
    typeof window !== "undefined" ? window.confirm(title) : false,
  openMenu: () => {},
  close: () => {},
};

export function useOverlay(): OverlayApi {
  return useContext(OverlayContext) ?? FALLBACK;
}

export function useConfirm(): OverlayApi["confirm"] {
  return useOverlay().confirm;
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
): void {
  const variant = currentOverlayVariant();
  if (overlayPlace(variant, kind) !== "anchor") {
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
): {
  bind: (el: HTMLElement | null) => void;
  node: RefObject<HTMLElement | null>;
} {
  const node = useRef<HTMLElement | null>(null);
  const bind = useCallback(
    (el: HTMLElement | null) => {
      node.current = el;
      if (el && open) {
        placePanel(el, kind, origin);
        requestAnimationFrame(() => {
          if (node.current === el) placePanel(el, kind, origin);
        });
      }
    },
    [open, kind, origin],
  );
  useLayoutEffect(() => {
    if (!open || !node.current) return;
    placePanel(node.current, kind, origin);
  }, [open, kind, origin]);
  return { bind, node };
}

type ConfirmState = ConfirmOptions & {
  title: string;
  resolve: (ok: boolean) => void;
};

type MenuState = { items: OverlayMenuItem[]; origin: Box };
type TipState = { text: string; origin: Box };

export function OverlayProvider({ children }: { children: ReactNode }) {
  const locale = useLocale();
  const [confirm, setConfirm] = useState<ConfirmState | null>(null);
  const [menu, setMenu] = useState<MenuState | null>(null);
  const [tip, setTip] = useState<TipState | null>(null);
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
    }),
    [close],
  );

  useEffect(() => {
    let timer = 0;
    let current: HTMLElement | null = null;

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

    function show(el: HTMLElement) {
      const text =
        el.getAttribute("data-tip") ||
        el.getAttribute("title") ||
        el.getAttribute("data-tip-restore") ||
        "";
      if (!text.trim()) return;
      if (el.hasAttribute("title")) {
        el.setAttribute("data-tip-restore", el.getAttribute("title") ?? "");
        el.removeAttribute("title");
      }
      current = el;
      setTip({ text, origin: originBox(el) });
    }

    function onOver(event: PointerEvent) {
      if (blocking) return;
      const el = source(event.target);
      if (!el) return;
      if (el === current) return;
      hide();
      timer = window.setTimeout(() => show(el), 180);
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
    document.addEventListener("pointerout", onOut, true);
    document.addEventListener("focusin", onFocus, true);
    document.addEventListener("focusout", onBlur, true);
    return () => {
      window.clearTimeout(timer);
      restore(current);
      document.removeEventListener("pointerover", onOver, true);
      document.removeEventListener("pointerout", onOut, true);
      document.removeEventListener("focusin", onFocus, true);
      document.removeEventListener("focusout", onBlur, true);
    };
  }, [blocking]);

  const cancelLabel = confirm?.cancelLabel ?? t(locale, "admin.cancel");
  const confirmLabel =
    confirm?.confirmLabel ??
    (confirm?.danger ? t(locale, "admin.delete") : t(locale, "common.yes"));

  return (
    <OverlayContext.Provider value={api}>
      {children}
      <div id="rw-overlay-layer" data-ov-skip>
        {tip && !blocking ? (
          <OverlayTip text={tip.text} origin={tip.origin} />
        ) : null}
        <ConfirmDialog
          open={Boolean(confirm)}
          title={confirm?.title ?? ""}
          body={confirm?.body}
          cancelLabel={cancelLabel}
          confirmLabel={confirmLabel}
          danger={Boolean(confirm?.danger)}
          onCancel={() => {
            confirm?.resolve(false);
            setConfirm(null);
          }}
          onOk={() => {
            confirm?.resolve(true);
            setConfirm(null);
          }}
        />
        {menu ? (
          <OverlayMenu
            items={menu.items}
            origin={menu.origin}
            onClose={() => setMenu(null)}
          />
        ) : null}
      </div>
    </OverlayContext.Provider>
  );
}

function OverlayTip({ text, origin }: { text: string; origin: Box }) {
  const { bind } = usePlacedPanel(true, "tip", origin);
  return (
    <div
      ref={bind}
      className="rw-ov-tip"
      role="tooltip"
      style={{ left: origin.left, top: Math.max(8, origin.top - 36) }}
    >
      {text}
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
  onCancel,
  onOk,
}: {
  open: boolean;
  title: string;
  body?: string;
  cancelLabel: string;
  confirmLabel: string;
  danger: boolean;
  onCancel: () => void;
  onOk: () => void;
}) {
  const { bind } = usePlacedPanel(open, "confirm");
  return (
    <Dialog open={open} onClose={onCancel} className="relative z-[80]">
      <DialogBackdrop className="rw-ov-scrim" />
      <DialogPanel ref={bind} className="rw-ov-panel">
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
