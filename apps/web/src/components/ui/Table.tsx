/** TailAdmin jadval patterni.
 *
 * `<table>` va `<tbody>` saqlanadi: E2E `tbody tr a` va `table`
 * selektorlariga tayanadi (tests/e2e/specs). */
export function Table({ children }: { children: React.ReactNode }) {
  return (
    // `min-w-0` bo'lmasa `overflow-x-auto` ISHLAMAYDI: grid yoki flex
    // ichidagi element standart `min-width: auto` bilan mazmunidan
    // kichrayolmaydi va jadval o'zi emas, BUTUN SAHIFA siljiydi.
    // O'lchandi: 412 px li telefonda arxiv 629 px bo'lib ketardi.
    <div className="custom-scrollbar min-w-0 overflow-x-auto">
      <table className="min-w-full text-left">{children}</table>
    </div>
  );
}

export function THead({ children }: { children: React.ReactNode }) {
  return (
    <thead className="border-b rw-divider">
      <tr>{children}</tr>
    </thead>
  );
}

export function TH({
  children,
  align = "left",
  className = "",
}: {
  children: React.ReactNode;
  align?: "left" | "right" | "center";
  className?: string;
}) {
  return (
    <th
      className={`px-4 py-3 text-theme-xs font-medium rw-dim uppercase 
 ${align === "right" ? "text-right" : align === "center" ? "text-center" : "text-left"} ${className}`}
    >
      {children}
    </th>
  );
}

/** Saralash yo'nalishi. Alohida tip — `direction?: "asc" | "desc"` deb
 *  yozilsa `check_hardcoded.py` uni ternary deb o'qib qoladi (u `?` va
 *  `|` ni ko'radi), ya'ni tekshiruv yolg'on qizaradi. */
export type SortDirection = "asc" | "desc";

/** `aria-sort` qiymatlari — ARIA standarti, tarjima qilinmaydi. Jadval
 *  sifatida saqlanadi: ternary ichida literal qolsa tekshiruv uni matn
 *  deb hisoblaydi. */
const ARIA_SORT: Record<SortDirection, "ascending" | "descending"> = {
  asc: "ascending",
  desc: "descending",
};

/** Saralanadigan ustun sarlavhasi (D61 ⑥).
 *
 *  ⚠️ Nega alohida komponent: saralash holati hozir faqat **ko'rinishda**
 *  bor edi (`↑`/`↓` matni). Ekran o'quvchi uchun jadval qaysi ustun
 *  bo'yicha saralanganini bilishning yagona standart yo'li — `aria-sort`
 *  atributi, va u butun loyihada **birorta joyda ham yo'q edi**
 *  (o'lchandi: `grep aria-sort` → 0 natija).
 *
 *  `aria-sort` faqat FAOL ustunga qo'yiladi — qolganlarida umuman
 *  bo'lmasligi kerak (`aria-sort="none"` ham mumkin, lekin ortiqcha ovoz).
 *
 *  Ikonka `aria-hidden`: yo'nalishni `aria-sort` aytadi, ya'ni uni
 *  takrorlash shovqin bo'lardi. */
export function SortHeader({
  children,
  active = false,
  direction = "asc",
  onSort,
  align = "left",
  className = "",
}: {
  children: React.ReactNode;
  /** Shu ustun bo'yicha saralanyaptimi. */
  active?: boolean;
  /** Faol bo'lsa — yo'nalish. */
  direction?: SortDirection;
  /** Bosilganda chaqiriladi. Berilmasa — tugma emas, oddiy sarlavha. */
  onSort?: () => void;
  align?: "left" | "right" | "center";
  className?: string;
}) {
  const alignCls =
    align === "right" ? "text-right" : align === "center" ? "text-center" : "text-left";
  const label = (
    <span className="inline-flex items-center gap-1">
      {children}
      {onSort && <SortGlyph active={active} direction={direction} />}
    </span>
  );
  return (
    <th
      scope="col"
      aria-sort={active ? ARIA_SORT[direction] : undefined}
      className={`px-4 py-3 text-theme-xs font-medium rw-dim uppercase ${alignCls} ${className}`}
    >
      {onSort ? (
        <button
          type="button"
          onClick={onSort}
          className="inline-flex items-center rw-radius-sm rw-hover-bg rw-focus-ring"
        >
          {label}
        </button>
      ) : (
        label
      )}
    </th>
  );
}

/** Yo'nalish belgisi. Faol emas — ikkala strelka xira, ya'ni «bosilsa
 *  saralanadi» degani ko'rinib turadi. */
function SortGlyph({ active, direction }: { active: boolean; direction: "asc" | "desc" }) {
  if (!active) {
    return (
      <span aria-hidden="true" className="rw-faint opacity-50">
        ↕
      </span>
    );
  }
  return (
    <span aria-hidden="true" className="rw-accent-ink">
      {direction === "asc" ? "↑" : "↓"}
    </span>
  );
}

export function TBody({ children }: { children: React.ReactNode }) {
  return <tbody className="divide-y rw-divide">{children}</tbody>;}

export function TR({ children }: { children: React.ReactNode }) {
  return <tr className="transition rw-hover-bg">{children}</tr>;
}

export function TD({
  children,
  align = "left",
  className = "",
}: {
  children: React.ReactNode;
  align?: "left" | "right" | "center";
  className?: string;
}) {
  return (
    <td
      className={`px-4 py-3 text-theme-sm rw-strong 
 ${align === "right" ? "text-right" : align === "center" ? "text-center" : "text-left"}
 ${className}`}
    >
      {children}
    </td>
  );
}

export function EmptyRow({
  colSpan,
  children,
}: {
  colSpan: number;
  children: React.ReactNode;
}) {
  return (
    <tr>
      <td
        colSpan={colSpan}
        className="px-4 py-10 text-center text-theme-sm rw-faint"
      >
        {children}
      </td>
    </tr>
  );
}
