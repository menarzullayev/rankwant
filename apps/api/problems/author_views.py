"""Muallif yuzasi (ADR-0025, qaror 23) — `problems/mine/`.

Masala muallifi `is_staff` BO'LMAGAN foydalanuvchi bo'lishi mumkin: o'z
DRAFT masalasini yaratadi (`is_public=False`), bayonot va editorialni
tahrirlaydi. Nashr — staff-ops (`staff/problems/` yuzasida). Muallif o'z
draftining testlarini ham boshqaradi — bu xodim yuzasidagi `tests`
amalining obyekt tekshiruvi orqali (`problems/staff_views.py`).

Yozish PAT bilan `submit` scope'ida ishlaydi (`CanSubmit`) — ADR-0008.
"""

from __future__ import annotations

from typing import Any

from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from core.models import User
from core.openapi_docs import crud_summaries
from core.permissions import CanSubmit
from problems.models import Problem
from problems.serializers import MineProblemSerializer


@crud_summaries(one="draft masala", many="draft masalalar")
class MineProblemViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet[Problem],
):
    serializer_class = MineProblemSerializer
    permission_classes = [IsAuthenticated, CanSubmit]
    lookup_field = "slug"

    def get_queryset(self) -> Any:
        assert self.request.user.is_authenticated
        return self.request.user.authored_problems.order_by("-pk")

    def perform_create(self, serializer: Any) -> None:
        # Draft: nashr staff-ops qarori.
        user = self.request.user
        assert isinstance(user, User)
        problem = serializer.save(is_public=False)
        problem.authors.add(user)

    def perform_destroy(self, instance: Problem) -> None:
        if instance.is_public:
            self.permission_denied(
                self.request,
                message="Nashr qilingan masala o'chirilmaydi — staff-ops bilan arxivlanadi",
            )
        super().perform_destroy(instance)
