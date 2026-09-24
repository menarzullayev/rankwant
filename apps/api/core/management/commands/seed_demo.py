"""Local ishlab chiqish uchun demo ma'lumot.

Ishlatish:  python manage.py seed_demo
"""

from __future__ import annotations

import secrets
from datetime import timedelta
from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from arena.models import ArenaQuestion, ArenaRound
from classroom.models import Assignment, Classroom, ClassroomMember
from content.models import Article, Roadmap, RoadmapStep
from contests.models import Contest, ContestProblem
from core.models import User
from duels.models import Duel
from hackathons.models import Hackathon
from problems import storage
from problems.languages import LANGUAGES, row_values
from problems.models import Language, Problem, TestCase, Topic
from quizzes.models import Choice, Question, Quiz, QuizQuestion
from tournaments.models import Tournament, TournamentStage

TOPICS = [
    ("implementation", "Amalga oshirish"),
    ("math", "Matematika"),
    ("dp", "Dinamik dasturlash"),
    ("graphs", "Graflar"),
    ("greedy", "Ochko'zlik"),
]

#: (slug, sarlavha, qiyinlik, mavzular, matn, [(kirish, chiqish), ...])
#:
#: Testlar HAQIQIY: matnsiz masala va bo'sh test bilan to'g'ri yechim ham
#: WA oladi, ya'ni demo hech narsani ko'rsatmaydi.
PROBLEMS = [
    (
        "a-plus-b",
        "A + B",
        800,
        ["implementation"],
        "Bitta qatorda ikkita butun son `a` va `b` berilgan.\n\nUlarning yig'indisini chiqaring.",
        [("1 2\n", "3\n"), ("100 -40\n", "60\n"), ("0 0\n", "0\n")],
    ),
    (
        "juft-toq",
        "Juft yoki toq",
        800,
        ["implementation", "math"],
        "Butun son `n` berilgan. Juft bo'lsa `JUFT`, aks holda `TOQ` chiqaring.",
        [("4\n", "JUFT\n"), ("7\n", "TOQ\n"), ("0\n", "JUFT\n")],
    ),
    (
        "eng-katta",
        "Massivdagi eng katta son",
        900,
        ["implementation"],
        "Birinchi qatorda `n`, keyingi qatorda `n` ta butun son.\n\nEng kattasini chiqaring.",
        [("5\n3 1 4 1 5\n", "5\n"), ("1\n-7\n", "-7\n"), ("3\n2 2 2\n", "2\n")],
    ),
    (
        "fibonacci",
        "Fibonachchi sonlari",
        1200,
        ["dp", "math"],
        "`n` berilgan (0 ≤ n ≤ 90). `F(0)=0`, `F(1)=1` bo'lganda `F(n)` ni chiqaring.",
        [("0\n", "0\n"), ("10\n", "55\n"), ("50\n", "12586269025\n")],
    ),
    # Quyidagi uchtasi qiyin masalalar: matn ham, test ham yozilmagan.
    # Ataylab TESTSIZ qoldirilgan — soxta test to'g'ri yechimni ham
    # yiqitadi, judge esa testsiz job'ni IE deb qaytaradi.
    ("ryukzak", "Ryukzak masalasi", 1600, ["dp"], "", []),
    ("eng-qisqa-yol", "Eng qisqa yo'l", 2000, ["graphs"], "", []),
    ("mintaqalar", "Mintaqalarni bo'lish", 2500, ["graphs", "greedy"], "", []),
]

