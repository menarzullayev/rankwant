"""A statement as text read aloud (ADR-0064, problems.speech)."""

from __future__ import annotations

from typing import Any

import pytest

from problems import speech as s
from problems.speech import Parts


def parts(statement: str = "", title: str = "T", inp: str = "", out: str = "") -> Parts:
    return {"title": title, "statement": statement, "input_format": inp, "output_format": out}


@pytest.mark.parametrize(
    ("n", "words"),
    [
        (0, "nol"),
        (7, "yetti"),
        (11, "o'n bir"),
        (248, "ikki yuz qirq sakkiz"),
        (1000, "ming"),
        (1234, "ming ikki yuz o'ttiz to'rt"),
        (2021, "ikki ming yigirma bir"),
        (1_000_000_007, "bir milliard yetti"),
        (-5, "minus besh"),
    ],
)
def test_numbers_are_words(n: int, words: str) -> None:
    assert s.number(n) == words


def test_ordinals_follow_the_vowel() -> None:
    assert [s.ordinal(n) for n in (1, 2, 4, 6, 9, 10)] == [
        "birinchi",
        "ikkinchi",
        "to'rtinchi",
        "oltinchi",
        "to'qqizinchi",
        "o'ninchi",
    ]


@pytest.mark.parametrize(
    ("formula", "spoken"),
    [
        (r"1 \le n \le 10^5", "en birdan o'nning beshinchi darajasigacha"),
        (r"n(1 \le n \le 10^4).", "en birdan o'nning to'rtinchi darajasigacha."),
        (
            r"-10^9 \le a, b \le 10^9",
            "a, be minus o'nning to'qqizinchi darajasidan o'nning to'qqizinchi darajasigacha",
        ),
        (
            r"a_n = (248n^2 + 28n) \bmod 10^9",
            "a en teng ikki yuz qirq sakkiz en kvadrat qo'shuv "
            "yigirma sakkiz en modul o'nning to'qqizinchi darajasi",
        ),
        (r"\frac{n(n+1)}{2}", "en en qo'shuv bir bo'linib ikki"),
        (r"\frac{1}{\sqrt{n}}", "bir bo'linib enning ildizi"),
        (r"\sum_{i=1}^{n} a_i", "i teng birdan engacha yig'indi a i"),
        (r"x \pmod{12}", "iks modul o'n ikki"),
        (r"\\pmod{7}", "modul yetti"),
        (r"0.5", "nol butun besh"),
    ],
)
def test_formulas_are_spoken(formula: str, spoken: str) -> None:
    assert s.speak_math(formula) == spoken


def test_a_monster_formula_is_one_phrase_and_never_fails() -> None:
    deep = r"\frac{" * 30 + "x" + "}{2}" * 30
    assert s.speak_math(deep) == s.COMPLEX
    # Whatever breaks inside a formula, the statement is still read.
    text = s.spoken(parts(f"Boshi ${deep}$ oxiri."))
    assert text.startswith("T. Boshi") and text.endswith("oxiri.")


def test_mathjax_delimiters_and_escaped_ones_are_formulas() -> None:
    text = s.spoken(parts(r"Har bir \\(a_i\\) son \(1 \le n \le 10\) va \[x^2\] ham."))
    assert "\\" not in text
    assert "a i" in text and "en birdan o'ngacha" in text and "iks kvadrat" in text


def test_imported_apostrophes_become_real_ones() -> None:
    text = s.spoken(parts("O\\`zbek o\\z bo`lib gʻalaba qo’shiq."))
    assert "O'zbek o'z bo'lib g'alaba qo'shiq" in text


def test_a_heading_that_repeats_the_title_is_read_once() -> None:
    text = s.spoken(parts("## A + B\n\nIkki son berilgan.", title="A + B"))
    assert text == "A + B. Ikki son berilgan."


def test_sections_are_labelled_and_markdown_is_silent() -> None:
    text = s.spoken(
        parts(
            "**Muhim**: [havola](https://x.uz) va ![rasm](data:image/png;base64,AAAA)\n\n"
            "```\nkod\n```\n| a | b |\n|---|---|\n| 1 | 2 |",
            inp="Bitta `n`.",
            out="Javob.",
        )
    )
    assert "Kiruvchi ma'lumot. Bitta en." in text
    assert "Chiquvchi ma'lumot. Javob." in text
    assert "https" not in text and "base64" not in text and "kod" not in text
    assert "*" not in text and "|" not in text


