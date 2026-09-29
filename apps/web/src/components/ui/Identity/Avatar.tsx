/** Profil rasmi yoki bosh harf. Server va mijoz komponentlarida ishlaydi.
 *
 * `next/image` emas: rasm API'dan keladi va nomi o'zgarmas (abadiy
 * keshlanadi), 256 pikselga esa yuklashda kichraytirilgan — optimizatsiya
 * qatlami hech narsa bermasdi, faqat tashqi domen sozlamasini talab qilardi. */
export function Avatar({
  url,
  name,
  className = "size-10",
}: {
  url: string;
  name: string;
  className?: string;
}) {
  if (url) {
    return (
      // eslint-disable-next-line @next/next/no-img-element -- yuqoridagi izohga qarang
      <img
        src={url}
        alt=""
        className={`${className} shrink-0 rounded-full object-cover`}
      />
    );
  }
  return (
    <span
      aria-hidden="true"
      className={`${className} flex shrink-0 items-center justify-center rounded-full rw-accent-soft font-bold rw-accent-ink`}
    >
      {name.charAt(0).toUpperCase()}
    </span>
  );
}
