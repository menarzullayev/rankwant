"""Local ishlab chiqish uchun demo ma'lumot.

Ishlatish:  python manage.py seed_demo
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from classroom.models import Assignment, Classroom, ClassroomMember
from content.models import Article, Roadmap, RoadmapStep
from contests.models import Contest, ContestProblem
from core.models import User
from problems import storage
from problems.models import Language, Problem, TestCase, Topic

LANGUAGES = [
    ("cpp23", "C++", "23", ["g++", "-std=c++23", "-O2", "-o", "{bin}", "{src}"], ["{bin}"]),
    ("py313", "Python", "3.13", [], ["python3", "{src}"]),
    ("java21", "Java", "21", ["javac", "{src}"], ["java", "-cp", "/box", "Main"]),
]

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


class Command(BaseCommand):
    help = "Demo ma'lumot yaratadi (til, mavzu, masala, contest, foydalanuvchi)"

    @transaction.atomic
    def handle(self, *args: Any, **options: Any) -> None:
        for code, name, version, compile_cmd, run_cmd in LANGUAGES:
            Language.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "version": version,
                    "compile_cmd": compile_cmd,
                    "run_cmd": run_cmd,
                },
            )

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
        contest, _ = Contest.objects.update_or_create(
            slug="demo-round-1",
            defaults={
                "title": "Demo Round #1",
                "description": "Local sinov uchun",
                "start_at": now - timedelta(hours=1),
                "end_at": now + timedelta(hours=2),
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

        teacher, created = User.objects.get_or_create(
            username="ustoz", defaults={"email": "ustoz@rankwant.uz", "display_name": "Ustoz"}
        )
        if created:
            teacher.set_password("ustoz12345")
            teacher.save()
            self.stdout.write("ustoz / ustoz12345 yaratildi")

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
            if made:
                student.set_password("oquvchi12345")
                student.save()
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

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo tayyor: {Problem.objects.count()} masala, "
                f"{Language.objects.count()} til, {Contest.objects.count()} contest, "
                f"{Article.objects.count()} maqola, {Classroom.objects.count()} sinf"
            )
        )
