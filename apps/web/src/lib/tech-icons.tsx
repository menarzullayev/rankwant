/** Texnologiya belgilari — `simple-icons` (CC0).
 *
 * Faqat katalogdagi (`profiles/catalog.py`) belgilar import qilinadi:
 * paket 3000 dan ortiq belgi beradi, nomli import esa qolganini
 * to'plamdan chiqarib tashlaydi. Belgi `currentColor` bilan chiziladi —
 * brend rangi (Next.js, Rust — qora) qorong'u mavzuda ko'rinmay qolardi.
 */

import {
  siAngular,
  siC,
  siCodeforces,
  siCplusplus,
  siDart,
  siDjango,
  siDocker,
  siDotnet,
  siElixir,
  siFastapi,
  siFlask,
  siFlutter,
  siGit,
  siGo,
  siGraphql,
  siHaskell,
  siJavascript,
  siJulia,
  siKotlin,
  siKubernetes,
  siLaravel,
  siLeetcode,
  siLinux,
  siLua,
  siMongodb,
  siMysql,
  siNextdotjs,
  siNodedotjs,
  siNumpy,
  siOcaml,
  siOpenjdk,
  siPandas,
  siPhp,
  siPostgresql,
  siPython,
  siPytorch,
  siR,
  siReact,
  siRedis,
  siRuby,
  siRust,
  siScala,
  siSpring,
  siSwift,
  siTailwindcss,
  siTensorflow,
  siTypescript,
  siVuedotjs,
} from "simple-icons";

type Icon = { title: string; path: string };

export const TECH_ICONS: Record<string, Icon> = {
  cplusplus: siCplusplus,
  c: siC,
  python: siPython,
  openjdk: siOpenjdk,
  javascript: siJavascript,
  typescript: siTypescript,
  go: siGo,
  rust: siRust,
  kotlin: siKotlin,
  dotnet: siDotnet,
  php: siPhp,
  ruby: siRuby,
  swift: siSwift,
  dart: siDart,
  haskell: siHaskell,
  scala: siScala,
  lua: siLua,
  r: siR,
  julia: siJulia,
  elixir: siElixir,
  ocaml: siOcaml,
  react: siReact,
  vuedotjs: siVuedotjs,
  angular: siAngular,
  nextdotjs: siNextdotjs,
  nodedotjs: siNodedotjs,
  tailwindcss: siTailwindcss,
  graphql: siGraphql,
  django: siDjango,
  flask: siFlask,
  fastapi: siFastapi,
  spring: siSpring,
  laravel: siLaravel,
  flutter: siFlutter,
  postgresql: siPostgresql,
  mysql: siMysql,
  mongodb: siMongodb,
  redis: siRedis,
  docker: siDocker,
  kubernetes: siKubernetes,
  linux: siLinux,
  git: siGit,
  numpy: siNumpy,
  pandas: siPandas,
  tensorflow: siTensorflow,
  pytorch: siPytorch,
};

/** Tashqi profillar. LinkedIn va AtCoder belgisi paketda yo'q —
 *  LinkedIn brend qoidasi sabab olib tashlangan. */
export const EXTERNAL_ICONS: Partial<Record<string, Icon>> = {
  codeforces: siCodeforces,
  leetcode: siLeetcode,
};

export function BrandIcon({
  icon,
  className = "size-4",
}: {
  icon: Icon | undefined;
  className?: string;
}) {
  if (!icon) return null;
  return (
    <svg viewBox="0 0 24 24" className={className} aria-hidden="true">
      <path d={icon.path} fill="currentColor" />
    </svg>
  );
}
