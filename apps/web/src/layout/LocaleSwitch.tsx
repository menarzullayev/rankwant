"use client";

import type { Route } from "next";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useId, useMemo, useRef, useState, useTransition } from "react";

import { Icon } from "@/components/ui/Icon";
import { useLocale, useLocaleAuto } from "@/i18n/LocaleProvider";
import { LOCALE_PARAM } from "@/i18n/locale-params";
import { LOCALES, LOCALE_NAMES, hasContentNames, t, type Locale } from "@/i18n/messages";
import { announcePrefs } from "@/lib/prefs";

import { LocaleFlag } from "./LocaleFlag";

/** «Avtomatik» — cookie o'chiriladi va til yana sarlavhadan aniqlanadi.
 *
 *  Busiz tanlov bir tomonlama qulf bo'lardi: bir marta qo'lda tanlagach
 *  `Accept-Language` bo'yicha aniqlash butunlay o'chadi va qaytish yo'li
 *  qolmaydi (tahlil B7). */
const AUTO = "__auto__";

/** Ro'yxat guruhlari va guruh ichidagi tartib.
 *
 *  Ilgari tartib izohsiz edi (`uz, kaa, ru, en, kk, ky, tg, tr, zh, es`)
 *  — na alifbo, na mintaqa (tahlil B11). */
const GROUPS: { key: string; locales: Locale[] }[] = [
  { key: "locale.group.core", locales: ["uz", "ru", "en", "kaa"] },
  { key: "locale.group.region", locales: ["kk", "ky", "tg", "tr"] },
  { key: "locale.group.broad", locales: ["zh", "es"] },
];

/** Endonim yonidagi inglizcha nom (qaror 9).
 *
 *  Faqat endonim yetarli emas (tahlil B9): lotin o'qiydigan odam
 *  `Қазақша` yoki `中文` ni topa olmasligi mumkin. Inglizcha nom — qidiruv
 *  kaliti, tarjima emas, shuning uchun HAR TILDA bir xil qoladi. */
const ENGLISH_NAMES: Record<Locale, string> = {
  uz: "Uzbek",
  kaa: "Karakalpak",
  ru: "Russian",
  en: "English",
  kk: "Kazakh",
  ky: "Kyrgyz",
  tg: "Tajik",
  tr: "Turkish",
  zh: "Chinese",
  es: "Spanish",
};

/** Panel kengligi (`w-64`) va chekka.
 *
 *  Tor ekran sharti shu ikkisidan chiqadi, ekran kengligidan emas: panel
 *  tugmaning o'ng chetidan 256px chapga osiladi, ya'ni tugma chetidan
 *  256px sig'masa — panel viewport'dan chiqib ketadi. */
const PANEL_W = 256;
const PANEL_GAP = 8;

/** Til tanlagich — custom listbox.
 *
 *  Nega native `<select>` emas (tahlil B1–B4): uni bezash mumkin emas,
 *  qorong'i UI da ro'yxat OQ chiqadi, o'lchami 118×28 va shrifti 12px —
 *  holbuki header'dagi qolgan tugmalar 40×40. Endonim yoniga inglizcha
 *  nom va mintaqa guruhi ham sig'masdi.
 *
 *  ⚠️ Native bepul bergan a11y SHU YERDA qo'lda yozilgan: rol, klaviatura,
 *  type-ahead, fokus qaytishi, tashqariga bosish, ekran o'quvchi nomi.
 *  Bularsiz bu almashtirish regressiya bo'lardi (qaror 8 ning
 *  majburiyatlari).
 *
 *  Almashtirish ARXITEKTURASI o'zgarmaydi: cookie + `router.refresh()`
 *  (qaror 7). Faqat tanlangan qiymat DARHOL ko'rinadi — ilgari u faqat
 *  server propidan kelardi va tanlov orqaga sakrardi (o'lchandi: 250 ms).
 */
