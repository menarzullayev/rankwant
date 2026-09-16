"""Maktab katalogi — sozlamalardagi tanlash maydoni va maktab reytingi uchun."""

from __future__ import annotations

from django.db.models import Count, Q, QuerySet
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from core.models import School
from core.openapi_docs import crud_summaries
from core.pagination import StandardPagination
from core.serializers import SchoolSerializer


@crud_summaries(one="maktab", many="maktablar", only=("list", "retrieve"))
class SchoolViewSet(viewsets.ReadOnlyModelViewSet[School]):
    serializer_class = SchoolSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardPagination

    def get_queryset(self) -> QuerySet[School]:
        queryset = School.objects.filter(is_active=True).annotate(
            members=Count("students", filter=Q(students__is_active=True))
        )
        q = self.request.query_params.get("q", "").strip()
        if q:
            queryset = queryset.filter(name__icontains=q)
        for field in ("region", "district"):
            value = self.request.query_params.get(field, "")
            if value:
                queryset = queryset.filter(**{field: value})
        return queryset.order_by("name", "pk")

    @extend_schema(
        parameters=[
            OpenApiParameter("q", str),
            OpenApiParameter("region", str),
            OpenApiParameter("district", str),
        ]
    )
    def list(self, request: Request, *args: object, **kwargs: object) -> Response:
        return super().list(request, *args, **kwargs)
