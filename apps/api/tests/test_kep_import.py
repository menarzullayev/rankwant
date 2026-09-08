"""KEP.uz importi — HTML→Markdown konvertori va xaritalash.

Tarmoqqa chiqmaydi: `kep.fetch` almashtiriladi. Qamrov aynan import
paytida ko'rilgan HAQIQIY nosozliklarga qaratilgan — ichma-ich
`<strong>`, `&nbsp;` li bo'sh ta'kid, CRLF va kod bloki tili.
"""

from __future__ import annotations

from typing import Any

import pytest

from core.models import User
from problems import kep
from problems.html_to_markdown import html_to_markdown
from problems.models import Language, Problem, ProblemLanguage, SimilarProblem, Topic


class TestHtmlToMarkdown:
    def test_matematika_katex_ga_otadi(self):
        source = '<p>Son <span class="mathjax-latex">\\(a\\)</span> berilgan.</p>'
        assert html_to_markdown(source) == "Son $a$ berilgan."

    def test_blok_matematika_ikki_dollar(self):
        source = '<p><span class="mathjax-latex">\\[x^2\\]</span></p>'
        assert html_to_markdown(source) == "$$x^2$$"

    def test_ichma_ich_strong_bitta_juft_beradi(self):
        # `****` Markdown'da qalin emas, adabiy yulduzcha bo'lib qolardi.
        source = "<p><strong><strong>b</strong></strong></p>"
        assert html_to_markdown(source) == "**b**"

    def test_qoshni_takidlar_birlashadi(self):
        # `**n****(n < 1000).**` ni remark qalin EMAS, oddiy yulduzcha
        # deb o'qiydi — tekshirilgan.
        source = "<p>son <strong>n</strong><strong>(n &lt; 1000).</strong></p>"
        assert html_to_markdown(source) == "son **n(n < 1000).**"

    def test_harf_raqamsiz_takid_belgisiz_qoladi(self):
        source = "<p><strong>ShopCard</strong><strong><em>.</em></strong></p>"
        assert html_to_markdown(source) == "**ShopCard.**"

    def test_matndagi_dollar_qochiriladi(self):
        # Qochirilmasa `$5 va $7` orasi formulaga aylanardi.
        source = "<p>narx $5 va $7</p>"
        assert html_to_markdown(source) == "narx \\$5 va \\$7"

    def test_bosh_takid_yoqoladi(self):
        source = "<p><strong>&nbsp;</strong>matn</p>"
        assert html_to_markdown(source) == "matn"

    def test_takid_chetidagi_boshliq_tashqariga_chiqadi(self):
        # `** Django**` delimiter bo'sh joyga tegib turadi — qalin bo'lmaydi.
        source = "<p>Sizga<strong> Django</strong> freymwork</p>"
        assert html_to_markdown(source) == "Sizga **Django** freymwork"

    def test_kod_bloki_tilini_saqlaydi(self):
        source = '<pre>\r\n<code class="language-python">x = 1\r\n</code></pre>'
        assert html_to_markdown(source) == "```python\nx = 1\n```"

    def test_kod_ichida_qochirish_yoq(self):
        source = "<p>Funksiya <code>get_students</code> tuzing.</p>"
        assert html_to_markdown(source) == "Funksiya `get_students` tuzing."

    def test_formuladagi_belgilar_qochirilmaydi(self):
        source = '<span class="mathjax-latex">\\(a_1 \\le 10^5\\)</span>'
        assert html_to_markdown(source) == "$a_1 \\le 10^5$"

    def test_jadval_gfm(self):
        source = "<table><tr><th>a</th><th>b</th></tr><tr><td>1</td><td>2</td></tr></table>"
        assert html_to_markdown(source) == "| a | b |\n| --- | --- |\n| 1 | 2 |"

    def test_bosh_kirish(self):
        assert html_to_markdown(None) == ""
        assert html_to_markdown("") == ""


class TestMapDifficulty:
    @pytest.mark.parametrize(
        ("source_rating", "expected"),
        [(100, 800), (2400, 3200), (400, 1100), (900, 1600), (None, 800)],
    )
    def test_chiziqli_xaritalash(self, source_rating, expected):
        assert kep.map_difficulty(source_rating) == expected

    def test_shkaladan_chiqmaydi(self):
        assert kep.map_difficulty(99999) == 3500


class TestToFields:
    def test_limitlar_va_manba(self):
        payload = {
            "id": 42,
            "title": "Sinov",
            "body": "<p>matn</p>",
            "inputData": "<p>kirish</p>",
            "outputData": "<p>chiqish</p>",
            "comment": "<p>izoh</p>",
            "problemRating": 400,
            "timeLimit": 2000,
            "memoryLimit": 512,
            "likesCount": 7,
            "dislikesCount": 1,
            "partialSolvable": True,
            "image": None,
        }
        fields = kep.to_fields(payload)
        assert fields["difficulty"] == 1100
        assert fields["source_rating"] == 400
        assert fields["memory_limit_kb"] == 512 * 1024  # KEP MB da beradi
        assert fields["note"] == "izoh"
        assert fields["source_url"] == "https://kep.uz/problems/42"
        assert fields["likes_count"] == 7
        assert fields["partial_scoring"] is True

    def test_til_limiti_null_bolsa_masala_limiti_ishlaydi(self):
        entry = {"lang": "cpp", "timeLimit": None, "memoryLimit": None, "codeTemplate": None}
        assert kep.language_limits(entry, 256) == {
            "time_limit_ms": None,
            "memory_limit_kb": None,
            "code_template": "",
        }