export function LocaleSwitch() {
  const locale = useLocale();
  const auto = useLocaleAuto();
  const router = useRouter();
  const [pending, startTransition] = useTransition();

  // Optimistik qiymat: server aylanishi tugaguncha tanlovni ushlab
  // turadi. Server qiymati yetib kelganda RENDER paytida tozalanadi —
  // effektda emas, ya'ni `react-hooks/set-state-in-effect` buzilmaydi
  // (bu loyihada effektda `setState` taqiqlangan).
  const [optimistic, setOptimistic] = useState<string | null>(null);
  if (optimistic !== null && optimistic === (auto ? AUTO : locale)) {
    setOptimistic(null);
  }
  const current: string = optimistic ?? (auto ? AUTO : locale);

  const [open, setOpen] = useState(false);
  const [active, setActive] = useState<string>(locale);

  // Tor ekranda panel `fixed` bo'ladi va shu koordinatadan boshlanadi.
  // `null` — keng ekran: panel odatdagidek tugmaga bog'lanadi.
  const [narrowBox, setNarrowBox] = useState<{ top: number } | null>(null);

  const rootRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const listRef = useRef<HTMLUListElement>(null);
  // Type-ahead: ketma-ket bosilgan harflar shu yerda yig'iladi.
  const typed = useRef({ text: "", at: 0 });
  const listId = useId();

  const options = useMemo(
    () => [AUTO, ...GROUPS.flatMap((group) => group.locales)] as string[],
    [],
  );

  // Native-first: triggerda faqat endonim. «Avtomatik» bo'lsa ham
  // aniqlangan tilning o'z nomi — bayroq qaysi til ekanini ko'rsatadi.
  // Inglizcha kalit menyuda, ikkinchi qatorda (qaror 9 / tahlil B9).
  const shown: Locale = current === AUTO ? locale : (current as Locale);
  const currentLabel = LOCALE_NAMES[shown];

  // Til KODI endi triggerda ko'rinmaydi — faqat `aria-label` da qoladi
  // (ovoz bilan boshqaruvchi `zh` deb ham chaqira olsin).
  //
  // Tarix: 2026-09-18 da tor ekranda KOD tanlangan edi — sabab, to'liq nom
  // bilan tugma 165px bo'lib header 15px (chiqqan) / 59px (kirgan) toshgan.
  // 2026-09-19 da qayta o'lchandi (`main` = 6486cd6, 320px): endonim
  // `max-w-[3rem]` bilan chegaralansa tugma 116px, toshish 0, va 10
  // endonimdan 7 tasi TO'LIQ sig'adi (faqat `Кыргызча`, `O'zbekcha`,
  // `Qaraqalpaqsha` vizual qirqiladi). Ya'ni kod shart emas edi.
  //
  // Nega butunlay yashirmaymiz: «qaysi tildaman» — eng ko'p so'raladigan
  // savol (qaror 9), kod uni saqlaydi, globus-only yo'qotardi.
  const currentCode = current === AUTO ? locale : current;

  // `active` ni ochilishda o'rnatadigan effekt YO'Q: uni `openList()`
  // o'zi qiladi. Effektda `setState` bu loyihada taqiqlangan
  // (`react-hooks/set-state-in-effect`) va bu yerda u ortiqcha ham edi —
  // ketma-ket ikki marta chizishga olib kelardi.

  const choose = useCallback(
    (next: string) => {
      setOpen(false);
      setOptimistic(next);
      buttonRef.current?.focus();

      if (next === AUTO) {
        // Marker, o'chirish EMAS: cookie yo'qligi «hali tanlanmagan»
        // degani, ya'ni `PrefsSync` hisobdagi tilni qaytarib qo'yardi.
        document.cookie = "rw_locale=auto; path=/; max-age=31536000; samesite=lax";
        announcePrefs({ locale: null });
      } else {
        document.cookie = `rw_locale=${next}; path=/; max-age=31536000; samesite=lax`;
        // Hisobga ham — xatlar shu tilda yuboriladi.
        announcePrefs({ locale: next });
      }
      // URL'dagi `?lang=` cookie'ni bosib ketadi (proxy parametrni ustun
      // qo'yadi), ya'ni u qoldirilsa yangi tanlov keyingi yangilanishda
      // QAYTIB ketardi. Shuning uchun tanlov URL'ni ham tozalaydi va manba
      // yana cookie bo'lib qoladi.
      const url = new URL(window.location.href);
      if (url.searchParams.has(LOCALE_PARAM)) {
        url.searchParams.delete(LOCALE_PARAM);
        const next_ = `${url.pathname}${url.search}${url.hash}`;
        // ⚠️ `replace` YOLG'IZ yetarli emas — o'lchandi (2026-09-19, jonli
        // brauzer): `/about?lang=ru` da inglizchani tanlaganda URL va
        // kontent (`<title>`, `<h1>`) almashdi, lekin
        // `document.documentElement.lang` `ru` bo'lib QOLDI. Sabab: soft
        // navigatsiya faqat sahifa segmentini yangilaydi, ildiz layout
        // keshlangan qoladi — `<html lang>` esa ildizda chiziladi.
        // `refresh()` butun daraxtni serverdan qayta oladi, ya'ni
        // atribut ham yangilanadi (nazorat o'lchovi: parametrsiz yo'lda
        // aynan `refresh()` ishlaydi va atribut to'g'ri bo'ladi).
        // WCAG 3.1.1 — noto'g'ri `lang` ekran o'quvchini xato ovozga
        // o'tkazadi.
        startTransition(() => {
          router.replace(next_ as Route);
          router.refresh();
        });
        return;
      }
      startTransition(() => router.refresh());
    },
    [router],
  );

  const openList = useCallback(() => {
    setActive(current);
    // Tor ekranda `absolute right-0` chapga toshadi va panelning chap
    // ustuni (bayroq) butunlay ekrandan chiqadi. O'lchandi (320px,
    // `main` = 6486cd6, `zh`): tugma o'ng cheti atigi 212px → panel
    // `left = -44`, BARCHA 11 bayroq `left = -32…-11` — ko'rinmaydi.
    // 360px da `left = -4` (bayroq `left = 8` — ko'rinadi), ya'ni
    // chegara ~352px. Shuning uchun shart ekran kengligiga emas,
    // HAQIQIY joylashuvga bog'lanadi.
    const rect = buttonRef.current?.getBoundingClientRect();
    let box: { top: number } | null = null;
    if (rect && rect.right < PANEL_W + PANEL_GAP) {
      box = { top: rect.bottom + 4 };
    }
    setNarrowBox(box);
    setOpen(true);
  }, [current]);

  // Tashqariga bosish bilan yopilish. `pointerdown` — `click` emas:
  // `click` tugagach ishga tushadi, ya'ni tashqi tugma ikki marta
  // bosilgan bo'lib tuyuladi.
  useEffect(() => {
    if (!open) return;
    function onPointerDown(event: PointerEvent) {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false);
    }
    // Oyna o'lchami o'zgarsa panel yopiladi: `fixed` koordinatasi ochilish
    // paytida o'lchangan, ya'ni o'lcham o'zgarsa u eskirib qoladi.
    function onResize() {
      setOpen(false);
    }
    document.addEventListener("pointerdown", onPointerDown);
    window.addEventListener("resize", onResize);
    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      window.removeEventListener("resize", onResize);
    };
  }, [open]);

  // Aktiv variant ko'rinadigan joyga suriladi (ro'yxat uzun).
  useEffect(() => {
    if (!open) return;
    listRef.current
      ?.querySelector<HTMLElement>(`[data-value="${active}"]`)
      ?.scrollIntoView({ block: "nearest" });
  }, [open, active]);

  function move(step: number) {
    const index = options.indexOf(active);
    const base = index === -1 ? 0 : index;
    const next = Math.min(options.length - 1, Math.max(0, base + step));
    setActive(options[next] ?? active);
  }

  function onButtonKeyDown(event: React.KeyboardEvent<HTMLButtonElement>) {
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      if (!open) openList();
      else move(event.key === "ArrowDown" ? 1 : -1);
      return;
    }
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      if (open) choose(active);
      else openList();
      return;
    }
    if (event.key === "Escape" && open) {
      event.preventDefault();
      setOpen(false);
    }
  }

  function onListKeyDown(event: React.KeyboardEvent<HTMLUListElement>) {
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      move(event.key === "ArrowDown" ? 1 : -1);
      return;
    }
    if (event.key === "Home") {
      event.preventDefault();
      setActive(options[0] ?? active);
      return;
    }
    if (event.key === "End") {
      event.preventDefault();
      setActive(options[options.length - 1] ?? active);
      return;
    }
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      choose(active);
      return;
    }
    if (event.key === "Escape") {
      event.preventDefault();
      setOpen(false);
      // Fokus ochgan tugmaga QAYTADI — aks holda u `body` ga tushib,
      // klaviatura foydalanuvchisi sahifa boshidan boshlaydi.
      buttonRef.current?.focus();
      return;
    }
    if (event.key === "Tab") {
      // Tab — fokus ketadi; ochiq ro'yxat chalkash.
      setOpen(false);
      return;
    }
    // Type-ahead. 700 ms dan keyin yig'indi tozalanadi: aks holda "r"
    // dan keyin "u" bosgan odam `ru` ni izlaydi, lekin kechikkan
    // harflar qo'shilib `ruen` bo'lib qolishi mumkin edi.
    if (event.key.length !== 1 || event.metaKey || event.ctrlKey || event.altKey) return;
    const now = Date.now();
    const buffer = now - typed.current.at > 700 ? event.key : typed.current.text + event.key;
    typed.current = { text: buffer, at: now };
    const needle = buffer.toLowerCase();
    const hit = options.find((code) => {
      if (code === AUTO) return t(locale, "locale.auto").toLowerCase().startsWith(needle);
      return `${LOCALE_NAMES[code as Locale]} ${ENGLISH_NAMES[code as Locale]} ${code}`
        .toLowerCase()
        .includes(needle);
    });
    if (hit) setActive(hit);
  }

  return (
    <div className="relative" ref={rootRef}>
      <button
        ref={buttonRef}
        type="button"
        // `aria-haspopup` + `aria-expanded` — ekran o'quvchi ochilish
        // holatini biladi; `aria-controls` ro'yxatga bog'laydi.
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={open ? listId : undefined}
        // ⚠️ `aria-label` KO'RINADIGAN matnni O'Z ICHIGA OLISHI shart
        // (WCAG 2.5.3, «Label in Name»). Ilgari bu yerda faqat
        // `switchLabel` turardi ("Выберите язык"), ko'rinadigan matn esa
        // joriy til nomi ("Русский") — ya'ni ovoz bilan boshqaradigan
        // foydalanuvchi tugmani ekranda ko'rgan so'zi bilan
        // chaqira olmasdi. Lighthouse tutdi:
        // `label-content-name-mismatch` — accessibility 100 dan tushdi.
        //
        // Ko'rinadigan matn endi har qanday kenglikda ENDONIM (tor ekranda
        // vizual `truncate` bo'ladi, lekin DOM matni to'liq qoladi — ya'ni
        // Lighthouse uchun moslik saqlanadi). Shuning uchun `currentLabel`
        // shu yerda MAJBURIY. `currentCode` — qo'shimcha: ovoz bilan
        // boshqaruvchi `zh` deb ham chaqira olsin.
        aria-label={`${currentLabel} (${currentCode}) — ${t(locale, "locale.switchLabel")}`}
        onClick={() => (open ? setOpen(false) : openList())}
        onKeyDown={onButtonKeyDown}
        className="flex h-10 items-center gap-1.5 rw-radius-sm border rw-line rw-field-bg px-2.5
          rw-dim transition rw-hover-strong"
      >
        <LocaleFlag code={shown} />
        {/* Endonim HAR QANDAY kenglikda ko'rinadi. Ilgari `sm` dan pastda
            til KODI (`zh`) turardi — ya'ni tor ekranda odam o'z tilini
            ko'rmasdi (tahlil B9). Kod endi faqat `aria-label` da qoladi.

            `max-w` + `truncate` SHART: o'lchandi (320px, cheklovsiz
            endonim bilan) — `Qaraqalpaqsha` tugmani 149px qiladi va header
            29px toshadi; `O'zbekcha` 124px/7px, `Кыргызча` 123px/6px.
            Header'da bo'sh joy yo'q (o'ng guruh `min-w-0` bilan allaqachon
            siqilgan), shuning uchun chegara 48px: tugma 116px, toshish 0,
            va 10 endonimdan 7 tasi to'liq sig'adi. */}
        <span className="min-w-0 max-w-[3rem] truncate text-theme-xs sm:max-w-[7.5rem]">
          {currentLabel}
        </span>
        {pending ? (
          <Icon name="action.loading" className="size-3.5 shrink-0 animate-spin motion-reduce:animate-none" />
        ) : (
          <Icon name="nav.expandDown" className="size-3.5 shrink-0 opacity-70" />
        )}
      </button>

      {open && (
        <ul
          ref={listRef}
          id={listId}
          role="listbox"
          aria-label={t(locale, "locale.listLabel")}
          tabIndex={-1}
          onKeyDown={onListKeyDown}
          // Tor ekranda `fixed` + o'lchangan koordinata, keng ekranda
          // hozirgidek tugmaga bog'lanadi (shartni `openList` qo'yadi).
          style={
            narrowBox === null
              ? undefined
              : { top: narrowBox.top, left: PANEL_GAP, right: PANEL_GAP }
          }
          className={`z-50 max-h-80 overflow-y-auto rw-panel py-1 text-theme-xs ${
            narrowBox === null ? "absolute right-0 mt-1 w-64" : "fixed mt-1"
          }`}
        >
          {/* «Avtomatik» guruhdan tashqarida — u hech qaysi guruhga
              tegishli emas, ya'ni uni guruh ichiga tiqish noto'g'ri
              bo'lardi (qaror 9: «Avtomatik» BIRINCHI turadi). */}
          <li role="presentation">
            <div
              role="option"
              data-value={AUTO}
              aria-selected={current === AUTO}
              onClick={() => choose(AUTO)}
              onMouseEnter={() => setActive(AUTO)}
              className={`flex cursor-pointer items-center gap-2 px-3 py-2 text-theme-xs ${
                active === AUTO ? "rw-hover-bg" : ""
              } ${current === AUTO ? "font-medium" : ""}`}
            >
              <LocaleFlag code={locale} />
              <span className="min-w-0 flex-1">
                <span className="block truncate">{t(locale, "locale.auto")}</span>
                <span className="block truncate rw-dim-2">{LOCALE_NAMES[locale]}</span>
              </span>
              {current === AUTO && <Icon name="action.confirm" className="size-3.5 shrink-0" />}
            </div>
          </li>

          {/* ⚠️ Guruh AYNAN `role="group"` + `aria-label` bilan
              belgilanadi. O'lchandi: ilgari sarlavha shunchaki `<div>`
              edi va ekran o'quvchi 11 variantni GURUHSIZ, uzluksiz
              ro'yxat qilib o'qirdi — holbuki vizual guruh bor edi.
              `aria-label` esa tarjima qilinadi (ilgari sarlavha
              inglizcha "CORE"/"REGIONAL" bo'lib qolgan edi — `zh`
              sahifasida ham). */}
          {GROUPS.map((group) => {
            const name = t(locale, group.key);
            return (
              <li key={group.key} role="presentation">
                <div role="group" aria-label={name}>
                  <div
                    aria-hidden="true"
                    className="px-3 pb-1 pt-2 text-theme-xs uppercase tracking-wide rw-dim-2"
                  >
                    {name}
                  </div>
                  {group.locales.map((code) => (
                    <div
                      key={code}
                      role="option"
                      data-value={code}
                      aria-selected={current === code}
                      onClick={() => choose(code)}
                      onMouseEnter={() => setActive(code)}
                      className={`flex cursor-pointer items-center gap-2 px-3 py-2 text-theme-xs ${
                        active === code ? "rw-hover-bg" : ""
                      } ${current === code ? "font-medium" : ""}`}
                    >
                      <LocaleFlag code={code} />
                      <span className="min-w-0 flex-1">
                        <span className="block truncate">{LOCALE_NAMES[code]}</span>
                        {LOCALE_NAMES[code] !== ENGLISH_NAMES[code] ? (
                          <span className="block truncate rw-dim-2">{ENGLISH_NAMES[code]}</span>
                        ) : null}
                      </span>
                      {/* Qamrov OLDINDAN ko'rinadi (qaror 10, T3-c):
                          mavzu/ko'nikma nomlari faqat uz/ru/en da bor,
                          ya'ni qolgan yetti tilda o'zbekcha chiqadi.
                          Buni tanlashdan KEYIN aytish kech bo'lardi. */}
                      {!hasContentNames(code) && (
                        <span
                          title={t(locale, "content.uzOnly")}
                          className="shrink-0 rounded rw-chip px-1 text-theme-xs rw-dim-2"
                        >
                          {t(locale, "locale.contentUz")}
                        </span>
                      )}
                      {current === code && <Icon name="action.confirm" className="size-3.5 shrink-0" />}
                    </div>
                  ))}
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

/** Ro'yxatdagi barcha tillar — `LOCALES` bilan bir xil bo'lishi shart.
 *
 *  `GROUPS` ni qo'lda tahrirlash oson va bitta tilni tushirib qoldirish
 *  ham oson; bu tekshiruv modul yuklanishida o'sha xatoni tutadi. */
if (GROUPS.flatMap((g) => g.locales).length !== LOCALES.length) {
  throw new Error("LocaleSwitch: GROUPS every locale must appear exactly once");
}
