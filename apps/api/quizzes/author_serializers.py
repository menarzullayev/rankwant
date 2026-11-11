"""A teacher's own question bank and quizzes (ADR-0061 § 5)."""

from __future__ import annotations

from typing import Any, ClassVar

from django.db import transaction
from rest_framework import serializers

from quizzes.models import Choice, Question, QuestionFolder, Quiz, QuizAttempt, QuizQuestion

#: Questions one teacher may keep: a guard against a flood, not a plan limit
#: (the plan counts quizzes, owner decision ⑨).
MAX_BANK = 1000
MAX_QUIZ_QUESTIONS = 100
#: Paths under `/quizzes/` a quiz slug must not take.
RESERVED_SLUGS = frozenset({"mine"})


class FolderSerializer(serializers.ModelSerializer[QuestionFolder]):
    question_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = QuestionFolder
        fields = ["id", "name", "question_count", "created_at"]
        read_only_fields: ClassVar = ["id", "created_at"]


class AuthorChoiceSerializer(serializers.ModelSerializer[Choice]):
    order = serializers.IntegerField(min_value=1)

    class Meta:
        model = Choice
        fields = ["id", "order", "text", "is_correct"]
        read_only_fields: ClassVar = ["id"]


def _answered(question: Question) -> bool:
    """Students have finished a quiz with this question: its choices are fixed."""
    return QuizAttempt.objects.filter(
        quiz__items__question=question, finished_at__isnull=False
    ).exists()


