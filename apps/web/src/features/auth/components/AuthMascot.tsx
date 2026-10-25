import type { ReactNode } from "react";

/** Cho'qqi — the brand mascot, drawn from the crest's mountain.
 *
 *  Pure SVG with no request, no asset file. Every fill is a class from
 *  `auth-panel.css` (`m-*`), so this file carries no colour. The body and
 *  flame gradients are defined once in `AuthPanel` (`#ap-body`, `#ap-fire`,
 *  `#ap-gold`) and referenced from CSS.
 *
 *  Decorative by default (`aria-hidden`); pass `label` where the mascot is
 *  the point of the slide and it should be announced. */

const IMG = "img";

type Eyes = "open" | "happy";
type Mouth = "smile" | "open" | "flat";
type Arms = "down" | "up" | "wave" | "point" | "hold";

export function AuthMascot({
  eyes = "open",
  mouth = "smile",
  arms = "down",
  gaze = 0,
  wide = false,
  label,
  children,
}: {
  eyes?: Eyes;
  mouth?: Mouth;
  arms?: Arms;
  /** Pupil shift in viewBox units; negative looks left. */
  gaze?: number;
  /** Room on the right for a held object (watch, gavel, flame). */
  wide?: boolean;
  label?: string;
  children?: ReactNode;
}) {
  return (
    <svg
      className="ap-mascot"
      viewBox={wide ? "0 -34 250 234" : "0 -34 200 234"}
      role={label ? IMG : undefined}
      aria-label={label}
      aria-hidden={label ? undefined : true}
      focusable="false"
    >
      <ellipse className="m-shadow" cx="100" cy="188" rx="62" ry="8" />
      <line className="m-pole" x1="100" y1="22" x2="100" y2="-24" strokeWidth="4" strokeLinecap="round" />
      <path className="m-flag" d="M102 -24 L136 -14 L102 -4 Z" />
      {arms === "up" ? (
        <>
          <ellipse className="m-arm" cx="16" cy="92" rx="11" ry="22" transform="rotate(-25 16 92)" />
          <ellipse className="m-arm" cx="184" cy="92" rx="11" ry="22" transform="rotate(25 184 92)" />
        </>
      ) : arms === "point" ? (
        <>
          <g className="ap-point">
            <ellipse className="m-arm" cx="22" cy="104" rx="11" ry="22" transform="rotate(62 22 104)" />
          </g>
          <ellipse className="m-arm" cx="178" cy="132" rx="11" ry="20" transform="rotate(-25 178 132)" />
        </>
      ) : arms === "wave" ? (
        <>
          <ellipse className="m-arm" cx="22" cy="132" rx="11" ry="20" transform="rotate(25 22 132)" />
          <g className="ap-wave">
            <ellipse className="m-arm" cx="184" cy="96" rx="11" ry="22" transform="rotate(-20 184 96)" />
          </g>
        </>
      ) : arms === "hold" ? (
        <>
          <ellipse className="m-arm" cx="22" cy="132" rx="11" ry="20" transform="rotate(25 22 132)" />
          <ellipse className="m-arm" cx="182" cy="128" rx="11" ry="18" transform="rotate(-32 182 128)" />
        </>
      ) : (
        <>
          <ellipse className="m-arm" cx="22" cy="132" rx="11" ry="20" transform="rotate(25 22 132)" />
          <ellipse className="m-arm" cx="178" cy="132" rx="11" ry="20" transform="rotate(-25 178 132)" />
        </>
      )}
      <path
        className="m-body"
        d="M100 20 C113 20 121 30 131 46 L178 126 C188 144 176 176 156 176 L44 176 C24 176 12 144 22 126 L69 46 C79 30 87 20 100 20 Z"
      />
      <path
        className="m-snow"
        d="M100 20 C89 20 81 29 73 43 L65 58 Q79 68 90 58 Q100 70 110 58 Q121 68 135 58 L127 43 C119 29 111 20 100 20 Z"
      />
      {eyes === "happy" ? (
        <>
          <path className="m-line" d="M66 106 Q78 94 90 106" strokeWidth="5" />
          <path className="m-line" d="M110 106 Q122 94 134 106" strokeWidth="5" />
        </>
      ) : (
        <g className="ap-blink">
          <ellipse className="m-eye" cx="78" cy="108" rx="14" ry="16" />
          <ellipse className="m-eye" cx="122" cy="108" rx="14" ry="16" />
          <circle className="m-pupil" cx={80 + gaze} cy="110" r="7" />
          <circle className="m-pupil" cx={124 + gaze} cy="110" r="7" />
          <circle className="m-glint" cx={83 + gaze} cy="106" r="2.5" />
          <circle className="m-glint" cx={127 + gaze} cy="106" r="2.5" />
        </g>
      )}
      <circle className="m-cheek" cx="62" cy="130" r="8" />
      <circle className="m-cheek" cx="138" cy="130" r="8" />
      {mouth === "open" ? (
        <path className="m-ink" d="M86 130 Q100 152 114 130 Z" />
      ) : mouth === "flat" ? (
        <path className="m-line" d="M90 136 L110 136" strokeWidth="4" />
      ) : (
        <path className="m-line" d="M88 132 Q100 146 112 132" strokeWidth="4" />
      )}
      <ellipse className="m-foot" cx="72" cy="178" rx="20" ry="9" />
      <ellipse className="m-foot" cx="128" cy="178" rx="20" ry="9" />
      {children}
    </svg>
  );
}
