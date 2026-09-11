/** Bo'lim nima o'lchashini aytuvchi bir qator — izohsiz raqam hech narsa
 *  aytmaydi (Robocontest'dagi «20» ning ma'nosi sahifada yozilmagan edi). */
export function SectionHint({ children }: { children: React.ReactNode }) {
  return <p className="text-theme-xs rw-dim">{children}</p>;
}