class AuthorQuestionSerializer(serializers.ModelSerializer[Question]):
    choices = AuthorChoiceSerializer(many=True, required=False)
    folder = serializers.PrimaryKeyRelatedField(
        queryset=QuestionFolder.objects.none(), allow_null=True, required=False
    )
    #: Quizzes that use the question.
    used = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Question
        fields = [
            "id",
            "kind",
            "text",
            "code",
            "code_language",
            "explanation",
            "folder",
            "choices",
            "answer_number",
            "tolerance",
            "answer_text",
            "difficulty",
            "used",
            "created_at",
        ]
        read_only_fields: ClassVar = ["id", "created_at"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        user = self.context.get("user")
        # Schema generation has an anonymous user: no folders to offer.
        if user is not None and user.is_authenticated:
            self.fields["folder"].queryset = QuestionFolder.objects.filter(owner=user)  # type: ignore[attr-defined]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        instance = self.instance
        if instance is not None and _answered(instance):
            # Past scores were counted against the old answer: a new one
            # would make every review disagree with its score.
            fixed = ("kind", "answer_number", "tolerance", "answer_text")
            if any(name in attrs and attrs[name] != getattr(instance, name) for name in fixed):
                raise serializers.ValidationError(
                    "Students already answered this question; make a copy"
                )
        kind = attrs.get("kind", instance.kind if instance else Question.Kind.SINGLE)
        choices = attrs.get("choices")
        if choices is None and instance is not None and "kind" not in attrs:
            return attrs  # a PATCH that leaves the answers alone
        if kind in (Question.Kind.SINGLE, Question.Kind.MULTIPLE):
            if choices is None:
                raise serializers.ValidationError({"choices": "Give the choices"})
            if len(choices) < 2:
                raise serializers.ValidationError({"choices": "At least two choices are required"})
            right = sum(1 for c in choices if c.get("is_correct"))
            if kind == Question.Kind.SINGLE and right != 1:
                raise serializers.ValidationError({"choices": "Exactly one choice must be correct"})
            if kind == Question.Kind.MULTIPLE and right < 1:
                raise serializers.ValidationError(
                    {"choices": "At least one choice must be correct"}
                )
            orders = [c["order"] for c in choices]
            if len(set(orders)) != len(orders):
                raise serializers.ValidationError(
                    {"choices": "Choice order numbers must be unique"}
                )
        elif kind == Question.Kind.NUMBER:
            number = attrs.get("answer_number", instance.answer_number if instance else None)
            if number is None:
                raise serializers.ValidationError({"answer_number": "Give the right number"})
            if attrs.get("tolerance", 0) < 0:
                raise serializers.ValidationError({"tolerance": "Cannot be negative"})
            attrs["choices"] = []
        else:
            text = attrs.get("answer_text", instance.answer_text if instance else "")
            if not text.strip():
                raise serializers.ValidationError({"answer_text": "Give at least one answer"})
            attrs["choices"] = []
        return attrs

    @staticmethod
    def _replace_choices(question: Question, choices: list[dict[str, Any]]) -> None:
        # A finished attempt keeps choice ids in its answers: new ids would
        # turn every past review wrong.
        if _answered(question):
            raise serializers.ValidationError(
                {"choices": "Students already answered this question; make a copy"}
            )
        question.choices.all().delete()
        Choice.objects.bulk_create(
            Choice(
                question=question,
                order=c["order"],
                text=c["text"],
                is_correct=c.get("is_correct", False),
            )
            for c in choices
        )

    @transaction.atomic
    def create(self, validated_data: dict[str, Any]) -> Question:
        user = self.context["user"]
        if Question.objects.filter(owner=user).count() >= MAX_BANK:
            raise serializers.ValidationError(f"At most {MAX_BANK} questions")
        choices = validated_data.pop("choices", [])
        question = Question.objects.create(owner=user, **validated_data)
        self._replace_choices(question, choices)
        return question

    @transaction.atomic
    def update(self, instance: Question, validated_data: dict[str, Any]) -> Question:
        choices = validated_data.pop("choices", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if choices is not None:
            self._replace_choices(instance, choices)
        return instance


class QuizQuestionRefSerializer(serializers.Serializer[dict[str, Any]]):
    id = serializers.IntegerField()
    kind = serializers.CharField()
    text = serializers.CharField()


class AuthorQuizSerializer(serializers.ModelSerializer[Quiz]):
    #: The quiz's questions in order, as ids of the author's own questions.
    question_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    questions = serializers.SerializerMethodField()
    attempt_count = serializers.IntegerField(read_only=True, default=0)
    assignment_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Quiz
        fields = [
            "slug",
            "title",
            "description",
            "time_limit_minutes",
            "one_attempt",
            "answers_after",
            "question_ids",
            "questions",
            "attempt_count",
            "assignment_count",
            "created_at",
        ]
        read_only_fields: ClassVar = ["created_at"]
        extra_kwargs: ClassVar[dict[str, dict[str, Any]]] = {
            "time_limit_minutes": {"min_value": 1, "max_value": 600}
        }

    def get_questions(self, quiz: Quiz) -> list[dict[str, Any]]:
        return [
            {"id": item.question_id, "kind": item.question.kind, "text": item.question.text[:120]}
            for item in quiz.items.select_related("question")
        ]

    def validate_slug(self, value: str) -> str:
        if value in RESERVED_SLUGS:
            raise serializers.ValidationError("This address is reserved")
        if self.instance is not None and value != self.instance.slug:
            raise serializers.ValidationError("The address cannot change")
        return value

    def validate_question_ids(self, value: list[int]) -> list[int]:
        if len(value) > MAX_QUIZ_QUESTIONS:
            raise serializers.ValidationError(f"At most {MAX_QUIZ_QUESTIONS} questions")
        if len(set(value)) != len(value):
            raise serializers.ValidationError("A question appears twice")
        own = set(
            Question.objects.filter(owner=self.context["user"], pk__in=value).values_list(
                "pk", flat=True
            )
        )
        missing = [pk for pk in value if pk not in own]
        if missing:
            raise serializers.ValidationError(f"Not your questions: {missing}")
        return value

    @staticmethod
    def _set_questions(quiz: Quiz, ids: list[int]) -> None:
        if QuizAttempt.objects.filter(quiz=quiz, finished_at__isnull=False).exists():
            raise serializers.ValidationError(
                {"question_ids": "Students already took this quiz; its questions are fixed"}
            )
        quiz.items.all().delete()
        QuizQuestion.objects.bulk_create(
            QuizQuestion(quiz=quiz, question_id=pk, order=i) for i, pk in enumerate(ids, start=1)
        )

    @transaction.atomic
    def create(self, validated_data: dict[str, Any]) -> Quiz:
        ids = validated_data.pop("question_ids", [])
        # No Qvant for a teacher's quiz, and never in the public catalogue.
        quiz = Quiz.objects.create(
            owner=self.context["user"], reward_qvant=0, is_published=False, **validated_data
        )
        self._set_questions(quiz, ids)
        return quiz

    @transaction.atomic
    def update(self, instance: Quiz, validated_data: dict[str, Any]) -> Quiz:
        ids = validated_data.pop("question_ids", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if ids is not None:
            self._set_questions(instance, ids)
        return instance
