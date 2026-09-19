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
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from core.openapi_docs import crud_summaries
from core.permissions import STAFF_GROUP_OPS, StaffOps, has_staff_group
from core.staff import SessionOnly, StaffViewSet
from problems import storage
from problems.models import (
    Problem,
    ProblemReport,
    ReferenceSolution,
    TestCase,
    Topic,
    Validator,
)
from problems.staff_serializers import (
    StaffProblemReportSerializer,
    StaffProblemSerializer,
    StaffReferenceSolutionSerializer,
    StaffTestCaseSerializer,
    StaffTopicSerializer,
    StaffValidatorSerializer,
    TestCaseUploadSerializer,
)


@crud_summaries(one="mavzu", many="mavzular")
class StaffTopicViewSet(StaffViewSet):
    # StaffOps — ADR-0025 guruh bo'linishi.
    permission_classes = [StaffOps]

    serializer_class = StaffTopicSerializer
    lookup_field = "slug"
    queryset = Topic.objects.select_related("parent").all()
    search_fields = ["slug", "name_uz", "name_ru", "name_en"]
    ordering_fields = ["slug", "name_uz", "pk"]
    ordering = ["slug", "pk"]


@crud_summaries(one="shikoyat", many="shikoyatlar")
class StaffProblemReportViewSet(StaffViewSet):
    """Foydalanuvchilar yuborgan nuqson xabarlari.

    Standart tartib — ochiqlari birinchi: navbat shu yerdan ko'riladi.
    """

    # StaffOps — ADR-0025 guruh bo'linishi.
    permission_classes = [StaffOps]

    serializer_class = StaffProblemReportSerializer
    queryset = ProblemReport.objects.select_related("problem", "user")
    filterset_fields = ["status", "reason"]
    search_fields = ["problem__slug", "problem__title", "comment"]
    ordering_fields = ["created_at", "status", "pk"]
    ordering = ["status", "-created_at", "-pk"]


@crud_summaries(
    one="masala",
    many="masalalar",
    extra={
        "tests": "Masala testlari bilan ishlash",
        "delete_test": "Testni o'chirish",
        "validator": "Tekshiruvchi (validator) yuklash",
        "reference_solution": "Namuna yechim yuklash",
    },
)
class StaffProblemViewSet(StaffViewSet):
    # StaffOps — ADR-0025 guruh bo'linishi.
    permission_classes = [StaffOps]

    def get_permissions(self):  # type: ignore[no-untyped-def]
        # `tests` amali muallifga ham ochiq (obyekt tekshiruvi `tests` ichida,
        # ADR-0025): muallif is_staff bo'lmasligi mumkin, shuning uchun bu
        # amalga guruh o'rniga IsAdminUser + SessionOnly — qolgan CRUD ops.
        if self.action == "tests":
            # Muallif is_staff bo'lmasligi mumkin — kirish uchun oddiy
            # autentifikatsiya; obyekt va guruh tekshiruvi `tests` ichida.
            return [IsAuthenticated(), SessionOnly()]
        return super().get_permissions()

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
        # staff-ops — to'liq huquq; muallif esa faqat O'Z draft masalasini
        # boshqaradi (ADR-0025): nashr qilingan masalada testlar baribir
        # xodim nazoratida, chunki judge to'plamining butunligi shunga
        # tayanadi. `permission_classes` (StaffOps) bu yerda emas —
        # get_permissions() da: amal darajasidagi istisno.
        if not has_staff_group(request.user, STAFF_GROUP_OPS):
            is_author = (
                request.user.is_authenticated
                and problem.authors.filter(pk=request.user.pk).exists()
            )
            if not (is_author and not problem.is_public):
                raise PermissionDenied(
                    "Problem tests belong to staff-ops or the draft author"
                )
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

    def _program(self, request: Request, model: Any, serializer_class: Any) -> Response:
        """Masalaga biriktirilgan bitta dasturni boshqaradi.

        `model` va `serializer_class` — `Validator` yoki
        `ReferenceSolution`. Ikkalasi ham masala bilan bitta-bitta
        bog'langan, ya'ni ro'yxat ham, ID ham yo'q: GET o'qiydi, PUT
        yozadi yoki almashtiradi, DELETE olib tashlaydi.
        """
        problem = self.get_object()
        existing = model.objects.filter(problem=problem).first()

        if request.method == "GET":
            if existing is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            return Response(serializer_class(existing).data)

        if request.method == "DELETE":
            if existing is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            existing.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = serializer_class(existing, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(problem=problem)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK if existing else status.HTTP_201_CREATED,
        )

    @extend_schema(
        request=StaffValidatorSerializer,
        responses={200: StaffValidatorSerializer, 201: StaffValidatorSerializer, 204: None},
    )
    @action(detail=True, methods=["get", "put", "delete"], url_path="validator")
    def validator(self, request: Request, slug: str | None = None) -> Response:
        """Kirish validatori (ADR-0020).

        Hackingning MAJBURIY darvozasi: validatorsiz masalada hack
        umuman ochilmaydi, ya'ni bu endpoint bo'lmasa xususiyatni hech
        bir masalada yoqib bo'lmasdi.
        """
        return self._program(request, Validator, StaffValidatorSerializer)

    @extend_schema(
        request=StaffReferenceSolutionSerializer,
        responses={
            200: StaffReferenceSolutionSerializer,
            201: StaffReferenceSolutionSerializer,
            204: None,
        },
    )
    @action(detail=True, methods=["get", "put", "delete"], url_path="reference-solution")
    def reference_solution(self, request: Request, slug: str | None = None) -> Response:
        """Etalon yechim (ADR-0021) — hack testining to'g'ri javobi.

        Hackerning o'z yechimi etalon bo'la OLMAYDI, shuning uchun u
        masala bilan keladi va faqat xodim yuklaydi.
        """
        return self._program(request, ReferenceSolution, StaffReferenceSolutionSerializer)

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
