from __future__ import annotations

from collections import Counter
from typing import Any

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from problems import storage
from problems.models import Language, Problem, ProblemAttachment, ProblemVote, Topic


class TopicSerializer(serializers.ModelSerializer[Topic]):
    class Meta:
        model = Topic
        fields = ["slug", "name_uz", "name_ru", "name_en", "parent"]


class LanguageSerializer(serializers.ModelSerializer[Language]):
    class Meta:
        model = Language
        fields = ["code", "name", "version"]


#: Tahlil matni yuboriladigan holatlar — ADR-0013. Mehmon bu yerda YO'Q:
#: u yechganini ko'rsata olmaydi, ya'ni spoyler darvozasi u uchun yopiq.
EDITORIAL_OPEN = frozenset({"solved", "staff", "purchased", "free"})


class ProblemLanguageSerializer(serializers.Serializer[dict[str, Any]]):
    """Masalada RUXSAT etilgan til va uning yakuniy limitlari.

    Limitlar allaqachon hisoblangan holda keladi: masalaga xos qiymat
    bo'lmasa masala limiti qo'yiladi. Aks holda har mijoz shu
    mantiqni o'zi takrorlashi kerak bo'lardi.
    """

    code = serializers.CharField()
    name = serializers.CharField()
    version = serializers.CharField()
    time_limit_ms = serializers.IntegerField()
    memory_limit_kb = serializers.IntegerField()
    code_template = serializers.CharField(allow_blank=True)


class SimilarProblemSerializer(serializers.Serializer[dict[str, Any]]):
    slug = serializers.CharField()
    title = serializers.CharField()
    difficulty = serializers.IntegerField()
    level = serializers.CharField()
    level_label = serializers.CharField()
    score = serializers.FloatField()


class AttachmentSerializer(serializers.ModelSerializer[ProblemAttachment]):
    class Meta:
        model = ProblemAttachment
        fields = ["name", "url", "size_bytes"]


class VoteSerializer(serializers.Serializer[dict[str, Any]]):
    #: 0 — ovozni olib tashlash.
    value = serializers.ChoiceField(choices=[-1, 0, 1])


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
    languages = serializers.SerializerMethodField()
    similar = serializers.SerializerMethodField()
    attachments = AttachmentSerializer(many=True, read_only=True)
    votes = serializers.SerializerMethodField()
    editorial = serializers.SerializerMethodField()
    editorial_state = serializers.SerializerMethodField()

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

    @extend_schema_field(ProblemLanguageSerializer(many=True))
    def get_languages(self, problem: Problem) -> list[dict[str, Any]]:
        rows = list(problem.languages.select_related("language"))
        if not rows:
            # Ro'yxat bo'sh — masala hech qanday tilni cheklamagan.
            return [
                {
                    "code": language.code,
                    "name": language.name,
                    "version": language.version,
                    "time_limit_ms": problem.time_limit_ms,
                    "memory_limit_kb": problem.memory_limit_kb,
                    "code_template": "",
                }
                for language in Language.objects.filter(is_active=True)
            ]
        return [
            {
                "code": row.language.code,
                "name": row.language.name,
                "version": row.language.version,
                "time_limit_ms": row.time_limit_ms or problem.time_limit_ms,
                "memory_limit_kb": row.memory_limit_kb or problem.memory_limit_kb,
                "code_template": row.code_template,
            }
            for row in rows
            if row.language.is_active
        ]

    @extend_schema_field(SimilarProblemSerializer(many=True))
    def get_similar(self, problem: Problem) -> list[dict[str, Any]]:
        """O'xshash masalalar — taqalib qolganda keyingi qadam.

        Faqat OMMAVIY masalalar: import qilingan graf qoralamalarga ham
        ishora qiladi va ular hali ochilmagan.
        """
        links = problem.similar_to.select_related("similar").filter(similar__is_public=True)[:6]
        return [
            {
                "slug": link.similar.slug,
                "title": link.similar.title,
                "difficulty": link.similar.difficulty,
                "level": link.similar.level,
                "level_label": link.similar.level_label,
                "score": round(link.score, 2),
            }
            for link in links
        ]

    def get_votes(self, problem: Problem) -> dict[str, Any]:
        """Import qilingan sanoq + bizdagi ovozlar.

        Ikkalasi qo'shiladi: foydalanuvchi uchun bu bitta raqam, manba
        farqi esa faqat bizning ichki masalamiz.
        """
        counts = Counter(problem.votes.values_list("value", flat=True))
        user = self._user()
        mine = problem.votes.filter(user=user).first() if user else None
        return {
            "up": problem.likes_count + counts[ProblemVote.UP],
            "down": problem.dislikes_count + counts[ProblemVote.DOWN],
            "mine": mine.value if mine else 0,
        }

    def _editorial_access(self, problem: Problem) -> str:
        """ADR-0013: yechgan bepul ko'radi, yechmagan Qvant sarflaydi."""
        user = self._user()
        if user is None:
            return "anonymous"
        if user.is_staff:
            return "staff"
        if problem.slug in (self.context.get("solved_slugs") or ()):
            return "solved"
        if problem.pk in (self.context.get("unlocked_ids") or ()):
            return "purchased"
        return "free" if not problem.editorial_price else "locked"

    def get_editorial(self, problem: Problem) -> str:
        """Ochilmagan bo'lsa MATN UMUMAN YUBORILMAYDI.

        Frontendda yashirish spoylerni himoya qilmaydi — matn baribir
        sahifa manbasida ko'rinib turardi.
        """
        if not problem.editorial:
            return ""
        return problem.editorial if self._editorial_access(problem) in EDITORIAL_OPEN else ""

    def get_editorial_state(self, problem: Problem) -> dict[str, Any]:
        return {
            "available": bool(problem.editorial),
            "access": self._editorial_access(problem),
            "price": problem.editorial_price,
        }

    class Meta(ProblemListSerializer.Meta):
        fields = [
            *ProblemListSerializer.Meta.fields,
            "samples",
            "my_rating",
            "languages",
            "similar",
            "attachments",
            "votes",
            "editorial_state",
            "image",
            "partial_scoring",
            "source_rating",
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