#: Kiruvchi/chiquvchi va izoh — slug bo'yicha. Tuple shaklini
#: o'zgartirmaslik uchun alohida: matni yozilmagan masalalar bo'sh qoladi.
FORMATS: dict[str, tuple[str, str, str]] = {
    "a-plus-b": (
        "Yagona qatorda ikkita butun son $a$ va $b$ ($-10^9 \\le a, b \\le 10^9$).",
        "Yagona qatorda $a + b$ yig'indisini chiqaring.",
        "",
    ),
    "juft-toq": (
        "Yagona qatorda butun son $n$ ($-10^9 \\le n \\le 10^9$).",
        "Agar $n$ juft bo'lsa `JUFT`, aks holda `TOQ` chiqaring.",
        "Nol juft son hisoblanadi.",
    ),
    "eng-katta": (
        "Birinchi qatorda $n$ ($1 \\le n \\le 10^5$).\n\n"
        "Ikkinchi qatorda $n$ ta butun son ($-10^9 \\le a_i \\le 10^9$).",
        "Yagona qatorda eng katta sonni chiqaring.",
        "",
    ),
    "fibonacci": (
        "Yagona qatorda butun son $n$ ($0 \\le n \\le 90$).",
        "Yagona qatorda $F(n)$ ni chiqaring.",
        "$F(0) = 0$, $F(1) = 1$, keyingilari $F(n) = F(n-1) + F(n-2)$.\n\n"
        "$F(90)$ 64-bitli songa sig'adi, `int` esa yetmaydi.",
    ),
}


ARTICLES = [
    (
        "kirish-cpp",
        "C++ da kirish/chiqish",
        800,
        ["implementation"],
        "Tez kirish/chiqish, `cin`/`cout` va `scanf` farqi.",
    ),
    (
        "dp-asoslari",
        "Dinamik dasturlash asoslari",
        1400,
        ["dp"],
        "Qism-masala, memoizatsiya va pastdan-yuqoriga yondashuv.",
    ),
    (
        "graf-bfs-dfs",
        "Graflarda BFS va DFS",
        1600,
        ["graphs"],
        "Kenglik va chuqurlik bo'yicha izlash, qachon qaysi biri.",
    ),
]

ROADMAP_STEPS = [
    ("kirish-cpp", "a-plus-b"),
    ("kirish-cpp", "juft-toq"),
    ("dp-asoslari", "fibonacci"),
    ("dp-asoslari", "ryukzak"),
    ("graf-bfs-dfs", "eng-qisqa-yol"),
]


ALGO_BODY = """## G'oya

Oraliqni har qadamda ikkiga bo'lamiz.

```cpp
int lo = 0, hi = n - 1;
while (lo <= hi) {
  int mid = (lo + hi) / 2;
  if (a[mid] == x) return mid;
  if (a[mid] < x) lo = mid + 1; else hi = mid - 1;
}
```

Murakkablik: $O(\\log n)$.
"""

#: (matn, [(variant, to'g'rimi), ...], tushuntirish)
QUESTIONS = [
    (
        "Ikkilik qidiruvning vaqt murakkabligi?",
        [("O(log n)", True), ("O(n)", False), ("O(n log n)", False), ("O(1)", False)],
        "Har qadamda oraliq ikkiga bo'linadi.",
    ),
    (
        "Qaysi struktura LIFO tartibida ishlaydi?",
        [("Stek", True), ("Navbat", False), ("Bog'langan ro'yxat", False), ("Hash-jadval", False)],
        "Last In, First Out — oxirgi kirgan birinchi chiqadi.",
    ),
    (
        "Dijkstra algoritmi qachon ISHLAMAYDI?",
        [
            ("Manfiy og'irlikli qirralar bo'lsa", True),
            ("Graf yo'naltirilgan bo'lsa", False),
            ("Uzellar ko'p bo'lsa", False),
            ("Qirralar teng og'irlikda bo'lsa", False),
        ],
        "Manfiy qirra ochko'z tanlovni buzadi — Bellman-Ford kerak.",
    ),
    (
        "Fibonachchi uchun memoizatsiya nimani kamaytiradi?",
        [
            ("Takroriy hisoblarni", True),
            ("Xotira sarfini", False),
            ("Kod uzunligini", False),
            ("Rekursiya chuqurligini", False),
        ],
        "F(n) bir marta hisoblanadi va saqlanadi.",
    ),
]