def test_nothing_unread_reaches_the_voice() -> None:
    text = s.spoken(parts(r"Format: {id} - {price}, a ∈ {0,1}, \weird $x$ ^"))
    assert not any(ch in text for ch in "\\{}$^")
    assert "tegishli" in text


def test_the_cache_key_names_model_and_text() -> None:
    a = s.cache_key("navoiy-xotirjam", "salom")
    assert a == s.cache_key("navoiy-xotirjam", "salom")
    assert a != s.cache_key("navoiy-xotirjam", "salom.")
    assert a != s.cache_key("boshqa-model", "salom")
    assert len(a) == 40


# ── the endpoint ─────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestSpeechEndpoint:
    def test_a_public_problem_gives_its_text_and_audio_name(self, problem) -> None:
        from django.conf import settings
        from rest_framework.test import APIClient

        response = APIClient().get(f"/api/v1/problems/{problem.slug}/speech/")
        assert response.status_code == 200, response.content
        body = response.json()
        assert body["text"].startswith("A+B.")
        assert body["model"] == settings.TTS_MODEL
        assert body["key"] == s.cache_key(settings.TTS_MODEL, body["text"])
        assert body["chars"] == len(body["text"])

    def test_a_contest_problem_before_the_start_has_no_text(self) -> None:
        from rest_framework.test import APIClient

        from tests.test_contest_problems import held_problem, make_contest

        hidden = held_problem(make_contest(starts_in=60))
        assert APIClient().get(f"/api/v1/problems/{hidden.slug}/speech/").status_code == 404

    def test_the_voice_reads_an_uzbek_translation_or_nothing(self, problem) -> None:
        from rest_framework.test import APIClient

        from problems.models import ProblemTranslation

        problem.statement_locale = "ru"
        problem.save(update_fields=["statement_locale"])
        url = f"/api/v1/problems/{problem.slug}/speech/"
        assert APIClient().get(url).status_code == 404
        ProblemTranslation.objects.create(
            problem=problem, locale="uz", title="Yig'indi", statement="Ikki $n$ son."
        )
        body = APIClient().get(url).json()
        assert body["text"] == "Yig'indi. Ikki en son."


# ── phase 2: pieces, the queue and the audio (ADR-0064 § 5) ────────────


def test_pieces_keep_every_word_and_grow_from_a_short_first() -> None:
    text = " ".join(f"Bu {i}-gap bo'lib, u bir oz uzunroq yozilgan." for i in range(40))
    pieces = s.segments(text)
    assert all(
        len(p) <= s._cap(i, s.FIRST_SEGMENT_CHARS, s.SEGMENT_CHARS) for i, p in enumerate(pieces)
    )
    assert " ".join(pieces).split() == text.split()
    long = "so'z " * 200
    assert all(len(p) <= s.SEGMENT_CHARS for p in s.segments(long))
    assert " ".join(s.segments(long)).split() == long.split()


def test_a_title_is_not_left_alone_before_a_long_sentence() -> None:
    # Measured 2026-11-12: «Oraliq yig'indisi.» went alone (18 chars) before
    # a 384-character piece — about 20 s of silence for the first listener.
    title = "Oraliq yig'indisi."
    body = "Massivda en ta butun son berilgan, " * 11 + "so'rovlarga javob bering."
    pieces = s.segments(f"{title} {body}")
    assert pieces[0].startswith(title)
    assert len(pieces[0]) > s.FIRST_SEGMENT_CHARS * 0.6
    assert len(pieces[1]) <= s._cap(1, s.FIRST_SEGMENT_CHARS, s.SEGMENT_CHARS)


@pytest.fixture
def voice(settings, monkeypatch):  # type: ignore[no-untyped-def]
    from problems import speech_audio
    from problems import tasks as speech_tasks

    settings.TTS_URL = "http://tts.test"
    store: dict[str, bytes] = {}
    claimed: set[str] = set()
    queued: list[str] = []
    monkeypatch.setattr(speech_audio, "exists", lambda key: key in store)
    monkeypatch.setattr(speech_audio, "put", lambda key, data: store.__setitem__(key, data))
    monkeypatch.setattr(speech_audio, "get", lambda key: store.get(key))

    def claim(key: str) -> bool:
        if key in claimed:
            return False
        claimed.add(key)
        return True

    monkeypatch.setattr(speech_audio, "claim", claim)
    monkeypatch.setattr(
        speech_tasks.synthesize_speech, "delay", lambda key, text: queued.append(key)
    )
    return store, queued


