from __future__ import annotations

from typing import Any

from django.db.models import Avg, Count
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
    level_label = serializers.CharField(read_only=True)
    topics = serializers.SlugRelatedField[Topic](many=True, read_only=True, slug_field="slug")

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
            "is_solved",
        ]


class ProblemDetailSerializer(ProblemListSerializer):
    samples = serializers.SerializerMethodField()

    author = serializers.CharField(source="author.username", read_only=True, default=None)
    rating = serializers.SerializerMethodField()
    my_rating = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()

    def get_rating(self, problem: Problem) -> dict[str, Any]:
        stats = problem.ratings.aggregate(average=Avg("score"), count=Count("pk"))
        average = stats["average"]
        return {
            "average": round(average, 1) if average is not None else None,
            "count": stats["count"],
        }

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

    def get_is_favourite(self, problem: Problem) -> bool:
        user = self._user()
        return user is not None and problem.favourites.filter(user=user).exists()

    def get_samples(self, problem: Problem) -> list[dict[str, Any]]:
        return storage.sample_tests(problem)

    class Meta(ProblemListSerializer.Meta):
        fields = [
            *ProblemListSerializer.Meta.fields,
            "samples",
            "statement",
            "input_format",
            "output_format",
            "note",
            "editorial",
            "author",
            "rating",
            "my_rating",
            "is_favourite",
            "statement_locale",
            "time_limit_ms",
            "memory_limit_kb",
            "checker_type",
            "source",
            "source_url",
        ]
