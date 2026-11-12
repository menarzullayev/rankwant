"""The tutor never hands out a ready solution (decision ②, ADR-0065 § 2.4).

The system prompt says so, but a prompt is a request, not a guarantee: a
student can talk a model into writing code. So every answer passes this
filter before it is stored. A fenced code block longer than
`MAX_CODE_LINES` non-blank lines is cut out; a short one stays, because
pointing at the line of the student's own code that is wrong is the point
of «Nega xato?».
"""

from __future__ import annotations

import re

#: The longest code block an answer may keep.
MAX_CODE_LINES = 3
#: What stands where a block was cut; the web replaces it with a sentence
#: in the reader's language.
REMOVED = "[[code-removed]]"

_FENCE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})")


def strip_solution_code(text: str) -> tuple[str, int]:
    """Cut long fenced code blocks; return the text and how many were cut.

    An unclosed fence runs to the end of the answer, as Markdown renders it.
    """
    out: list[str] = []
    block: list[str] = []
    fence = ""
    removed = 0

    def flush(closed: bool) -> None:
        nonlocal removed
        body = block[1:-1] if closed else block[1:]
        if sum(1 for line in body if line.strip()) > MAX_CODE_LINES:
            out.append(REMOVED)
            removed += 1
        else:
            out.extend(block)

    for line in text.split("\n"):
        if not fence:
            m = _FENCE.match(line)
            if m:
                fence = m.group(1)
                block = [line]
            else:
                out.append(line)
            continue
        block.append(line)
        m = _FENCE.match(line)
        if (
            m
            and m.group(1)[0] == fence[0]
            and len(m.group(1)) >= len(fence)
            and not line.strip()[len(m.group(1)) :]
        ):
            flush(closed=True)
            fence = ""
            block = []
    if fence:
        flush(closed=False)
    return "\n".join(out), removed
