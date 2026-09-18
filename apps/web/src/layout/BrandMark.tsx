import { IntentLink } from "@/components/ui/IntentLink";

/** Brend — YAGONA manba (qaror 22): header, topnav va sidebar shu
 *  komponentdan ishlatadi. Ilgari wordmark ikki joyda nusxalangan edi
 *  (AppSidebar, AppTopNav), header'da esa umuman yo'q edi — telefonlda
 *  brend faqat drawer ichida ko'rinardi.
 *
 *  `variant`:
 *    · "responsive" — `sm` dan kengda wordmark, torda monogram (header:
 *      320 px sig'ish qarori tordagi har px hisoblangan).
 *    · "full"       — doim wordmark (topnav, keng sidebar).
 *    · "compact"    — doim monogram (yig'ilgan sidebar, 86 px — CSS
 *      breakpoint'i panel holatini bilmaydi, shuning uchun prop).
 */
export default function BrandMark({
  variant = "responsive",
  className = "",
  onClick,
}: {
  variant?: "responsive" | "full" | "compact";
  className?: string;
  onClick?: () => void;
}) {
  const wordmark = (
    <>
      Rank<span className="rw-accent-ink">Want</span>
    </>
  );
  return (
    <IntentLink
      href="/"
      aria-label="RankWant"
      className={`text-lg font-bold ${className}`}
      onClick={onClick}
    >
      {variant === "compact" ? (
        <span className="rw-accent-ink">R</span>
      ) : variant === "full" ? (
        wordmark
      ) : (
        <>
          <span className="hidden sm:inline">{wordmark}</span>
          {/* Monogram ham brend — `aria-label` yuqorida, ya'ni ekran
              o'quvchi «R» emas, «RankWant» ni eshitadi. */}
          <span className="rw-accent-ink sm:hidden" aria-hidden="true">
            R
          </span>
        </>
      )}
    </IntentLink>
  );
}