@pytest.fixture
def kep_api(monkeypatch) -> None:
    """KEP javoblarini o'rniga qo'yamiz — import testi tarmoqsiz ishlasin."""
    problems = {
        1: {
            "id": 1,
            "title": "Ikki son",
            "body": "<p>a va b</p>",
            "inputData": "",
            "outputData": "",
            "comment": None,
            "problemRating": 100,
            "timeLimit": 1000,
            "memoryLimit": 256,
            "authorUsername": "admin",
            "tags": [{"id": 1, "name": "Oddiy"}],
            "topics": [{"id": 2, "name": "Coding"}],
            "availableLanguages": [
                {"lang": "py", "timeLimit": 3000, "memoryLimit": None, "codeTemplate": "x = 1"},
                {"lang": "rs", "timeLimit": None, "memoryLimit": None, "codeTemplate": None},
            ],
            "sampleTests": [],
            "similarProblems": [{"id": 2, "score": 0.9}],
            "attachments": [],
            "checkInputSource": None,
            "likesCount": 0,
            "dislikesCount": 0,
            "partialSolvable": False,
            "image": None,
        },
        2: {
            "id": 2,
            "title": "Uch son",
            "body": "<p>a, b, c</p>",
            "inputData": "",
            "outputData": "",
            "comment": None,
            "problemRating": 2400,
            "timeLimit": 1000,
            "memoryLimit": 256,
            "authorUsername": "admin",
            "tags": [{"id": 1, "name": "Oddiy"}],
            "topics": [],
            "availableLanguages": [],
            "sampleTests": [],
            "similarProblems": [],
            "attachments": [],
            "checkInputSource": None,
            "likesCount": 0,
            "dislikesCount": 0,
            "partialSolvable": False,
            "image": None,
        },
    }

    def fake_fetch(path: str, **params: Any) -> Any:
        if path == "/tags/":
            return [{"id": 1, "name": "Oddiy"}]
        if path.startswith("/problems/") and path != "/problems/":
            return problems[int(path.strip("/").split("/")[-1])]
        if path.startswith("/users/"):
            return {"firstName": "Nazarbek", "lastName": "Baltabaev", "avatar": ""}
        raise AssertionError(f"kutilmagan yo'l: {path}")

    monkeypatch.setattr(kep, "fetch", fake_fetch)


@pytest.mark.django_db
class TestImportCommand:
    def run(self, **kwargs: Any) -> None:
        from django.core.management import call_command

        call_command("import_kep", ids="1,2", no_samples=True, sleep=0, **kwargs)

    def test_qoralama_bolib_tushadi(self, kep_api, language):
        self.run()
        problem = Problem.objects.get(slug="ikki-son")
        # Yashirin testlar yo'q — ommaga chiqarish yolg'on va'da bo'lardi.
        assert problem.is_public is False
        assert problem.code is None
        assert problem.source == "KEP.uz"

    def test_mavzular_ikki_qatlam(self, kep_api, language):
        self.run()
        oddiy = Topic.objects.get(slug="oddiy")
        assert oddiy.parent is not None
        assert oddiy.parent.slug == "coding"

    def test_faqat_bizda_bor_tillar_yoziladi(self, kep_api, language):
        Language.objects.create(code="py313", name="Python", version="3.13", run_cmd=["{src}"])
        self.run()
        rows = ProblemLanguage.objects.filter(problem__slug="ikki-son")
        # `rs` bizda yo'q — tushirib qoldiriladi, `py` esa limiti bilan keladi.
        assert [(r.language.code, r.time_limit_ms) for r in rows] == [("py313", 3000)]

    def test_muallif_nofaol_soya_hisob(self, kep_api, language):
        User.objects.create_user("admin", password="Parol!12345")
        self.run()
        author = Problem.objects.get(slug="ikki-son").author
        assert author is not None
        # Bizdagi `admin` — KEP dagi `admin` emas.
        assert author.username == "kep-admin"
        assert author.is_active is False
        assert author.has_usable_password() is False

    def test_oxshashlik_grafi(self, kep_api, language):
        self.run()
        link = SimilarProblem.objects.get()
        assert (link.problem.slug, link.similar.slug, link.source) == (
            "ikki-son",
            "uch-son",
            "kep.uz",
        )

    def test_qayta_yuritish_takrorlamaydi(self, kep_api, language):
        self.run()
        self.run(refresh=True)
        assert Problem.objects.count() == 2
        assert SimilarProblem.objects.count() == 1
