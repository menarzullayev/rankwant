"""Judge shartnomasi: protocol.md ↔ Go struct ↔ Python JudgeJob.

Nega kerak: API va judge alohida sinaladi (API judge'ni mock qiladi,
bake-off harness job'ni o'zi quradi), shuning uchun ular orasidagi
nomuvofiqlik ikkala to'plamda ham ko'rinmaydi. Amalda ikkita shunday
nomuvofiqlik topildi:

  * API `input_ref`/`output_ref` yuborardi, judge `input`/`expected`
    kutardi — HAR submission WA olardi;
  * judge natijada `attempt_id` qaytarmasdi — verdict hech qachon
    yozilmasdi, urinish PENDING qolardi.

Ishlatish:  python3 tools/check_contract.py
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
PROTOCOL = REPO / "services/bakeoff/protocol.md"
GO_PROTOCOL = REPO / "services/judge-go/protocol.go"
PY_PROVIDER = REPO / "apps/api/judging/provider.py"
PY_SERVICES = REPO / "apps/api/judging/services.py"

problems: list[str] = []


def json_blocks(text: str) -> list[dict]:
    return [
        json.loads(m)
        for m in re.findall(r"```json\n(.*?)\n```", text, re.S)
        if m.lstrip().startswith("{")
    ]


def go_json_tags(text: str) -> set[str]:
    return set(re.findall(r'json:"([^",]+)', text))


def main() -> int:
    protocol = PROTOCOL.read_text()
    blocks = json_blocks(protocol)
    if len(blocks) < 2:
        print(f"protocol.md da Job va Result bloklari topilmadi ({len(blocks)} ta)")
        return 1
    job_block, result_block = blocks[0], blocks[1]

    go_tags = go_json_tags(GO_PROTOCOL.read_text())
    py_source = PY_PROVIDER.read_text() + PY_SERVICES.read_text()

    for name, block in (("Job", job_block), ("Result", result_block)):
        for key in block:
            if key not in go_tags:
                problems.append(f"{name}.{key} — protocol.md da bor, judge-go da json tag yo'q")
            if f'"{key}"' not in py_source:
                problems.append(f"{name}.{key} — protocol.md da bor, API kodida ishlatilmagan")

    # Test maydonlari alohida: judge S3 havolasini ham, inline matnni ham
    # qabul qiladi, lekin API HAVOLA yuboradi.
    for key in ("input_ref", "output_ref"):
        if key not in go_tags:
            problems.append(f"tests[].{key} — API yuboradi, judge-go o'qimaydi")

    if problems:
        print("Shartnoma nomuvofiqligi:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print(f"Shartnoma mos: Job {len(job_block)} maydon, Result {len(result_block)} maydon ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
