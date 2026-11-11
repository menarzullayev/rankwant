#!/usr/bin/env python3
"""Build the vendored cp.uz algorithms snapshot (ADR-0062).

Reads the cp.uz content snapshot and the cp-algorithms original, both at a
pinned commit, and writes:

- `apps/api/content/cpuz/uz/<category>/<slug>.md` — the Uzbek article,
  normalised for our Markdown renderer;
- `apps/api/content/cpuz/en/<category>/<slug>.md` — the English original,
  normalised the same way (it becomes the `en` version, ADR-0062 § 2.4);
- `apps/api/content/cpuz/articles.json` — metadata, practice links and the
  hash of every file this tool wrote;
- `apps/web/public/algorithms-media/<category>/<file>` — the local images.

Run it again for a newer pin. A file whose bytes differ from what this tool
wrote last time was edited by us (the agent review, a person) and is kept:
the import never overwrites our own edits (ADR-0062 § 2.1).

    python tools/cpuz_snapshot.py --cpuz <cp-uz clone> --cpuz-rev 91f90d7 \\
        --upstream <cp-algorithms clone>

The normalisation only changes markup our renderer does not draw (raw HTML is
off there on purpose — `components/ui/Markdown.tsx`): mkdocs admonitions,
tabs, fence attributes, `<img>`/`<figure>`/`<center>`/`<a>` tags and the
relative `*.md` links. Prose, code and formulas are left as they are.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "apps/api"))
from content.exercise_keys import exercise_key

OUT = ROOT / "apps/api/content/cpuz"
MEDIA = ROOT / "apps/web/public/algorithms-media"
MEDIA_URL = "/algorithms-media"
ROUTE = "/algorithms"
UPSTREAM_SITE = "https://cp-algorithms.com"

FENCE = re.compile(r"^(\s*)(```+|~~~+)\s*(.*)$")
ADMONITION = re.compile(r'^(\s*)(!!!|\?\?\?\+?)\s*([\w-]+)(?:\s+"([^"]*)")?\s*$')
TAB = re.compile(r'^(\s*)===\s+"([^"]*)"\s*$')
# `{#id}`, `{ #id data-toc-label=… }` and the attr_list form `{: #id }`.
HEADING_ID = re.compile(r"^(#{1,6}\s.*?)\s*\{\s*:?\s*#([\w-]+)(?:\s[^}]*)?\}\s*$")
LANGS = {
    "c++": "cpp",
    "cpp": "cpp",
    "py": "python",
    "python": "python",
    "nohighlight": "text",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_show(repo: Path, rev: str, path: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{rev}:{path}"], cwd=repo, capture_output=True, check=True
    ).stdout


def git_rev(repo: Path, rev: str) -> str:
    return subprocess.run(
        ["git", "rev-parse", rev], cwd=repo, capture_output=True, check=True, text=True
    ).stdout.strip()


def category_slug(name: str) -> str:
    return name.replace("_", "-")


def article_slug(stem: str) -> str:
    return stem.replace("_", "-").lower()


# ── practice links: `content.exercise_keys` (shared with the API) ──────────

# ── normalisation ──────────────────────────────────────────────────────────


class Links:
    """Rewrites the relative links of one article."""

    def __init__(
        self, routes: dict[str, str], media: dict[str, str], here: str
    ) -> None:
        self.routes = (
            routes  # "algebra/binary-exp.md" -> "/algorithms/algebra/binary-exp"
        )
        self.media = media  # "algebra/x.png" -> "/algorithms-media/algebra/x.png"
        self.here = here  # "algebra/binary-exp.md"
        self.unresolved: list[str] = []

    def resolve(self, url: str) -> str:
        if re.match(r"^[a-z][a-z0-9+.-]*:", url, re.IGNORECASE) or url.startswith(
            ("#", "/")
        ):
            return url
        target, _, anchor = url.partition("#")
        base = Path(self.here).parent
        joined = (base / target).as_posix() if target else self.here
        parts: list[str] = []
        for part in joined.split("/"):
            if part == "..":
                if parts:
                    parts.pop()
            elif part and part != ".":
                parts.append(part)
        key = "/".join(parts)
        suffix = f"#{anchor}" if anchor else ""
        if key in self.routes:
            return self.routes[key] + suffix
        if key in self.media:
            return self.media[key]
        if key.endswith(".md"):
            # An article cp.uz did not translate: the original on cp-algorithms.
            return f"{UPSTREAM_SITE}/{key[:-3]}.html{suffix}"
        self.unresolved.append(url)
        return url


def protect(text: str) -> tuple[str, list[str]]:
    """Hide inline code and math so the HTML rewrite cannot touch them."""
    kept: list[str] = []

    def keep(m: re.Match[str]) -> str:
        kept.append(m.group(0))
        return f"\x00{len(kept) - 1}\x00"

    text = re.sub(r"`[^`\n]+`", keep, text)
    text = re.sub(r"\$\$.+?\$\$", keep, text, flags=re.DOTALL)
    text = re.sub(r"(?<![\\$])\$(?!\s)[^$\n]+?(?<![\s\\])\$", keep, text)
    return text, kept


def restore(text: str, kept: list[str]) -> str:
    return re.sub(r"\x00(\d+)\x00", lambda m: kept[int(m.group(1))], text)


def attr(tag: str, name: str) -> str | None:
    m = re.search(rf'\b{name}\s*=\s*(["\'])(.*?)\1', tag, re.DOTALL)
    return m.group(2) if m else None


def html_to_markdown(text: str, links: Links) -> str:
    text, kept = protect(text)

    def script(m: re.Match[str]) -> str:
        body = m.group(2).strip()
        return f"$${body}$$" if "display" in m.group(1) else f"${body}$"

    text = re.sub(
        r"<script\s+type=['\"](math/tex[^'\"]*)['\"]\s*>(.*?)</script>",
        script,
        text,
        flags=re.DOTALL,
    )

    def img(m: re.Match[str]) -> str:
        src = attr(m.group(0), "src") or ""
        alt = attr(m.group(0), "alt") or ""
        return f"![{alt}]({links.resolve(src)})"

    text = re.sub(r"<img\b[^>]*?/?>", img, text, flags=re.DOTALL)

    def anchor(m: re.Match[str]) -> str:
        href = attr(m.group(1), "href")
        inner = m.group(2).strip()
        if href is None:
            return inner  # `<a id=…>` / `<a name=…>`: an anchor target, nothing to show
        return f"[{inner}]({links.resolve(href)})"

    text = re.sub(r"<a\b([^>]*)>(.*?)</a>", anchor, text, flags=re.DOTALL)
    text = re.sub(
        r"<figcaption>\s*(.*?)\s*</figcaption>",
        lambda m: "\n*" + " ".join(m.group(1).split()) + "*\n",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(r"</?(?:center|figure|div|span|p)\b[^>]*>", "", text)
    text = re.sub(r"<br\s*/?>", " ", text)
    text = re.sub(r"<(b|strong)>(.*?)</\1>", r"**\2**", text, flags=re.DOTALL)
    text = re.sub(r"<(tt|code|kbd)>(.*?)</\1>", r"`\2`", text, flags=re.DOTALL)
    text = re.sub(r"</?(?:sup|sub|u|small)>", "", text)
    text = re.sub(r"<(i|em)>(.*?)</\1>", r"*\2*", text, flags=re.DOTALL)
    return restore(text, kept)


def markdown_links(text: str, links: Links) -> str:
    text, kept = protect(text)
    text = re.sub(
        r"(!?\[[^\]]*\]\()\s*<?([^)\s>]+)>?(\s+\"[^\"]*\")?\)",
        lambda m: f"{m.group(1)}{links.resolve(m.group(2))}{m.group(3) or ''})",
        text,
    )
    return restore(text, kept)


def dedent(line: str) -> str:
    if line.startswith("\t"):
        return line[1:]
    if line.startswith("    "):
        return line[4:]
    return line.lstrip(" ")


def normalise_blocks(lines: list[str]) -> list[str]:
    """mkdocs admonitions and tabs → blockquotes and labels; fence info → language."""
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m_adm = ADMONITION.match(line)
        m_tab = TAB.match(line)
        if m_adm or m_tab:
            indent = (m_adm or m_tab).group(1)  # type: ignore[union-attr]
            body: list[str] = []
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if nxt.strip() == "":
                    body.append("")
                    i += 1
                    continue
                if nxt.startswith((indent + "\t", indent + "    ")):
                    body.append(dedent(nxt[len(indent) :]))
                    i += 1
                    continue
                break
            while body and body[-1] == "":
                body.pop()
            inner = normalise_blocks(body)
            if m_adm:
                title = m_adm.group(4)
                quoted = ([f"**{title}**", ""] if title else []) + inner
                out.extend(indent + ("> " + q if q else ">") for q in quoted)
            else:
                out.extend([indent + f"**{m_tab.group(2)}**", ""])  # type: ignore[union-attr]
                out.extend(indent + q if q else "" for q in inner)
            out.append("")
            continue
        m_fence = FENCE.match(line)
        if m_fence:
            info = m_fence.group(3).strip()
            lang = ""
            if info.startswith("{"):
                m_lang = re.search(r"\.([\w+#-]+)", info)
                lang = m_lang.group(1) if m_lang else ""
            else:
                lang = info.split()[0] if info else ""
            lang = LANGS.get(lang.lower(), lang)
            out.append(f"{m_fence.group(1)}{m_fence.group(2)}{lang}")
            close = m_fence.group(2)
            i += 1
            while i < len(lines):
                out.append(lines[i])
                if (
                    lines[i].strip().startswith(close)
                    and lines[i].strip().strip(close[0]) == ""
                ):
                    i += 1
                    break
                i += 1
            continue
        m_head = HEADING_ID.match(line)
        out.append(f"{m_head.group(1)} {{#{m_head.group(2)}}}" if m_head else line)
        i += 1
    return out


def split_fences(text: str) -> list[tuple[bool, str]]:
    """Alternate prose and fenced code, so prose rewrites never enter code."""
    parts: list[tuple[bool, str]] = []
    buf: list[str] = []
    in_code = False
    close = ""
    for line in text.split("\n"):
        stripped = line.strip().lstrip(">").strip()
        m = FENCE.match(stripped)
        if not in_code and m:
            if buf:
                parts.append((False, "\n".join(buf)))
            buf, in_code, close = [line], True, m.group(2)
            continue
        buf.append(line)
        if in_code and stripped.startswith(close) and stripped.strip(close[0]) == "":
            parts.append((True, "\n".join(buf)))
            buf, in_code = [], False
    if buf:
        parts.append((in_code, "\n".join(buf)))
    return parts


HEADING_ATTRS = re.compile(r"^(#{1,6}\s.*?)\s*\{\s*[^}#]*\}\s*$")
JINJA = re.compile(r"\{%-?\s*(?:raw|endraw)\s*-?%\}")
DISPLAY_BRACKETS = re.compile(r"(?<!\\)\\\[(.+?)(?<!\\)\\\]", re.DOTALL)


TEXT_MODE = re.compile(r"(\\(?:text|textrm|texttt|textit|textbf|mbox)\{)([^{}]*)\}")


def _eqnarray(edge: str) -> str:
    return "\\begin{array}{rcl}" if edge == "begin" else "\\end{array}"


DISPLAY_OPEN = re.compile(r"^([ \t>]*)\$\$(.*)$")
DISPLAY_LINE = re.compile(r"^([ \t>]*)\$\$((?:(?!\$\$).)+)\$\$[ \t]*$")
BARE_ENV = re.compile(r"^([ \t>]*)(\\begin\{([a-z]+\*?)\}.*)$")


def _fenced(prefix: str, body: list[str]) -> list[str]:
    rows = [f"{prefix}{row}" if row else prefix.rstrip() for row in body]
    return [f"{prefix}$$", *rows, f"{prefix}$$"]


def fence_display_math(chunk: str) -> str:
    """Every display formula gets its `$$` on lines of their own.

    remark-math reads a display formula like a code fence: what follows the
    opening `$$` on its line is metadata and is dropped (`$$\\begin{align}`
    lost its `\\begin`), and a closing `$$` must stand alone. A whole line of
    `$$x$$` is not a fence at all: it renders as inline math, where `align`
    is refused. MathJax also draws a bare `\\begin{align}` that no `$$`
    surrounds; our renderer prints it as text. mkdocs accepted all three
    (measured 2026-11-12). A blockquote's `>` prefix is kept on every line.
    """
    lines = chunk.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        one = DISPLAY_LINE.match(lines[i])
        if one:
            out += _fenced(one.group(1), [one.group(2).strip()])
            i += 1
            continue
        env = BARE_ENV.match(lines[i])
        # Only an environment that opens its own paragraph: one that follows
        # text is the tail of an inline `$…$` (simulated-annealing's cases).
        if env and (not out or not out[-1].strip(" \t>")):
            prefix, end = env.group(1), f"\\end{{{env.group(3)}}}"
            j = i
            while j < len(lines) and end not in lines[j]:
                j += 1
            if j < len(lines):
                body = [
                    line[len(prefix) :] if line.startswith(prefix) else line.lstrip(" \t>")
                    for line in lines[i : j + 1]
                ]
                out += _fenced(prefix, body)
                i = j + 1
                continue
        m = DISPLAY_OPEN.match(lines[i])
        rest = m.group(2) if m else ""
        if m is None or (rest.strip() and rest.rstrip().endswith("$$")):
            out.append(lines[i])
            i += 1
            continue
        prefix = m.group(1)
        body = [rest.rstrip()] if rest.strip() else []
        j, after = i + 1, None
        while j < len(lines):
            line = lines[j]
            content = line[len(prefix) :] if line.startswith(prefix) else line.lstrip(" \t>")
            if "$$" in content:
                before, _, after = content.partition("$$")
                if before.strip():
                    body.append(before.rstrip())
                break
            body.append(content)
            j += 1
        if after is None:  # never closed: leave it as written
            out.append(lines[i])
            i += 1
            continue
        out += _fenced(prefix, body)
        if after.strip():
            out.append(f"{prefix}{after.strip()}")
        i = j + 1
    return "\n".join(out)


def tidy(text: str) -> str:
    """Markup our renderer reads differently from mkdocs; safe on reviewed text too.

    - `\\[ … \\]` display math → `$$ … $$` (remark-math reads only dollars);
    - `\\\\\\\\` → `\\\\` inside math: mkdocs' Markdown halves the escape before
      MathJax sees it, remark-math does not, so the original's line break
      became two;
    - a heading's mkdocs attribute list without an id (`{ data-toc-label=… }`)
      goes; an `{#id}` stays (links point at it);
    - Jinja `{% raw %}` markers go.

    And what KaTeX refuses where MathJax was lenient (measured 2026-11-12:
    21 of 23 977 formulas failed to render on the site):

    - `\\$` (a dollar sign inside a formula) → `\\text{\\textdollar}`: remark-math
      reads `\\$$` as an escape and loses the formula's end (the library writes
      `\\$` only inside formulas);
    - `eqnarray` → `array{rcl}` (KaTeX has no `eqnarray`; same three columns);
    - `_` inside `\\text{…}` → `\\_`;
    - `\\*` inside a formula → `*` (a Markdown escape mkdocs removed).
    """
    text = JINJA.sub("", text)
    out = []
    for is_code, chunk in split_fences(text):
        if not is_code:
            chunk = DISPLAY_BRACKETS.sub(lambda m: f"$${m.group(1)}$$", chunk)
            chunk = chunk.replace("\\$", "\\text{\\textdollar}")
            chunk = fence_display_math(chunk)
            chunk = re.sub(r"\\(begin|end)\{eqnarray\*?\}", lambda m: _eqnarray(m.group(1)), chunk)
            chunk = TEXT_MODE.sub(
                lambda m: m.group(1) + re.sub(r"(?<!\\)_", r"\\_", m.group(2)) + "}", chunk
            )
            chunk = re.sub(
                r"\$\$.+?\$\$|(?<![\\$])\$[^$\n]+\$",
                lambda m: m.group(0).replace("\\\\\\\\", "\\\\").replace("\\*", "*"),
                chunk,
                flags=re.DOTALL,
            )
            chunk = "\n".join(HEADING_ATTRS.sub(r"\1", line) for line in chunk.split("\n"))
        out.append(chunk)
    return "\n".join(out)


HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
EXPLICIT_ID = re.compile(r"\s*\{#([\w-]+)\}\s*$")
# A heading's own id in the raw original: `{#id}`, `{ #id … }` or `{: #id }`.
OWN_ID = re.compile(r"\s*\{\s*:?\s*#([\w-]+)[^}]*\}\s*$")


def slugify(text: str) -> str:
    """The id mkdocs gave a heading (python-markdown's `toc` slugify).

    The original's cross-article links point at these ids
    (`segment_tree.md#implementation`), so the headings must carry them.
    """
    text = re.sub(r"\$[^$]*\$", lambda m: m.group(0).strip("$"), text)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", text)


def heading_lines(text: str) -> list[int]:
    """Indexes of the heading lines outside fenced code."""
    found, line_no = [], 0
    for is_code, chunk in split_fences(text):
        lines = chunk.split("\n")
        if not is_code:
            found += [line_no + i for i, line in enumerate(lines) if HEADING.match(line)]
        line_no += len(lines)
    return found


def with_heading_ids(text: str, original: str) -> str:
    """Give each heading the id of the original's heading in the same place.

    A translation keeps the original's headings in order, so the n-th heading
    of one is the n-th of the other. When the outlines differ (a level or a
    count), nothing is guessed and the text is returned unchanged.
    """
    lines, orig = text.split("\n"), original.split("\n")
    mine, theirs = heading_lines(text), heading_lines(original)
    levels = [HEADING.match(lines[i]).group(1) for i in mine]  # type: ignore[union-attr]
    their_levels = [HEADING.match(orig[i]).group(1) for i in theirs]  # type: ignore[union-attr]
    if levels != their_levels:
        return text
    for i, j in zip(mine, theirs, strict=True):
        head = HEADING.match(orig[j])
        assert head is not None
        found = EXPLICIT_ID.search(head.group(2))
        auto = slugify(EXPLICIT_ID.sub("", head.group(2)))
        anchor = found.group(1) if found else auto
        own = EXPLICIT_ID.search(lines[i])
        if own and own.group(1) != auto:
            continue  # an id the text chose itself stays
        if anchor:
            lines[i] = f"{EXPLICIT_ID.sub('', lines[i]).rstrip()} {{#{anchor}}}"
    return "\n".join(lines)


ANCHOR_BEFORE_HEADING = re.compile(
    r"^[ \t]*<(?:div|a)\s+(?:id|name)=[\"']([\w-]+)[\"']\s*>\s*</(?:div|a)>[ \t]*\n+(#{1,6}\s[^\n]*?)[ \t]*$",
    re.MULTILINE,
)


PARAGRAPH_ANCHOR = re.compile(r"^[ \t]*<(?:div|a)\s+(?:id|name)=[\"']([\w-]+)[\"']\s*>\s*</(?:div|a)>[ \t]*$")
ANCHOR_LINK = re.compile(r"\]\((/algorithms/[\w-]+/[\w-]+)?#([\w-]+)\)")


def section_anchors(original: str) -> dict[str, str]:
    """`<div id>` anchors in the middle of a section → that section's heading id.

    A heading can carry one id; an anchor before a paragraph has no heading of
    its own, so a link to it is sent to the section it sits in.
    """
    found: dict[str, str] = {}
    current = ""
    lines = original.split("\n")
    for k, line in enumerate(lines):
        head = HEADING.match(line)
        if head:
            own = OWN_ID.search(head.group(2))
            current = own.group(1) if own else slugify(OWN_ID.sub("", head.group(2)))
            continue
        m = PARAGRAPH_ANCHOR.match(line)
        if not m:
            continue
        nxt = next((x for x in lines[k + 1 :] if x.strip()), "")
        nxt_head = HEADING.match(nxt)
        if nxt_head:
            own = OWN_ID.search(nxt_head.group(2))
            if own and own.group(1) != m.group(1):
                found[m.group(1)] = own.group(1)
        elif current:
            found[m.group(1)] = current
    return found


def retarget(text: str, here: str, sections: dict[str, dict[str, str]]) -> str:
    def fix(m: re.Match[str]) -> str:
        page = m.group(1) or here
        anchor = sections.get(page, {}).get(m.group(2), m.group(2))
        return f"]({m.group(1) or ''}#{anchor})"

    return ANCHOR_LINK.sub(fix, text)


def anchors_to_headings(text: str) -> str:
    """`<div id="fermat-euler"></div>` right above a heading → the heading's id.

    The original marks a few sections that way so other articles can link to
    them; our renderer draws no raw HTML, so the id moves onto the heading.
    """

    def move(m: re.Match[str]) -> str:
        if OWN_ID.search(m.group(2)):
            return m.group(2)  # its own id wins; links to the div are retargeted
        return f"{m.group(2).rstrip()} {{#{m.group(1)}}}"

    return ANCHOR_BEFORE_HEADING.sub(move, text)


def normalise(text: str, links: Links) -> str:
    text = text.replace("\r\n", "\n")
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            text = text[end + 5 :]
    text = anchors_to_headings(text)
    text = "\n".join(normalise_blocks(text.split("\n")))
    out = []
    for is_code, chunk in split_fences(text):
        if not is_code:
            chunk = markdown_links(html_to_markdown(chunk, links), links)
        out.append(chunk)
    text = tidy("\n".join(out))
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    return text


def remaining_html(text: str) -> list[str]:
    """Tags left in prose — the renderer would print them as text."""
    found = []
    for is_code, chunk in split_fences(text):
        if is_code:
            continue
        chunk, _ = protect(chunk)
        found += re.findall(r"</?[a-zA-Z][a-zA-Z0-9]*\b[^>\n]*>", chunk)
    return found


# ── build ──────────────────────────────────────────────────────────────────


def load_previous() -> dict[str, dict[str, str]]:
    path = OUT / "articles.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {a["id"]: a.get("written", {}) for a in data["articles"]}


def write_kept(
    path: Path, data: bytes, previous_sha: str | None, report: dict[str, list[str]]
) -> str:
    """Write unless we edited the file since the last build; return the sha written."""
    rel = path.relative_to(ROOT).as_posix()
    if path.exists():
        current = sha256(path.read_bytes())
        if previous_sha is not None and current != previous_sha:
            report["kept"].append(rel)
            return previous_sha
        if current == sha256(data):
            return current
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    report["written"].append(rel)
    return sha256(data)


def build(cpuz: Path, rev: str, upstream: Path) -> dict[str, Any]:
    cpuz_commit = git_rev(cpuz, rev)
    export = json.loads(git_show(cpuz, cpuz_commit, "content/exports/articles.v1.json"))
    import yaml  # local: the tool is run by hand, pyyaml is in the API venv

    meta = {
        a["id"]: a
        for a in yaml.safe_load(
            git_show(cpuz, cpuz_commit, "content/metadata/articles.yml")
        )["articles"]
    }
    snapshot = json.loads(git_show(cpuz, cpuz_commit, "content/SNAPSHOT.json"))
    upstream_commit = snapshot["upstream_commit"]
    if git_rev(upstream, "HEAD") != upstream_commit:
        sys.exit(f"cp-algorithms checkout must be at {upstream_commit}")

    asset_paths = [
        p[len("content/articles/") :]
        for p in subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", cpuz_commit, "content/articles"],
            cwd=cpuz,
            capture_output=True,
            check=True,
            text=True,
        ).stdout.splitlines()
        if not p.endswith(".md")
    ]
    routes = {
        a[
            "path"
        ]: f"{ROUTE}/{category_slug(a['path'].split('/')[0])}/{article_slug(Path(a['path']).stem)}"
        for a in export["articles"]
    }
    media = {
        p: f"{MEDIA_URL}/{category_slug(p.split('/')[0])}/{p.split('/')[-1]}"
        for p in asset_paths
    }

    previous = load_previous()
    report: dict[str, list[str]] = {
        "written": [],
        "kept": [],
        "html_left": [],
        "unresolved": [],
    }

    for p in asset_paths:
        target = MEDIA / category_slug(p.split("/")[0]) / p.split("/")[-1]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(git_show(cpuz, cpuz_commit, f"content/articles/{p}"))

    # Paragraph anchors of every original, by the article's address.
    sections = {
        routes[a['path']]: section_anchors(
            anchors_to_headings(
                (upstream / meta[a['id']]['source']['file']).read_text(encoding='utf-8')
            )
        )
        for a in export['articles']
    }
    articles = []
    for a in sorted(export["articles"], key=lambda x: int(x["index"])):
        m = meta[a["id"]]
        category = a["path"].split("/")[0]
        slug = article_slug(Path(a["path"]).stem)
        written_before = previous.get(a["id"], {})
        written: dict[str, str] = {}

        uz_links = Links(routes, media, a["path"])
        uz = normalise(a["markdown"], uz_links)
        upstream_file = m["source"]["file"]
        en_raw = (upstream / upstream_file).read_text(encoding="utf-8")
        # The original sits under `src/`; its relative links mean the same tree.
        en_links = Links(routes, media, upstream_file.removeprefix("src/"))
        en = normalise(en_raw, en_links)
        # An image only the original has: take it from cp-algorithms too.
        for ref in re.findall(r"\]\((/algorithms-media/[^)\s]+)", en):
            target = MEDIA / ref.removeprefix(MEDIA_URL + "/")
            if not target.exists():
                report["unresolved"].append(f"{a['id']} en image {ref}")
        for ref in en_links.unresolved:
            src = (upstream / Path(upstream_file).parent / ref).resolve()
            if src.suffix.lower() in {".png", ".svg", ".jpg", ".gif"} and src.exists():
                target = MEDIA / category_slug(category) / src.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, target)
                en = en.replace(
                    f"]({ref})", f"]({MEDIA_URL}/{category_slug(category)}/{src.name})"
                )
            else:
                report["unresolved"].append(f"{a['id']} en {ref}")
        report["unresolved"] += [f"{a['id']} uz {u}" for u in uz_links.unresolved]
        # The original's headings get mkdocs' ids, and the translation the same.
        en = with_heading_ids(en, en)
        uz = with_heading_ids(uz, en)
        here = routes[a['path']]
        en = retarget(en, here, sections)
        uz = retarget(uz, here, sections)

        for lang, text in (("uz", uz), ("en", en)):
            left = remaining_html(text)
            if left:
                report["html_left"].append(f"{a['id']} {lang}: {sorted(set(left))[:5]}")
            path = OUT / lang / category_slug(category) / f"{slug}.md"
            written[lang] = write_kept(
                path, text.encode("utf-8"), written_before.get(lang), report
            )

        tr = m["translation"]
        articles.append(
            {
                "id": a["id"],
                "slug": slug,
                "category": category_slug(category),
                "category_en": a["category"],
                "category_uz": a["category_uz"],
                "subcategory_en": a.get("subcategory") or "",
                "subcategory_uz": a.get("subcategory_uz") or "",
                "level": a["difficulty"],
                "order": int(a["index"]),
                "title": tr["title"],
                "idea": tr.get("idea") or "",
                "complexity": tr.get("complexity") or "",
                "uses": tr.get("uses") or "",
                "translator": ", ".join(tr.get("translators") or []),
                "translated_at": str(tr.get("translated_at") or ""),
                "source": {
                    "title": m["source"]["title"],
                    "url": m["source"]["url"],
                    "file": upstream_file,
                    "commit": m["source"]["commit"],
                    "license": m["source"]["license"],
                },
                "practice": [
                    {
                        "platform": link.get("platform") or "",
                        "title": link.get("title") or "",
                        "url": link["url"],
                        "key": exercise_key(link["url"]),
                        "note": link.get("note") or "",
                    }
                    for link in a.get("practice_links") or []
                ],
                "written": written,
            }
        )

    data = {
        "schema": "rankwant.cpuz-snapshot.v1",
        "cpuz_repository": "https://github.com/cp-uz/cp-uz",
        "cpuz_commit": cpuz_commit,
        "snapshot_commit": snapshot["commit"],
        "upstream_repository": snapshot["upstream_repository"],
        "upstream_commit": upstream_commit,
        "license": "CC-BY-SA-4.0",
        "articles": articles,
    }
    (OUT / "articles.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    # The glossary (ADR-0062 § 3: a page and tooltips): English term, Uzbek
    # term, aliases and a one-line note, as cp.uz has them.
    glossary = json.loads(git_show(cpuz, cpuz_commit, "content/metadata/glossary.json"))
    (OUT / "glossary.json").write_text(
        json.dumps(glossary, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n"
    )
    for name in ("LICENSE-CC-BY-SA-4.0.txt", "ATTRIBUTION.md"):
        (OUT / name).write_bytes(git_show(cpuz, cpuz_commit, f"content/{name}"))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--cpuz", type=Path, required=True, help="a cp-uz git clone")
    parser.add_argument("--cpuz-rev", required=True, help="the pinned cp-uz commit")
    parser.add_argument(
        "--upstream",
        type=Path,
        required=True,
        help="a cp-algorithms checkout at the pinned commit",
    )
    args = parser.parse_args()
    report = build(args.cpuz, args.cpuz_rev, args.upstream)
    print(
        f"written {len(report['written'])}, kept (edited by us) {len(report['kept'])}"
    )
    for key in ("kept", "html_left", "unresolved"):
        for line in report[key]:
            print(f"  {key}: {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
