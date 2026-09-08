from __future__ import annotations

from typing import Any

from rest_framework import serializers

from problems import storage
from problems.models import Language, Problem, Topic


class TopicSerializer(serializers.ModelSerializer[Topic]):
    class Meta:
        model = Topic
        fields = ["slug", "name_uz", "name_ru", "name_en", "parent"]


class LanguageSerializer(serializers.ModelSerializer[Language]):
    class Meta:
        model = Language
        fields = ["code", "name", "version"]


class SampleTestSerializer(serializers.Serializer[dict[str, Any]]):
    """Namuna test — kirish va kutilgan chiqish matni bilan.

    Kiruvchi/chiquvchi formatini faqat matndan tushunib bo'lmaydi, shuning
    uchun namunalar masala sahifasining ajralmas qismi (RoboContest, KEP,
    Codeforces — uchalasida ham shunday) va SSR ga kiradi.
    """

    order = serializers.IntegerField(read_only=True)
    input = serializers.CharField(read_only=True)
    expected = serializers.CharField(read_only=True)


class RateProblemSerializer(serializers.Serializer[dict[str, Any]]):
    score = serializers.IntegerField(min_value=1, max_value=5)


class ProblemListSerializer(serializers.ModelSerializer[Problem]):
    level = serializers.CharField(read_only=True)
    is_solved = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    has_editorial = serializers.SerializerMethodField()
    my_verdict = serializers.SerializerMethodField()
    success_rate = serializers.SerializerMethodField()
    level_label = serializers.CharField(read_only=True)
    topics = serializers.SlugRelatedField[Topic](many=True, read_only=True, slug_field="slug")

    def get_is_favourite(self, problem: Problem) -> bool:
        return problem.pk in (self.context.get("favourite_ids") or ())

    def get_rating(self, problem: Problem) -> dict[str, Any]:
        """Jamoa bahosi — queryset'da annotatsiya qilinadi (N+1 emas)."""
        average = getattr(problem, "rating_avg", None)
        return {
            "average": round(average, 1) if average is not None else None,
            "count": getattr(problem, "rating_count", 0),
        }

    def get_has_editorial(self, problem: Problem) -> bool:
        return bool(problem.editorial)

    def get_my_verdict(self, problem: Problem) -> str | None:
        """Shu masala bo'yicha oxirgi urinishim verdikti."""
        return (self.context.get("my_verdicts") or {}).get(problem.pk)

    def get_success_rate(self, problem: Problem) -> int | None:
        """Yechilgan / urinilgan, foizda. Urinish bo'lmasa ma'nosiz."""
        if not problem.attempt_count:
            return None
        return round(problem.solved_count / problem.attempt_count * 100)

    def get_is_solved(self, problem: Problem) -> bool:
        """Foydalanuvchi shu masalani yechganmi.

        Slug to'plamini viewset bitta so'rovda tayyorlaydi (`context`) —
        aks holda har qatorga alohida so'rov ketardi. Mehmon uchun `None`,
        ya'ni hammasi `false`.
        """
        solved = self.context.get("solved_slugs")
        return problem.slug in solved if solved else False

    class Meta:
        model = Problem
        fields = [
            "slug",
            "title",
            "difficulty",
            "level",
            "level_label",
            "topics",
            "solved_count",
            "attempt_count",
            "view_count",
            "success_rate",
            "is_solved",
            "is_favourite",
            "rating",
            "has_editorial",
            "my_verdict",
            "code",
        ]


class ProblemDetailSerializer(ProblemListSerializer):
    samples = serializers.SerializerMethodField()

    author = serializers.CharField(source="author.username", read_only=True, default=None)
    my_rating = serializers.SerializerMethodField()

    def _user(self) -> Any:
        request = self.context.get("request")
        user = getattr(request, "user", None)
        return user if user is not None and user.is_authenticated else None

    def get_my_rating(self, problem: Problem) -> int | None:
        user = self._user()
        if user is None:
            return None
        mine = problem.ratings.filter(user=user).first()
        return mine.score if mine else None

    def get_samples(self, problem: Problem) -> list[dict[str, Any]]:
        return storage.sample_tests(problem)

    class Meta(ProblemListSerializer.Meta):
        fields = [
            *ProblemListSerializer.Meta.fields,
            "samples",
            "my_rating",
            "statement",
            "input_format",
            "output_format",
            "note",
            "editorial",
            "author",
            "statement_locale",
            "time_limit_ms",
            "memory_limit_kb",
            "checker_type",
            "source",
            "source_url",
        ]
