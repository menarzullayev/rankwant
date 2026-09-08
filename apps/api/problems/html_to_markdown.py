"""HTML + MathJax → Markdown + KaTeX.

Import qilinadigan arxivlar masala matnini HTML da saqlaydi, bizniki esa
Markdown (`remark-gfm` + `remark-math` → KaTeX). Formula `\\(…\\)` va
`\\[…\\]` ichida keladi, bizda esa `$…$` va `$$…$$`.

Nega tashqi kutubxona emas: kiruvchi teg to'plami tor va aniq
(`p`, `strong`, `em`, `ul/ol/li`, `pre/code`, `table`, `img`, `a`,
`span.mathjax-latex`), stdlib `html.parser` esa bog'liqlik qo'shmasdan
uni to'liq qoplaydi. Muhimi — formulani BUZMASLIK: uning ichida `*`,
`_`, `\\` belgilari bor va ular Markdown'da boshqa ma'no bildiradi,
shuning uchun matematik qism alohida ajratib olinadi va qochirilmaydi.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser

#: Markdown'da ma'noga ega belgilar. Matematikaning TASHQARISIDA qochiriladi.
_ESCAPE = re.compile(r"([\\`*_\[\]#$])")

_SKIP = {"script", "style", "head", "meta", "link"}


class _Converter(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self._skip_depth = 0
        self._math: list[str] | None = None
        self._pre = 0
        self._fence: int | None = None
        self._code = 0
        self._list: list[str] = []
        self._href: str | None = None
        self._row: list[list[str]] = []
        self._cell: list[str] | None = None
        self._header_row = False
        # KEP matnida `<strong><strong>x</strong></strong>` va
        # `<strong>&nbsp;</strong>` uchraydi. Birinchisi `****` berardi —
        # Markdown uni qalin emas, adabiy yulduzcha deb o'qiydi;
        # ikkinchisi bo'sh ta'kid qoldirardi. Ikkalasini ham chiqarish
        # payti tutamiz: regex bilan tozalash `**qalin**` ni ham yeb
        # qo'yardi.
        self._depth: dict[str, int] = {"**": 0, "*": 0}
        self._opened_at: dict[str, int] = {}
        #: Yopilgan, lekin hali yozilmagan ta'kid: (belgi, orqadagi bo'shliq).
        self._pending: tuple[str, str] | None = None

    # ── yordamchilar ────────────────────────────────────────────────
    @property
    def _buf(self) -> list[str]:
        return self.out if self._cell is None else self._cell

    def _emit(self, text: str) -> None:
        self._flush()
        self._buf.append(text)

    def _newline(self, count: int = 1) -> None:
        self._flush()
        buf = self._buf
        have = 0
        for chunk in reversed(buf):
            body = chunk.rstrip("\n")
            have += len(chunk) - len(body)
            if body.strip():
                break
            if body:
                return
        else:
            return  # butunlay bo'sh — boshida bo'sh qator kerak emas
        if have < count:
            buf.append("\n" * (count - have))

    # ── teglar ──────────────────────────────────────────────────────
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = dict(attrs)
        if tag in _SKIP:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return

        if tag == "span" and "mathjax-latex" in (attr.get("class") or ""):
            self._math = []
            return

        match tag:
            case "br":
                self._emit("  \n")
            case "p" | "div":
                self._newline(2)
            case "h1" | "h2" | "h3" | "h4" | "h5" | "h6":
                self._newline(2)
                self._emit("#" * int(tag[1]) + " ")
            case "strong" | "b":
                self._open("**")
            case "em" | "i":
                self._open("*")
            # `<pre><code class="language-python">` — tilni yo'qotmaymiz,
            # aks holda import qilingan kod rangsiz qolardi.
            case "code" if self._pre:
                lang = (attr.get("class") or "").removeprefix("language-").strip()
                if lang.isalnum() and self._fence is not None:
                    self.out[self._fence] = f"```{lang}\n"
            case "code":
                self._code += 1
                self._emit("`")
            case "pre":
                self._pre += 1
                self._newline(2)
                self._emit("```\n")
                self._fence = len(self.out) - 1 if self._cell is None else None
            case "ul" | "ol":
                self._list.append(tag)
                self._newline(2)
            case "li":
                self._newline(1)
                self._emit("1. " if self._list and self._list[-1] == "ol" else "- ")
            case "a":
                self._href = attr.get("href")
                self._emit("[")
            case "img":
                src = attr.get("src") or ""
                alt = (attr.get("alt") or "rasm").replace("]", "")
                if src:
                    self._newline(2)
                    self._emit(f"![{alt}]({src})")
                    self._newline(2)
            case "table":
                self._newline(2)
            case "tr":
                self._row = []
                self._header_row = False
            case "th" | "td":
                self._header_row = self._header_row or tag == "th"
                self._row.append([])
                self._cell = self._row[-1]

    def handle_endtag(self, tag: str) -> None:
        if tag in _SKIP:
            self._skip_depth = max(0, self._skip_depth - 1)
            return
        if self._skip_depth:
            return

        if tag == "span" and self._math is not None:
            self._flush_math()
            return

        match tag:
            case "strong" | "b":
                self._close("**")
            case "em" | "i":
                self._close("*")
            case "code" if not self._pre:
                self._code = max(0, self._code - 1)
                self._emit("`")
            case "pre":
                self._pre = max(0, self._pre - 1)
                if self._fence is not None:
                    # Yopuvchi fence oldidagi bo'sh qator kod blokining
                    # ichida ortiqcha satr bo'lib ko'rinardi.
                    body = "".join(self.out[self._fence + 1 :]).rstrip("\n")
                    del self.out[self._fence + 1 :]
                    self.out.append(body)
                    self._fence = None
                self._emit("\n```")
                self._newline(2)
            case "ul" | "ol":
                if self._list:
                    self._list.pop()
                self._newline(2)
            case "a":
                self._emit(f"]({self._href or ''})")
                self._href = None
            case "th" | "td":
                self._cell = None
            case "tr":
                self._flush_row()
            case "p" | "div" | "h1" | "h2" | "h3" | "h4" | "h5" | "h6":
                self._newline(2)

    def close(self) -> None:
        super().close()
        self._flush()

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        if self._math is not None:
            self._math.append(data)
            return
        # `&nbsp;` matnda qattiq bo'shliq bo'lib keladi — oddiy bo'shliqqa
        # aylantiramiz, aks holda Markdown uni matn deb qabul qiladi.
        data = data.replace("\xa0", " ")
        if self._pre:
            # Ochilish fenceidan keyingi bo'sh qator ortiqcha.
            if self._fence is not None and not any(self.out[self._fence + 1 :]):
                data = data.lstrip("\n")
            self._emit(data)
            return

        text = data
        if not text.strip():
            buf = self._buf
            if buf and not buf[-1].endswith((" ", "\n")):
                self._emit(" ")
            return
        self._emit(text if self._code else _ESCAPE.sub(r"\\\1", text))

    # ── ta'kid ──────────────────────────────────────────────────────
    def _flush(self) -> None:
        if self._pending is None:
            return
        marker, tail = self._pending
        self._pending = None
        self._buf.append(marker)
        if tail:
            self._buf.append(tail)

    def _open(self, marker: str) -> None:
        if self._depth[marker] == 0:
            # `</strong><strong>` — ikki qo'shni ta'kid `a****b` beradi va
            # remark uni QALIN EMAS, oddiy yulduzcha deb o'qiydi
            # (tekshirilgan). Yopuvchi hali yozilmagani uchun ikkalasini
            # bitta ta'kidga qo'shib yuboramiz.
            if self._pending == (marker, ""):
                self._pending = None
                self._depth[marker] = 1
                return
            self._flush()
            self._opened_at[marker] = len(self._buf)
            self._buf.append(marker)
        self._depth[marker] += 1

    def _close(self, marker: str) -> None:
        self._depth[marker] = max(0, self._depth[marker] - 1)
        if self._depth[marker]:
            return
        self._flush()
        buf = self._buf
        start = self._opened_at.pop(marker, len(buf))
        inner = "".join(buf[start + 1 :])
        # Harf-raqamsiz ta'kid — «.» yoki «→» ustidagi qalinlik muharrir
        # shovqini. Uni saqlashning imkoni ham yo'q: qo'shni ta'kid
        # yonida Markdown `**a*.***` ni umuman ifodalay olmaydi.
        if not any(char.isalnum() for char in inner):
            del buf[start:]
            if inner.strip():
                buf.append(inner)
            elif inner and buf and not buf[-1].endswith((" ", "\n")):
                buf.append(" ")
            return
        lead = inner[: len(inner) - len(inner.lstrip())]
        tail = inner[len(inner.rstrip()) :]
        buf[start:] = [lead, marker, inner.strip()]
        self._opened_at[marker] = start + 1
        self._pending = (marker, tail)

    # ── matematika ──────────────────────────────────────────────────
    def _flush_math(self) -> None:
        # Qattiq bo'shliq formulada ma'no bermaydi, KaTeX esa uni
        # «tanilmagan belgi» deb ogohlantiradi.
        raw = "".join(self._math or []).replace("\xa0", " ").strip()
        self._math = None
        if not raw:
            return
        display = raw.startswith("\\[")
        body = raw
        for opener, closer in (("\\(", "\\)"), ("\\[", "\\]"), ("$$", "$$"), ("$", "$")):
            if body.startswith(opener) and body.endswith(closer):
                body = body[len(opener) : len(body) - len(closer)]
                break
        body = body.strip()
        if not body:
            return
        self._emit(f"$${body}$$" if display else f"${body}$")

    def _flush_row(self) -> None:
        if not self._row:
            return
        cells = ["".join(c).strip() or " " for c in self._row]
        self._newline(1)
        self._emit("| " + " | ".join(cells) + " |")
        if self._header_row:
            self._emit("\n|" + "|".join(" --- " for _ in cells) + "|")
        self._row = []


def html_to_markdown(source: str | None) -> str:
    """HTML matnni Markdown'ga aylantiradi. Bo'sh kirish — bo'sh chiqish."""
    if not source:
        return ""
    parser = _Converter()
    # KEP matni CRLF da keladi; `\r` bo'sh qator bo'lib ko'rinardi.
    parser.feed(source.replace("\r\n", "\n").replace("\r", "\n"))
    parser.close()
    text = "".join(parser.out)
    # Ketma-ket bo'sh qatorlarni ikkitaga tushiramiz va chetlarni tozalaymiz.
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