class Command(BaseCommand):
    help = "Demo ma'lumot yaratadi (til, mavzu, masala, contest, foydalanuvchi)"

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--rotate-passwords",
            action="store_true",
            help="Mavjud demo hisoblarga ham yangi parol beradi",
        )
        parser.add_argument(
            "--live",
            action="store_true",
            help=(
                "Demo contest va arena oynasini HOZIR jonli qiladi "
                "(standart: tugagan). Jonli oyna deploy'ni bloklaydi — "
                "10-operations qoida №1: faol contest paytida deploy "
                "qilinmaydi."
            ),
        )

    @transaction.atomic
    def handle(self, *args: Any, **options: Any) -> None:
        for spec in LANGUAGES:
            Language.objects.update_or_create(code=spec["code"], defaults=row_values(spec))

        topics = {}
        for slug, name in TOPICS:
            topic, _ = Topic.objects.update_or_create(slug=slug, defaults={"name_uz": name})
            topics[slug] = topic

        storage.ensure_bucket()

        for slug, title, difficulty, topic_slugs, statement, tests in PROBLEMS:
            problem, _ = Problem.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "statement": f"## {title}\n\n{statement}"
                    if statement
                    else f"## {title}\n\n_Matn hali yozilmagan._",
                    "input_format": FORMATS.get(slug, ("", "", ""))[0],
                    "output_format": FORMATS.get(slug, ("", "", ""))[1],
                    "note": FORMATS.get(slug, ("", "", ""))[2],
                    "difficulty": difficulty,
                    "is_public": True,
                    "time_limit_ms": 1000,
                    "memory_limit_kb": 262144,
                },
            )
            problem.topics.set([topics[s] for s in topic_slugs])

            for i, (test_in, test_out) in enumerate(tests, start=1):
                TestCase.objects.update_or_create(
                    problem=problem,
                    order=i,
                    defaults={
                        "input_ref": storage.put_test_data(f"tests/{slug}/{i}.in", test_in),
                        "output_ref": storage.put_test_data(f"tests/{slug}/{i}.out", test_out),
                        "is_sample": i == 1,
                    },
                )

        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@rankwant.uz", "admin12345")
            self.stdout.write("admin / admin12345 yaratildi")

        now = timezone.now()

        # ⚠️ Jonli oyna — OPT-IN (2026-09-24). Standart: TUGAGAN demo raund.
        #
        # Sabab o'lchandi. `deploy.yml` ning `Demo data` qadami bu buyruqni
        # HAR deploy'da yurgizadi. Ilgari oyna doim `now-1h → now+2h` edi,
        # ya'ni har deploy o'zidan keyingi deploy'ni 2 soatga bloklardi:
        # `tools/check_deploy_window.py` `is_running` ni ko'radi
        # (`core/mixins.py`: `start_at <= now < end_at`) va qoida №1
        # bo'yicha deploy'ni to'xtatadi.
        #
        #     run 35966889156 — deploy to'xtadi:
        #     ✗ contest «demo-round-1» — 2026-09-24T13:52:30+05:00 gacha
        #
        # Demo ko'rsatish uchun jonli oyna kerak bo'lsa — `--live` bering.
        live = bool(options.get("live"))
        #: Contest: jonli bo'lsa 1 soat oldin boshlanib 2 soatdan keyin
        #: tugaydi; aks holda kecha boshlanib kecha tugagan (tugagan raund
        #: ham ro'yxatda, sahifalarida va reytingida ko'rinadi).
        contest_start = now - timedelta(hours=1) if live else now - timedelta(days=1)
        contest_end = now + timedelta(hours=2) if live else now - timedelta(hours=23)
        #: Arena: jonli bo'lsa 3 daqiqadan keyin boshlanadi (jonli sinab
        #: ko'rish uchun), aks holda kecha tugagan.
        arena_start = now + timedelta(minutes=3) if live else now - timedelta(days=1)

        contest, _ = Contest.objects.update_or_create(
            slug="demo-round-1",
            defaults={
                "title": "Demo Round #1",
                "description": "Local sinov uchun",
                "start_at": contest_start,
                "end_at": contest_end,
                "is_rated": True,
                "freeze_minutes": 30,
            },
        )
        for i, (slug, *_rest) in enumerate(PROBLEMS[:4]):
            ContestProblem.objects.update_or_create(
                contest=contest,
                index_letter=chr(ord("A") + i),
                defaults={"problem": Problem.objects.get(slug=slug)},
            )

        articles = {}
        for slug, title, difficulty, topic_slugs, summary in ARTICLES:
            article, _ = Article.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "summary": summary,
                    "body": f"## {title}\n\n{summary}\n\nMaqola matni bu yerda bo'ladi.",
                    "difficulty": difficulty,
                    "is_published": True,
                },
            )
            article.topics.set([topics[s] for s in topic_slugs])
            articles[slug] = article

        algo, _ = Article.objects.update_or_create(
            slug="ikkilik-qidiruv",
            defaults={
                "title": "Ikkilik qidiruv",
                "kind": Article.Kind.ALGORITHM,
                "summary": "Saralangan massivda O(log n) qidiruv.",
                "body": ALGO_BODY,
                "difficulty": 1000,
                "is_published": True,
            },
        )
        algo.topics.set([topics["implementation"]])

        roadmap, _ = Roadmap.objects.update_or_create(
            slug="boshlangich",
            defaults={
                "title": "Boshlang'ich yo'l",
                "description": "Noldan birinchi contestgacha.",
                "is_published": True,
                "order": 1,
            },
        )
        for i, (article_slug, problem_slug) in enumerate(ROADMAP_STEPS, start=1):
            RoadmapStep.objects.update_or_create(
                roadmap=roadmap,
                order=i,
                defaults={
                    "article": articles[article_slug],
                    "problem": Problem.objects.get(slug=problem_slug),
                },
            )

        # Demo hisoblar o'qituvchi huquqiga ega (sinf yaratish, o'quvchi
        # qo'shish) va sayt ochiq internetda — parol qat'iy va tasodifiy.
        # Yaratilganda beriladi; mavjud hisobga tegmaydi, aks holda har
        # kontent seed'i ulashilgan ma'lumotni yaroqsiz qilardi.
        credentials: list[tuple[str, str]] = []

        rotate = bool(options.get("rotate_passwords"))

        teacher, created = User.objects.get_or_create(
            username="ustoz", defaults={"email": "ustoz@rankwant.uz", "display_name": "Ustoz"}
        )
        if created or rotate:
            teacher_password = secrets.token_urlsafe(12)
            teacher.set_password(teacher_password)
            teacher.save()
            credentials.append(("ustoz", teacher_password))

        classroom, _ = Classroom.objects.update_or_create(
            slug="11-a-sinf",
            defaults={
                "name": "11-A sinf",
                "owner": teacher,
                "description": "Maktab olimpiada guruhi.",
            },
        )
        for i in range(1, 4):
            student, made = User.objects.get_or_create(
                username=f"oquvchi{i}",
                defaults={"email": f"oquvchi{i}@rankwant.uz", "display_name": f"O'quvchi {i}"},
            )
            if made or rotate:
                student_password = secrets.token_urlsafe(12)
                student.set_password(student_password)
                student.save()
                credentials.append((f"oquvchi{i}", student_password))
            ClassroomMember.objects.get_or_create(classroom=classroom, user=student)

        assignment, _ = Assignment.objects.update_or_create(
            classroom=classroom,
            title="1-hafta: kirish",
            defaults={
                "description": "Birinchi uchta masala.",
                "due_at": now + timedelta(days=7),
            },
        )
        assignment.problems.set(Problem.objects.filter(slug__in=[p[0] for p in PROBLEMS[:3]]))

        # ── Testlar va Arena — bitta savol banki ──
        questions = []
        for text, choices, explanation in QUESTIONS:
            q, _ = Question.objects.get_or_create(text=text, defaults={"explanation": explanation})
            if not q.choices.exists():
                for i, (label, ok) in enumerate(choices, start=1):
                    Choice.objects.create(question=q, order=i, text=label, is_correct=ok)
            questions.append(q)
        quiz, _ = Quiz.objects.update_or_create(
            slug="algoritm-asoslari",
            defaults={
                "title": "Algoritm asoslari",
                "description": "4 ta savol, +10 Qvant",
                "is_published": True,
                "reward_qvant": 10,
            },
        )
        for i, q in enumerate(questions, start=1):
            QuizQuestion.objects.get_or_create(quiz=quiz, question=q, defaults={"order": i})

        # Arena: jonli bo'lsa seed'dan 3 daqiqa keyin boshlanadi — jonli
        # sinab ko'rish uchun (`--live`); standart holatda kecha tugagan,
        # ya'ni deploy'ni bloklamaydi.
        arena, _ = ArenaRound.objects.update_or_create(
            slug="demo-arena",
            defaults={
                "title": "Demo Arena",
                "description": "4 savol, har biriga 45 s",
                "start_at": arena_start,
                "seconds_per_question": 45,
                "reward_qvant": 15,
                "rewards_applied_at": None,
            },
        )
        for i, q in enumerate(questions, start=1):
            ArenaQuestion.objects.get_or_create(round=arena, question=q, defaults={"order": i})

        # ── Chempionat: demo contest + final ──
        final, _ = Contest.objects.update_or_create(
            slug="demo-final",
            defaults={
                "title": "Demo Final",
                "description": "Chempionat finali",
                "start_at": now + timedelta(days=3),
                "end_at": now + timedelta(days=3, hours=2),
                "is_rated": True,
            },
        )
        for i, (slug, *_rest) in enumerate(PROBLEMS[:4]):
            ContestProblem.objects.update_or_create(
                contest=final,
                index_letter=chr(ord("A") + i),
                defaults={"problem": Problem.objects.get(slug=slug)},
            )
        tournament, _ = Tournament.objects.update_or_create(
            slug="demo-mavsum",
            defaults={
                "title": "Demo mavsum",
                "description": "Ikki bosqich: raund va final (×2).",
                "start_at": now - timedelta(days=1),
                "end_at": now + timedelta(days=4),
            },
        )
        TournamentStage.objects.update_or_create(
            tournament=tournament, order=1, defaults={"title": "1-raund", "contest": contest}
        )
        TournamentStage.objects.update_or_create(
            tournament=tournament,
            order=2,
            defaults={"title": "Final", "contest": final, "weight": 2},
        )

        # ── Hakaton: hozir ochiq ──
        Hackathon.objects.update_or_create(
            slug="demo-hakaton",
            defaults={
                "title": "Demo Hakaton",
                "description": "## Mavzu\n\nMaktab uchun foydali bot yoki sayt.\n\n"
                "Mezonlar: foydalilik, kod sifati, demo.",
                "start_at": now - timedelta(days=1),
                "submission_deadline": now + timedelta(days=5),
                "end_at": now + timedelta(days=7),
            },
        )

        # ── Duel: ustozdan ochiq chaqiriq ──
        if not Duel.objects.filter(challenger=teacher, status=Duel.Status.OPEN).exists():
            Duel.objects.create(
                challenger=teacher,
                title="Boshlang'ich duel",
                problem_count=3,
                difficulty=900,
                duration_minutes=45,
                start_at=now + timedelta(hours=1),
            )

        if credentials:
            self.stdout.write("--- demo parollar ---")
            for username, password in credentials:
                self.stdout.write(f"{username} / {password}")
            self.stdout.write("--- demo parollar tugadi ---")
        else:
            self.stdout.write("Demo parollar o'zgarmadi (--rotate-passwords bilan yangilanadi)")

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo tayyor: {Problem.objects.count()} masala, "
                f"{Language.objects.count()} til, {Contest.objects.count()} contest, "
                f"{Article.objects.count()} maqola, {Classroom.objects.count()} sinf, "
                f"{Quiz.objects.count()} test, {ArenaRound.objects.count()} arena, "
                f"{Tournament.objects.count()} chempionat, {Hackathon.objects.count()} hakaton"
            )
        )
