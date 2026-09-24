"use client";

import { EmptyState } from "@/components/ui/EmptyState";
import { Loading } from "@/components/ui/Loading";
import { Status } from "@/components/ui/Status";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, t } from "@/i18n/messages";
import { ApiError } from "@/lib/api";

/** Ma'lumot holatining yagona shoxlanishi — `loading → error → empty → data`.
 *
 *  Nega global: bu **to'rt holat har bir ro'yxat sahifasida takrorlanadi**.
 *  Har marta `if (loading) … if (error) … if (!data.length) …` yozilsa,
 *  uchta narsa buziladi:
 *
 *  1. **Tartib.** Xato va bo'sh holat bir vaqtda rost bo'lishi mumkin
 *     (`data = []` + `error`) — qaysi biri ustun? Har sahifa o'zicha
 *     hal qilsa, ba'zi joyda «ma'lumot yo'q», ba'zisida xato chiqadi.
 *     Bu yerda tartib qat'iy: **xato > bo'sh > ma'lumot**.
 *  2. **Matn.** Xato kodi (`not_found`, `rate_limited`) tarjima qilinmay
 *     qoladi, ya'ni foydalanuvchi inglizcha kod ko'radi.
 *  3. **Chizish.** `Loading` 10 variant, `EmptyState` 3 variant — har
 *     chaqiruvchi to'g'ri juftlikni tanlashi kerak.
 *
 *  ```tsx
 *  const { data, error, reload } = useLoad<Item[]>("/items/");
 *  return (
 *    <DataState data={data} error={error} onRetry={reload} empty={{title: …}}>
 *      {(items) => items.map((i) => <Row key={i.id} item={i} />)}
 *    </DataState>
 *  );
 *  ```
 *
 *  ⚠️ `empty` berilmasa bo'sh ro'yxat **xato emas** — `data` qaytariladi
 *  va chaqiruvchi o'zi chizadi. Bu ataylab: ba'zi sahifalarda bo'sh
 *  holat jadval sarlavhasi ichida ko'rinishi kerak.
 */
export function DataState<T>({
  data,
  error,
  loading = false,
  onRetry,
  empty,
  loadingVariant = "skeleton",
  className = "",
  children,
}: {
  /** Ma'lumot. `null` — hali kelmagan. */
  data: T | null;
  /** Xato matni yoki `unknown` (ApiError bo'lsa kod bo'yicha tarjima). */
  error?: string | unknown;
  /** Majburiy kutish holati (masalan qayta yuklash paytida). */
  loading?: boolean;
  /** Xato ekranidagi «Qayta urinish» tugmasi. Berilmasa tugma yo'q. */
  onRetry?: () => void;
  /** Bo'sh holat tavsifi. Berilmasa bo'sh ro'yxat `children` ga o'tadi. */
  empty?: {
    /** Nima bo'ldi — qisqa sarlavha. */
    title: string;
    /** Endi nima qilaman. */
    hint?: string;
    /** `EMPTY_ICONS` kaliti — sahifa o'zi ikonka o'ylab topmasin. */
    icon?: string;
    action?: { label: string; href?: string; onClick?: () => void };
  };
  /** Kutish ko'rinishi. Jadval uchun `skeleton`, karta uchun `ring`. */
  loadingVariant?: "skeleton" | "ring" | "spinner" | "shimmer" | "dotsBounce";
  className?: string;
  /** Ma'lumot tayyor bo'lganda chaqiriladi. `null` bo'lmaydi. */
  children: (data: T) => React.ReactNode;
}) {
  const locale = useLocale();

  if (loading && data === null) {
    return (
      <div className={className}>
        <Loading variant={loadingVariant} lines={5} block />
      </div>
    );
  }

  if (error) {
    const text = errorText2(locale, error);
    return (
      <div className={className}>
        <Status status="bad" variant="soft" label={text} alert />
        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="rw-dim-2 rw-hover-bg mt-2 rw-radius-sm px-3 py-1.5 text-theme-sm"
          >
            {t(locale, "error.retry")}
          </button>
        )}
      </div>
    );
  }

  if (data === null) {
    return (
      <div className={className}>
        <Loading variant={loadingVariant} lines={5} block />
      </div>
    );
  }

  if (empty && isEmpty(data)) {
    return (
      <div className={className}>
        <EmptyState
          variant="card"
          icon={empty.icon ?? "empty"}
          title={empty.title}
          hint={empty.hint}
          action={empty.action}
        />
      </div>
    );
  }

  return <>{children(data)}</>;
}

/** Bo'sh ro'yxatni aniqlaydi — massiv yoki `{results: []}` (DRF sahifalash). */
function isEmpty(value: unknown): boolean {
  if (Array.isArray(value)) return value.length === 0;
  if (value && typeof value === "object" && "results" in value) {
    const results = (value as { results?: unknown }).results;
    return Array.isArray(results) && results.length === 0;
  }
  return false;
}

/** Xato matnini yagona joyda tayyorlaydi.
 *
 *  `ApiError` bo'lsa — kod bo'yicha tarjima (`errorText`), notanish bo'lsa
 *  umumiy xabar. Satr berilsa — o'zi qaytadi (chaqiruvchi allaqachon
 *  `describeError` qilgan bo'lishi mumkin). */
function errorText2(locale: Parameters<typeof errorText>[0], error: unknown): string {
  if (typeof error === "string") return error;
  if (error instanceof ApiError) {
    return error.code === "invalid"
      ? error.text
      : errorText(locale, error.code, error.text);
  }
  return t(locale, "error.error");
}
