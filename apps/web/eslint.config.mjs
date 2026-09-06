import next from "eslint-config-next";

// eslint-config-next 16 native flat config beradi — FlatCompat kerak emas.
const config = [
  { ignores: [".next/**", "node_modules/**", "next-env.d.ts"] },
  ...next,
];

export default config;
