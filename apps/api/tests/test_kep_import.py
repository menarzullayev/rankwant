"""KEP.uz importi — HTML→Markdown konvertori va xaritalash.

Tarmoqqa chiqmaydi: `kep.fetch` almashtiriladi. Qamrov aynan import
paytida ko'rilgan HAQIQIY nosozliklarga qaratilgan — ichma-ich
`<strong>`, `&nbsp;` li bo'sh ta'kid, CRLF va kod bloki tili.
"""

from __future__ import annotations

from typing import Any

import pytest

from content.models import Article
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

    def test_formulada_qattiq_boshliq_oddiysiga_aylanadi(self):
        # KaTeX 160-belgini «tanilmagan» deb ogohlantiradi.
        source = '<span class="mathjax-latex">\\(n\xa0(1 \\le n)\\)</span>'
        assert html_to_markdown(source) == "$n (1 \\le n)$"

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
        [(100, 800), (2800, 3500), (2400, 3100), (400, 1100), (900, 1600), (None, 800)],
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

    def test_manfiy_limit_cheklov_yoqligini_bildiradi(self):
        # KEP `-1` yozadi; uni o'tkazish manfiy limit bo'lib bazani buzardi.
        entry = {"lang": "cpp", "timeLimit": 1000, "memoryLimit": -1, "codeTemplate": ""}
        assert kep.language_limits(entry, 256)["memory_limit_kb"] is None
        assert kep.to_fields({"id": 1, "memoryLimit": -1})["memory_limit_kb"] == 256 * 1024

    def test_biriktirmalar(self):
        payload = {
            "attachments": [
                {"id": 10, "name": "poly.zip", "url": "https://s3/poly.zip", "size": 1630},
                {"name": "havolasiz", "url": "", "size": 5},
            ]
        }
        assert kep.attachments(payload) == [
            {"url": "https://s3/poly.zip", "name": "poly.zip", "size_bytes": 1630}
        ]


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
            "attachments": [{"name": "poly.zip", "url": "https://s3/poly.zip", "size": 1630}],
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

    def test_biriktirma_koradi(self, kep_api, language):
        self.run()
        attachment = Problem.objects.get(slug="ikki-son").attachments.get()
        assert (attachment.name, attachment.size_bytes) == ("poly.zip", 1630)

    def test_oxshashlik_grafi(self, kep_api, language):
        self.run()
        link = SimilarProblem.objects.get()
        assert (link.problem.slug, link.similar.slug, link.source) == (
            "ikki-son",
            "uch-son",
            "kep.uz",
        )

    def test_refresh_elon_qilinganni_yashirmaydi(self, kep_api, language):
        self.run(publish=True)
        assert Problem.objects.filter(is_public=True).count() == 2

        # Matnni yangilash uchun yuritilgan import HOLATGA tegmaydi.
        self.run(refresh=True)
        assert Problem.objects.filter(is_public=True).count() == 2

    def test_qayta_yuritish_takrorlamaydi(self, kep_api, language):
        self.run()
        self.run(refresh=True)
        assert Problem.objects.count() == 2
        assert SimilarProblem.objects.count() == 1


class TestCleanTest:
    def test_crlf_va_qattiq_boshliq_tozalanadi(self):
        from problems.management.commands.import_kep import clean_test

        # `\r` ni dastur satr qismi deb o'qiydi — to'g'ri yechim yiqilardi.
        assert clean_test("5\r\n2\r\n") == "5\n2\n"
        assert clean_test("a\xa0b") == "a b"
        assert clean_test(None) == ""


