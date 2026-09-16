import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";

export default defineConfig({
  resolve: {
    alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) },
  },
  test: {
    // Outside `src/` on purpose: tools/check_i18n.py scans `src/` for hard-coded
    // UI text, and test fixtures are full of literal strings.
    include: ["tests/unit/**/*.test.ts"],
    environment: "node",
  },
});
