"""The old ↔ new Uzbek alphabet converter (ADR-0059).

The cases live in `packages/shared/src/alphabet-cases.json` and the
TypeScript twin runs the same file (`apps/web/tests/unit/alphabet.test.ts`).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.alphabet import is_foreign_word, to_new_alphabet, to_old_alphabet

CASES_FILE = Path(__file__).resolve().parents[3] / "packages/shared/src/alphabet-cases.json"
CASES = json.loads(CASES_FILE.read_text(encoding="utf-8"))["cases"]


@pytest.mark.parametrize("case", [c for c in CASES if "old" in c], ids=lambda c: c["old"][:30])
def test_old_to_new(case: dict[str, str]) -> None:
    assert to_new_alphabet(case["old"]) == case["new"]


@pytest.mark.parametrize("case", [c for c in CASES if "back" in c], ids=lambda c: c["new"][:30])
def test_new_to_old(case: dict[str, str]) -> None:
    assert to_old_alphabet(case["new"]) == case["back"]


def test_new_text_is_left_as_it_is() -> None:
    text = "Masala şarti: ikki sonniñ"
    assert to_new_alphabet(to_new_alphabet("Shart o'qing")) == "Şart öqing"
    assert to_new_alphabet(text) == text


@pytest.mark.parametrize("word", ["GitHub", "SSH", "Shift", "Cache", "Python", "Türkçe"])
def test_foreign_words(word: str) -> None:
    assert is_foreign_word(word)


@pytest.mark.parametrize("word", ["Shart", "o'qish", "chiqish", "yig'indi", "SHARTLAR"])
def test_uzbek_words(word: str) -> None:
    assert not is_foreign_word(word)


FOLDS = json.loads(CASES_FILE.read_text(encoding="utf-8"))["fold"]


@pytest.mark.parametrize("case", FOLDS, ids=lambda c: c["text"])
def test_search_fold_matches_the_shared_cases(case: dict[str, str]) -> None:
    from core.search import normalize_search

    assert normalize_search(case["text"]) == case["folded"]
