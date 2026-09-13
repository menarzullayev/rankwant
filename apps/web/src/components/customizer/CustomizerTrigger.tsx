"use client";

import { useCustomizer } from "@/context/CustomizerContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { PaletteIcon } from "@/icons";

/** Header'dagi kirish nuqtasi (D3).
 *
 *  Ilgari bu yerda IKKI tugma bor edi — mavzu va uslub. Ikkalasi ham
 *  bitta panelga yig'ildi: bir xil sozlamani ikki joydan boshqarish
 *  chalkashlik tug'diradi va yangi sozlamalar qaysi biriga tegishli
 *  ekani noaniq bo'lib qolardi.
 *
 *  Bu ikonka telefonda ham SHART: u yerda suzuvchi tugma yo'q (D32),
 *  ya'ni bu — asosiy kirish nuqtasi. Shu sababli `lg:` bilan
 *  yashirilmaydi.
 *
 *  ⚠️ `PaletteIcon`, `UpdatesIcon` EMAS: ilgari ikkinchisi ishlatilgan
 *  edi va u yangilanishlar qo'ng'irog'i bilan AYNI ikonka — ikki xil
 *  vazifa, bir xil belgi. Palitra — ko'rinish sozlagichining aniq belgisi.
 */
export function CustomizerTrigger() {
  const locale = useLocale();
  const { open, toggle } = useCustomizer();

  return (
    <button
      type="button"
      onClick={toggle}
      aria-expanded={open}
      aria-label={t(locale, "customizer.title")}
      title={`${t(locale, "customizer.title")} (Ctrl+.)`}
      className="flex size-10 items-center justify-center rw-radius-sm rw-dim-2 transition rw-hover-bg"
    >
      <PaletteIcon />
    </button>
  );
}
