from __future__ import annotations

from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from blog.models import Post
from blog.serializers import PostDetailSerializer, PostListSerializer
from core.pagination import StandardPagination


class PostViewSet(viewsets.ReadOnlyModelViewSet[Post]):
    """Yozish Django admin orqali — API faqat o'qish uchun."""

    permission_classes = [AllowAny]
    lookup_field = "slug"
    pagination_class = StandardPagination
    filterset_fields = ["kind", "locale"]
    queryset = Post.objects.filter(is_published=True).select_related("author")

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        return PostDetailSerializer if self.action == "retrieve" else PostListSerializer
