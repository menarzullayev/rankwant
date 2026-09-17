/** Qvant economy: wallet, quests, marathon, shop. */

import type { Problem } from "./problems";

export type Wallet = {
  balance: number;
  earned_today: number;
  remaining_today: number;
};

export type Quest = {
  code: string;
  type: "daily" | "weekly" | "achievement";
  title_uz: string;
  reward: number;
  done: boolean;
};

/** Haftalik marafon — har foydalanuvchiga o'z to'plami (PRD P1-9). */
export type Marathon = {
  week: string;
  reward: number;
  completed: boolean;
  solved_count: number;
  total: number;
  problems: (Problem & { marathon_solved: boolean })[];
};

export type ShopItem = {
  code: string;
  category: string;
  title_uz: string;
  price: number;
  is_consumable: boolean;
  owned: boolean;
};

export type Purchase = {
  code: string;
  category: string;
  title_uz: string;
  title_ru: string;
  title_en: string;
  purchased_at: string;
  is_equipped: boolean;
};
