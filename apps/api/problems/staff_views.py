"""Staff (admin UI) yuzasi — masala/mavzu CRUD va test yuklash.

Ommaviy `ProblemViewSet` o'zgarmaydi. Testlar masala ostidagi alohida
endpointlar orqali boshqariladi:
  GET/POST  staff/problems/<slug>/tests/
  DELETE    staff/problems/<slug>/tests/<order>/
"""

from __future__ import annotations

from typing import Any

from django.core.cache import cache
from django.db.models import Count
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from core.staff import StaffViewSet
from problems import storage
from problems.models import Problem, ProblemReport, TestCase, Topic
from problems.staff_serializers import (
    StaffProblemReportSerializer,
    StaffProblemSerializer,
    StaffTestCaseSerializer,
    StaffTopicSerializer,
    TestCaseUploadSerializer,
)


class StaffTopicViewSet(StaffViewSet):
    serializer_class = StaffTopicSerializer
    lookup_field = "slug"
    queryset = Topic.objects.select_related("parent").all()
    search_fields = ["slug", "name_uz", "name_ru", "name_en"]
    ordering_fields = ["slug", "name_uz", "pk"]
    ordering = ["slug"]


class StaffProblemReportViewSet(StaffViewSet):
    """Foydalanuvchilar yuborgan nuqson xabarlari.

    Standart tartib — ochiqlari birinchi: navbat shu yerdan ko'riladi.
    """

    serializer_class = StaffProblemReportSerializer
    queryset = ProblemReport.objects.select_related("problem", "user")
    filterset_fields = ["status", "reason"]
    search_fields = ["problem__slug", "problem__title", "comment"]
    ordering_fields = ["created_at", "status", "pk"]
    ordering = ["status", "-created_at"]


class StaffProblemViewSet(StaffViewSet):
    serializer_class = StaffProblemSerializer
    lookup_field = "slug"
    queryset = (
        Problem.objects.select_related("interactor_language")
        .prefetch_related("topics")
        .annotate(test_count=Count("tests", distinct=True))
    )
    search_fields = ["slug", "title", "source"]
    ordering_fields = ["slug", "difficulty", "solved_count", "created_at", "pk"]
    ordering = ["-pk"]

    def perform_update(self, serializer: Any) -> None:
        """Qiyinlik o'zgarsa yechganlarning Skills reytingi eskiradi.

        ADR-0007: Skills JORIY qiyinlikdan hisoblanadi, ya'ni masalani
        qayta baholash uni yechgan HAMMANING reytingini o'zgartiradi.
        O'lchandi: 800 → 2400 qilingach yechuvchining reytingi 800 da
        qotib qolardi — funksiya ham, Celery task ham bor edi, faqat
        ularni hech kim ulamagan.

        Navbatga tashlanadi, chunki bu arzon emas: o'lchandi — 2929
        yechuvchili masala 3.3 s va 9000 dan ortiq so'rov.
        """
        oldingi = serializer.instance.difficulty
        problem = serializer.save()
        if problem.difficulty != oldingi:
            from ratings.tasks import recalc_skills_for_problem_task

            recalc_skills_for_problem_task.delay(problem.pk)

    @extend_schema(
        request=TestCaseUploadSerializer,
        responses={200: StaffTestCaseSerializer(many=True), 201: StaffTestCaseSerializer},
    )
    @action(detail=True, methods=["get", "post"], url_path="tests")
    def tests(self, request: Request, slug: str | None = None) -> Response:
        problem = self.get_object()
        if request.method == "GET":
            return Response(StaffTestCaseSerializer(problem.tests.all(), many=True).data)

        serializer = TestCaseUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        order = data["order"]

        # Judge testni DB dan emas, S3 dan o'qiydi — avval yuklaymiz, keyin havolani saqlaymiz.
        storage.ensure_bucket()
        input_ref = storage.put_test_data(f"tests/{problem.slug}/{order}.in", data["input"])
        output_ref = storage.put_test_data(f"tests/{problem.slug}/{order}.out", data["expected"])
        cache.delete(storage.samples_cache_key(problem.slug))
        test, created = TestCase.objects.update_or_create(
            problem=problem,
            order=order,
            defaults={
                "input_ref": input_ref,
                "output_ref": output_ref,
                "is_sample": data["is_sample"],
                "points": data["points"],
            },
        )
        return Response(
            StaffTestCaseSerializer(test).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @extend_schema(request=None, responses={204: None})
    @action(detail=True, methods=["delete"], url_path=r"tests/(?P<order>\d+)")
    def delete_test(
        self, request: Request, slug: str | None = None, order: str | None = None
    ) -> Response:
        problem = self.get_object()
        deleted, _ = TestCase.objects.filter(problem=problem, order=int(order or 0)).delete()
        if not deleted:
            return Response(status=status.HTTP_404_NOT_FOUND)
        cache.delete(storage.samples_cache_key(problem.slug))
        return Response(status=status.HTTP_204_NO_CONTENT)