@pytest.mark.django_db
def test_without_a_voice_service_there_is_no_player(problem: Any) -> None:
    from rest_framework.test import APIClient

    data = APIClient().get(f"/api/v1/problems/{problem.slug}/speech/").data
    assert data["available"] is False
    assert all(not p["ready"] and p["url"] is None for p in data["pieces"])
    r = APIClient().post(f"/api/v1/problems/{problem.slug}/speech/generate/")
    assert r.status_code == 503
    assert r.data["error"]["code"] == "voice_unavailable"


@pytest.mark.django_db
def test_generate_queues_each_missing_piece_once(problem: Any, voice: Any) -> None:
    from rest_framework.test import APIClient

    store, queued = voice
    url = f"/api/v1/problems/{problem.slug}/speech/"
    pieces = APIClient().get(url).data["pieces"]
    store[pieces[0]["key"]] = b"OggS"
    r = APIClient().post(url + "generate/")
    assert r.status_code == 202
    assert queued == [p["key"] for p in pieces[1:]]
    assert r.data["pieces"][0]["url"] == f"/api/v1/speech/{pieces[0]['key']}.mp3"
    APIClient().post(url + "generate/")
    assert queued == [p["key"] for p in pieces[1:]]  # asked for already: not queued again


@pytest.mark.django_db
def test_audio_piece_is_served_for_a_year(voice: Any) -> None:
    from rest_framework.test import APIClient

    store, _ = voice
    key = "a" * 40
    store[key] = b"OggS-audio"
    r = APIClient().get(f"/api/v1/speech/{key}.mp3")
    assert r.status_code == 200
    assert r["Content-Type"] == "audio/mpeg"
    assert "immutable" in r["Cache-Control"]
    assert APIClient().get(f"/api/v1/speech/{key}.ogg").status_code == 404
    assert APIClient().get("/api/v1/speech/..%2F..%2Fsecret.mp3").status_code == 404


def test_task_keeps_audio_only_from_the_named_voice(settings, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    import io
    import urllib.request

    from problems import speech_audio, tasks

    settings.TTS_URL = "http://tts.test"
    settings.TTS_MODEL = "navoiy-xotirjam-fleurs"
    stored: dict[str, bytes] = {}
    monkeypatch.setattr(speech_audio, "exists", lambda key: False)
    monkeypatch.setattr(speech_audio, "put", lambda key, data: stored.__setitem__(key, data))

    class Response(io.BytesIO):
        def __init__(self, model: str) -> None:
            super().__init__(b"OggS")
            self.headers = {"X-Model": model}

        def __enter__(self) -> Response:
            return self

        def __exit__(self, *exc: object) -> None:
            return None

    monkeypatch.setattr(
        urllib.request, "urlopen", lambda req, timeout: Response("navoiy-xotirjam-fleurs")
    )
    assert tasks.synthesize_speech("k1", "salom") == "made"
    monkeypatch.setattr(
        urllib.request, "urlopen", lambda req, timeout: Response("navoiy-xursand-saidakbar")
    )
    assert tasks.synthesize_speech("k2", "salom") == "model_mismatch"
    assert list(stored) == ["k1"]


def test_pieces_go_to_the_tts_queue(settings) -> None:  # type: ignore[no-untyped-def]
    assert settings.CELERY_TASK_ROUTES["problems.synthesize_speech"] == {"queue": "tts"}
    assert settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["speech"]


@pytest.mark.django_db
def test_detail_says_whether_the_page_offers_the_voice(problem: Any, settings: Any) -> None:
    from rest_framework.test import APIClient

    settings.TTS_URL = ""
    assert APIClient().get(f"/api/v1/problems/{problem.slug}/").data["voice"] is False
    settings.TTS_URL = "http://tts.test"
    assert APIClient().get(f"/api/v1/problems/{problem.slug}/").data["voice"] is True
