"""Staff API for the team page (`staff/team/…`) — full management."""

from __future__ import annotations

from typing import ClassVar

from core.openapi_docs import crud_summaries
from core.permissions import StaffContent
from core.staff import StaffViewSet
from team.models import Department, Member, Role
from team.serializers import (
    StaffTeamDepartmentSerializer,
    StaffTeamMemberSerializer,
    StaffTeamRoleSerializer,
)


@crud_summaries(one="jamoa bo'limi", many="jamoa bo'limlari")
class StaffDepartmentViewSet(StaffViewSet):
    permission_classes = [StaffContent]
    queryset = Department.objects.all()
    serializer_class = StaffTeamDepartmentSerializer
    search_fields: ClassVar[list[str]] = ["name_uz", "name_ru", "name_en"]
    ordering_fields: ClassVar[list[str]] = ["pk", "order", "name_uz"]
    ordering: ClassVar[list[str]] = ["order", "pk"]


@crud_summaries(one="jamoa lavozimi", many="jamoa lavozimlari")
class StaffRoleViewSet(StaffViewSet):
    permission_classes = [StaffContent]
    queryset = Role.objects.select_related("department")
    serializer_class = StaffTeamRoleSerializer
    search_fields: ClassVar[list[str]] = ["title_uz", "title_ru", "title_en", "badge"]
    ordering_fields: ClassVar[list[str]] = ["pk", "order", "title_uz", "department__order"]
    ordering: ClassVar[list[str]] = ["department__order", "order", "pk"]


@crud_summaries(one="jamoa a'zosi", many="jamoa a'zolari")
class StaffMemberViewSet(StaffViewSet):
    permission_classes = [StaffContent]
    queryset = Member.objects.all()
    serializer_class = StaffTeamMemberSerializer
    search_fields: ClassVar[list[str]] = ["name", "title_uz", "title_en"]
    ordering_fields: ClassVar[list[str]] = ["pk", "order", "name", "section"]
    ordering: ClassVar[list[str]] = ["section", "order", "pk"]
