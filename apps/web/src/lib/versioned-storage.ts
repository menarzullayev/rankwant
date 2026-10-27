/** Values this device keeps for the person (code drafts, recent searches) are
 *  written as `{"$v": <version>, "data": …}`. The shape of `data` can then
 *  change without an old value being misread by new code or new code breaking
 *  an old tab:
 *
 *  - a value from before versioning (a bare string or array) is read as it
 *    always was — nothing a person wrote is lost to the upgrade;
 *  - a value from a NEWER version than this page knows is ignored, so the
 *    page falls back to its default instead of guessing at the shape.
 *
 *  Not used for UI toggles that are validated on read (a number clamped to a
 *  range, `"1"`/`"0"`) nor for the appearance keys read by the pre-hydration
 *  script: those have their own contract (docs/08-technical-spec/
 *  customization-contract.md). */

export type Unpacked =
  | { kind: "empty" }
  | { kind: "legacy"; raw: string }
  | { kind: "current"; data: unknown }
  | { kind: "newer" };

export function pack(version: number, data: unknown): string {
  return JSON.stringify({ $v: version, data });
}

export function unpack(raw: string | null, version: number): Unpacked {
  if (raw === null) return { kind: "empty" };
  try {
    const value: unknown = JSON.parse(raw);
    if (value !== null && typeof value === "object" && !Array.isArray(value)) {
      const stamped = value as { $v?: unknown; data?: unknown };
      if (typeof stamped.$v === "number") {
        return stamped.$v > version ? { kind: "newer" } : { kind: "current", data: stamped.data };
      }
    }
  } catch {
    // Not JSON: a bare draft written before versioning.
  }
  return { kind: "legacy", raw };
}

/** A string value (a draft): the stored text, or `null` for "use the default". */
export function readString(raw: string | null, version: number): string | null {
  const got = unpack(raw, version);
  if (got.kind === "legacy") return got.raw;
  if (got.kind === "current" && typeof got.data === "string") return got.data;
  return null;
}
