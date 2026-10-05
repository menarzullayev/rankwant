from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from team.models import Department, Member, Role
from team.serializers import TeamPageSerializer


class TeamView(APIView):
    """What the public `/team` page draws. Drafts are left out."""

    permission_classes = [AllowAny]

    @extend_schema(summary="Jamoa sahifasi", responses={200: TeamPageSerializer})
    def get(self, request: Request) -> Response:
        payload: dict[str, object] = {
            # A department with no published role would be an empty chip.
            "departments": Department.objects.filter(roles__is_published=True).distinct(),
            "roles": Role.objects.filter(is_published=True).select_related("department"),
            "members": Member.objects.filter(is_published=True),
        }
        return Response(TeamPageSerializer(payload).data)
