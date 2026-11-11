/** The tolerance of a `real` problem as a reader expects it (ADR-0060):
 *  a power of ten as `10⁻⁶`, anything else in exponent form (`1.5e-5`). */

const SUPERSCRIPT: Readonly<Record<string, string>> = {
  "-": "⁻",
  "0": "⁰",
  "1": "¹",
  "2": "²",
  "3": "³",
  "4": "⁴",
  "5": "⁵",
  "6": "⁶",
  "7": "⁷",
  "8": "⁸",
  "9": "⁹",
};

export function formatTolerance(eps: number): string {
  const power = Math.log10(eps);
  if (Number.isInteger(power)) {
    return `10${[...String(power)].map((char) => SUPERSCRIPT[char] ?? char).join("")}`;
  }
  return eps.toExponential();
}
