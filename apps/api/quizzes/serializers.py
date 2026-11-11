from __future__ import annotations

from typing import Any

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from problems.models import Topic
from quizzes.models import Choice, Question, Quiz, QuizAttempt


class ChoicePublicSerializer(serializers.ModelSerializer[Choice]):
    """`is_correct` ATAYLAB yo'q — baholash serverda."""

    class Meta:
        model = Choice
        fields = ["id", "order", "text"]


class QuestionPublicSerializer(serializers.ModelSerializer[Question]):
    choices = ChoicePublicSerializer(many=True, read_only=True)
    topics = serializers.SlugRelatedField[Topic](slug_field="slug", many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "kind", "text", "code", "code_language", "difficulty", "topics", "choices"]


class QuizSerializer(serializers.ModelSerializer[Quiz]):
    question_count = serializers.IntegerField(read_only=True)
    best_score = serializers.IntegerField(read_only=True, allow_null=True)
    #: A teacher's quiz, given to a class: no Qvant (ADR-0061 § 5).
    is_class = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = [
            "slug",
            "title",
            "description",
            "reward_qvant",
            "question_count",
            "best_score",
            "created_at",
            "is_class",
            "time_limit_minutes",
            "one_attempt",
            "answers_after",
        ]

    def get_is_class(self, quiz: Quiz) -> bool:
        return quiz.owner_id is not None


class QuizStateSerializer(serializers.Serializer[dict[str, Any]]):
    #: An open attempt's deadline (a timed quiz), else `null`.
    deadline = serializers.DateTimeField(allow_null=True)
    started = serializers.BooleanField()
    finished = serializers.IntegerField()
    #: A one-attempt quiz already taken.
    taken = serializers.BooleanField()


class QuizDetailSerializer(QuizSerializer):
    questions = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()

    class Meta(QuizSerializer.Meta):
        fields = [*QuizSerializer.Meta.fields, "questions", "state"]

    def _state(self, quiz: Quiz) -> dict[str, Any]:
        from quizzes import services

        cached = getattr(self, "_state_cache", None)
        if cached is not None:
            return dict(cached)
        user = self.context.get("user")
        state: dict[str, Any] = {"deadline": None, "started": False, "finished": 0, "taken": False}
        if user is not None and user.is_authenticated:
            current = services.open_attempt(user, quiz)
            finished = QuizAttempt.objects.filter(
                user=user, quiz=quiz, finished_at__isnull=False
            ).count()
            state = {
                "deadline": services.deadline(quiz, current) if current else None,
                "started": current is not None,
                "finished": finished,
                "taken": quiz.one_attempt and finished > 0,
            }
        self._state_cache = state
        return state

    @extend_schema_field(QuizStateSerializer)
    def get_state(self, quiz: Quiz) -> dict[str, Any]:
        return self._state(quiz)

    @extend_schema_field(QuestionPublicSerializer(many=True))
    def get_questions(self, quiz: Quiz) -> list[dict[str, Any]]:
        # A timed quiz shows its questions only inside a started attempt:
        # read before the clock, the limit would mean nothing.
        if quiz.time_limit_minutes is not None and not self._state(quiz)["started"]:
            return []
        items = quiz.items.select_related("question").prefetch_related(
            "question__choices", "question__topics"
        )
        return [QuestionPublicSerializer(i.question).data for i in items]


class QuizSubmitSerializer(serializers.Serializer[dict[str, Any]]):
    #: {question_id: answer}: a choice id, a list of choice ids, a number or
    #: a text, by the question's kind.
    answers = serializers.DictField(child=serializers.JSONField(), allow_empty=True)

    def validate_answers(self, value: dict[str, Any]) -> dict[int, Any]:
        out: dict[int, Any] = {}
        try:
            for key, answer in value.items():
                if isinstance(answer, list):
                    answer = [int(v) for v in answer]
                elif isinstance(answer, bool) or not isinstance(answer, int | float | str):
                    raise ValueError(key)
                out[int(key)] = answer
        except (TypeError, ValueError) as exc:
            raise serializers.ValidationError("Keys must be question IDs") from exc
        return out


class ReviewItemSerializer(serializers.Serializer[dict[str, Any]]):
    question_id = serializers.IntegerField()
    chosen = serializers.IntegerField(allow_null=True)
    correct = serializers.IntegerField(allow_null=True)
    #: Any kind (ADR-0061 § 5): a choice id, a list of them, a number or text.
    chosen_value = serializers.JSONField(allow_null=True)
    correct_value = serializers.JSONField(allow_null=True)
    is_correct = serializers.BooleanField()
    explanation = serializers.CharField()


class QuizResultSerializer(serializers.ModelSerializer[QuizAttempt]):
    review = ReviewItemSerializer(many=True, read_only=True)
    #: The right answers wait for the quiz's `answers_after`.
    answers_hidden = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = QuizAttempt
        fields = ["id", "score", "total", "qvant_awarded", "review", "created_at", "answers_hidden"]


class QuizStartSerializer(serializers.Serializer[dict[str, Any]]):
    deadline = serializers.DateTimeField(allow_null=True)
