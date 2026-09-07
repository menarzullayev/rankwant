"""Staff API — yangiliklar va e'lonlar (`staff/posts/`).

Bildirishnoma bu yerda YUBORILMAYDI: nashr qilingan `notify_users` postlarni
`blog.announce_published` beat task'i (`notified_at IS NULL` bo'yicha) o'zi
topib yuboradi. Shu yerdan qayta yuborilsa foydalanuvchi ikki marta oladi.
"""

from __future__ import annotations

from typing import Any, ClassVar

from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from blog.models import Post
from blog.staff_serializers import StaffPostSerializer
from core.staff import StaffViewSet


class StaffPostViewSet(StaffViewSet):
    queryset = Post.objects.select_related("author")
    serializer_class = StaffPostSerializer
    lookup_field = "slug"
    search_fields: ClassVar[list[str]] = ["slug", "title", "summary"]
    ordering_fields: ClassVar[list[str]] = ["pk", "published_at", "created_at", "title", "kind"]

    def perform_create(self, serializer: Any) -> None:
        serializer.save(author=self.request.user)

    def _set_published(self, request: Request, value: bool) -> Response:
        post: Post = self.get_object()
        post.is_published = value
        # published_at ni model.save() birinchi nashrda o'zi qo'yadi;
        # qayta nashrda eski sana saqlanadi.
        post.save(update_fields=["is_published", "published_at", "updated_at"])
        return Response(self.get_serializer(post).data)

    @action(detail=True, methods=["post"])
    def publish(self, request: Request, slug: str | None = None) -> Response:
        return self._set_published(request, True)

    @action(detail=True, methods=["post"])
    def unpublish(self, request: Request, slug: str | None = None) -> Response:
        return self._set_published(request, False)
