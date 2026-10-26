import { describe, expect, it } from "vitest";

import { passwordRules, strength } from "../src/password";

describe("strength", () => {
  it("is 0 for an empty password", () => {
    expect(strength("")).toBe(0);
  });

  it("never rates a password the server refuses above the lowest level", () => {
    expect(strength("1234567")).toBe(1); // too short
    expect(strength("12345678901")).toBe(1); // digits only
    expect(strength("aaaaaaaaaa")).toBe(1); // one repeated character
    expect(strength("Password1")).toBe(1); // on the common list
  });

  it("climbs with length and variety through all five levels", () => {
    expect(strength("abcdefgh")).toBe(2);
    expect(strength("abcdefgh1")).toBe(2);
    expect(strength("Abcdefgh1")).toBe(3);
    expect(strength("Abcdefgh1!")).toBe(3);
    expect(strength("Abcdefghijk1!")).toBe(4);
    expect(strength("Abcdefghijklmno1!")).toBe(5);
  });
});

describe("passwordRules", () => {
  it("reports each rule on its own", () => {
    expect(passwordRules("abc")).toEqual({ length: false, notNumeric: true, varied: true });
    expect(passwordRules("12345678")).toEqual({ length: true, notNumeric: false, varied: true });
    expect(passwordRules("aabbaabb")).toEqual({ length: true, notNumeric: true, varied: false });
  });
});