@pytest.mark.django_db
class TestRemapAndPublish:
    def make(self, **kwargs: Any) -> Problem:
        defaults = {
            "title": "Sinov",
            "statement": "x",
            "difficulty": 800,
            "source": "KEP.uz",
            "is_public": False,
        }
        return Problem.objects.create(**{**defaults, **kwargs})

    def test_qiyinlik_manba_reytingidan_qayta_hisoblanadi(self):
        from django.core.management import call_command

        problem = self.make(slug="eski", source_rating=2800, difficulty=3200)
        boshqa = self.make(slug="qolgan", source_rating=None, difficulty=1500)

        call_command("remap_difficulty")

        problem.refresh_from_db()
        boshqa.refresh_from_db()
        assert problem.difficulty == 3500
        # Manba reytingi yo'q masala o'z qiyinligida qoladi.
        assert boshqa.difficulty == 1500

    def test_elon_qilinganda_ommaviy_raqam_beriladi(self):
        from django.core.management import call_command

        from problems.models import TestCase as ProblemTest

        birinchi = self.make(slug="b")
        ikkinchi = self.make(slug="a")
        for problem in (birinchi, ikkinchi):
            ProblemTest.objects.create(
                problem=problem, order=1, input_ref="s3://a/1.in", output_ref="s3://a/1.out"
            )

        call_command("publish_problems", source="KEP.uz")

        birinchi.refresh_from_db()
        ikkinchi.refresh_from_db()
        assert birinchi.is_public and ikkinchi.is_public
        # `update()` bilan qilinsa raqam berilmay qolardi.
        assert birinchi.code is not None
        assert ikkinchi.code == birinchi.code + 1, "yaratilish tartibida"

    def test_testsizlar_standart_holda_qoralama_qoladi(self):
        from django.core.management import call_command

        from problems.models import TestCase as ProblemTest

        testli = self.make(slug="testli")
        ProblemTest.objects.create(
            problem=testli, order=1, input_ref="s3://a/1.in", output_ref="s3://a/1.out"
        )
        testsiz = self.make(slug="testsiz")

        call_command("publish_problems", source="KEP.uz")

        testli.refresh_from_db()
        testsiz.refresh_from_db()
        assert testli.is_public is True
        assert testsiz.is_public is False, "testsiz masala yechib bo'lmaydi — chiqmasin"

    def test_faqat_namunali_masala_qoralama_qoladi(self):
        """Yashirin test shart — namuna javobini bosib chiqargan dastur AC oladi."""
        from django.core.management import call_command

        from problems.models import TestCase as ProblemTest

        namunali = self.make(slug="namunali")
        ProblemTest.objects.create(
            problem=namunali,
            order=1,
            input_ref="s3://a/1.in",
            output_ref="s3://a/1.out",
            is_sample=True,
        )

        call_command("publish_problems", source="KEP.uz")

        namunali.refresh_from_db()
        assert namunali.is_public is False

    def test_testsizni_ataylab_chiqarish_mumkin(self):
        """Chetlab o'tish yo'li qoladi, lekin ataylab yozilishi kerak."""
        from django.core.management import call_command

        testsiz = self.make(slug="testsiz2")

        call_command("publish_problems", source="KEP.uz", allow_testless=True)

        testsiz.refresh_from_db()
        assert testsiz.is_public is True

    def test_takroriy_nomli_mavzular_birlashadi(self):
        from django.core.management import call_command

        from problems.models import Topic

        keep = Topic.objects.create(slug="dp", name_uz="Dinamik dasturlash")
        dupe = Topic.objects.create(slug="dinamik-dasturlash", name_uz="dinamik dasturlash")
        child = Topic.objects.create(slug="bola", name_uz="Bola", parent=dupe)
        problem = self.make(slug="masala")
        problem.topics.add(dupe)
        article = Article.objects.create(slug="maqola", title="Maqola", body="x")
        article.topics.add(dupe)

        call_command("merge_topics")

        child.refresh_from_db()
        assert Topic.objects.filter(slug="dinamik-dasturlash").exists() is False
        # Masala, maqola va bola mavzu — hammasi saqlangan yozuvga o'tadi.
        assert list(problem.topics.all()) == [keep]
        assert list(article.topics.all()) == [keep]
        assert child.parent == keep


class TestMirrorSSRF:
    """Ko'chiriladigan havolalar TASHQI arxivdan keladi.

    Ular bizning ichki tarmog'imizga qarab turishi mumkin — bulut
    metadata, MinIO yoki localhost — va buyruq ularni olib kelib ommaviy
    manzilda e'lon qilib qo'yardi.
    """

    def _fetch(self, url: str):
        from problems.management.commands.mirror_assets import _fetch

        return _fetch(url)

    @pytest.mark.parametrize(
        "url",
        [
            "http://127.0.0.1/x.png",
            "http://localhost/x.png",
            "http://169.254.169.254/latest/meta-data/",
            "http://10.0.0.5/x.png",
            "http://192.168.1.1/x.png",
            "http://[::1]/x.png",
            "file:///etc/passwd",
            "gopher://example.uz/x",
        ],
    )
    def test_ichki_manzil_rad_etiladi(self, url: str) -> None:
        with pytest.raises(ValueError):
            self._fetch(url)

    def test_yonaltirish_ham_tekshiriladi(self) -> None:
        """Boshlang'ich manzilni tekshirish yetarli emas: tashqi host 302
        bilan `http://127.0.0.1/…` ga yuborishi mumkin."""
        from problems.management.commands.mirror_assets import _CheckedRedirects

        handler = _CheckedRedirects()
        with pytest.raises(ValueError):
            handler.redirect_request(None, None, 302, "Found", {}, "http://127.0.0.1/x.png")


@pytest.mark.django_db
def test_import_kochirishni_qayta_yuritadi(kep_api, monkeypatch) -> None:
    """Import matnni MANBADAGI holatiga qaytaradi — ya'ni avval
    ko'chirilgan rasmlar yana tashqi hostga qarab qoladi.

    O'lchandi: `--refresh` bitta masalada mahalliy rasmni
    `cpython.s3.amazonaws.com` ga qaytargan.
    """
    from io import StringIO

    from django.core.management import call_command

    from problems.management.commands import import_kep

    chaqirildi: list[str] = []
    monkeypatch.setattr(import_kep, "call_command", lambda nom, *a, **kw: chaqirildi.append(nom))

    call_command("import_kep", "--ids", "1", "--no-samples", stdout=StringIO())

    assert chaqirildi == ["mirror_assets"]


@pytest.mark.django_db
def test_no_mirror_bilan_kochirilmaydi(kep_api, monkeypatch) -> None:
    from io import StringIO

    from django.core.management import call_command

    from problems.management.commands import import_kep

    chaqirildi: list[str] = []
    monkeypatch.setattr(import_kep, "call_command", lambda nom, *a, **kw: chaqirildi.append(nom))

    call_command("import_kep", "--ids", "1", "--no-samples", "--no-mirror", stdout=StringIO())

    assert chaqirildi == []
