/** Sozlagich modulining bayrog'i (D38).
 *
 *  O'chirilganda kirish nuqtalari (suzuvchi tugma, header ikonkasi,
 *  panel) ko'rinmaydi, lekin saqlangan sozlamalar bazada va qurilmada
 *  qoladi — qayta yoqilganda odam o'z ko'rinishini joyida topadi.
 *
 *  ⚠️ CHEKLOV: `NEXT_PUBLIC_*` build vaqtida bundle'ga singadi, ya'ni
 *  bayroqni almashtirish uchun `web` ni qayta qurish kerak
 *  (`PLAYBOOK.md` §1 — bu loyihada ma'lum cheklov). "Bir tugma bilan
 *  o'chirish" kerak bo'lsa, bayroqni API dan olib kelish kerak — u
 *  alohida ish va hozircha qilinmagan.
 *
 *  Nega shunga qaramay shu yo'l: yangi model ham, endpoint ham talab
 *  qilmaydi va qolgan `NEXT_PUBLIC_*` qiymatlar bilan bir xil naqshda.
 *  Favqulodda holatda qayta qurish bir daqiqa oladi (o'lchandi: ~40 s).
 */
export const CUSTOMIZER_ENABLED = process.env.NEXT_PUBLIC_CUSTOMIZER !== "0";
