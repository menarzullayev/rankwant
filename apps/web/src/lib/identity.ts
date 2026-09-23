/** Foydalanuvchi unvoni — umumiy tip.
 *
 *  ⚠️ Bu tip bir necha domenga tegishli (`profile`, `contests`, `problems`,
 *  `hackathons`), shuning uchun feature ichida emas — umumiy qatlamda.
 *  Ilgari `features/profile/api/users.ts` da edi va boshqa feature'lar
 *  profil API'siga bog'lanib qolardi. */

export type UserTitle = {
  code: string;
  level: number;
  colour_group: string;
  marker: number;
};

/** Pog'ona guruhi — reyting grafigidagi chiziqlar (ADR-0027 § L2). */
export type TitleBand = {
  code: string;
  level: number;
  min: number;
  max: number | null;
  colour_group: string;
  marker: number;
};
