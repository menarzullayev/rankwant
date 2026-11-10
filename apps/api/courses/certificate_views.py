"""Course certificates: public verification and the PDF (ADR-0019 style)."""

from __future__ import annotations

from uuid import UUID

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.cache import cache_get, cache_set
from courses import certificate_pdf
from courses.models import CourseCertificate
from courses.serializers import CourseCertificateSerializer

PDF_TTL = 24 * 3600


def _certificate(pk: UUID) -> CourseCertificate:
    return get_object_or_404(CourseCertificate.objects.select_related("user", "course"), pk=pk)


class CourseCertificateView(APIView):
    """Anyone with the id (the QR) may check it — that is what it is for."""

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Kurs sertifikatini tekshirish", responses={200: CourseCertificateSerializer}
    )
    def get(self, request: Request, pk: UUID) -> Response:
        return Response(CourseCertificateSerializer(_certificate(pk)).data)


class CourseCertificatePdfView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Kurs sertifikati PDF'i",
        responses={(200, "application/pdf"): OpenApiTypes.BINARY},
    )
    def get(self, request: Request, pk: UUID) -> HttpResponse:
        cert = _certificate(pk)
        key = f"course-cert:pdf:{cert.pk}"
        data: bytes | None = cache_get(key)
        if data is None:
            data = certificate_pdf.render(cert)
            cache_set(key, data, PDF_TTL)
        response = HttpResponse(data, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'inline; filename="rankwant-{cert.course.slug}-{cert.user.username}.pdf"'
        )
        return response
