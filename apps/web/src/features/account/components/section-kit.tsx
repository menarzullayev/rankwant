"use client";

/** Sozlamalar bo'limlari uchun umumiy bo'laklar.
 *
 *  ⚠️ Bu fayl **faqat qayta eksport** qiladi. Umumiy narsalarning haqiqiy
 *  uyi — global qatlam:
 *
 *  | Nima                      | Uy                        |
 *  |---------------------------|---------------------------|
 *  | `useAction`, `useLoad`, `describeError` | `lib/hooks`  |
 *  | `Status`, `Hint`          | `components/kit/Feedback` |
 *  | `TextArea`, `Select`, `Check` | `components/form/SettingsKit` |
 *  | `Loading`                 | `components/ui/Loading`   |
 *
 *  Ilgari shu fayl ularning barchasini o'zi yaratardi va natijada
 *  `hackathons`, `submissions` kabi feature'lar `features/account` ga
 *  bog'lanib qolardi — arxitektura chegarasi buzilardi. Endi sozlamalar
 *  bo'limlari o'z importlarini o'zgartirmasligi uchun shu yupqa qavat
 *  saqlanadi. */

export { describeError, useAction, useLoad } from "@/lib/hooks";
export { Hint, Status } from "@/components/kit/Feedback";
export { Check, Select, TextArea } from "@/components/form/SettingsKit";
export { Loading } from "@/components/ui/Loading";
