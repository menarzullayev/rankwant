from __future__ import annotations

from rest_framework import serializers

from blog.models import Post


class PostListSerializer(serializers.ModelSerializer[Post]):
    author = serializers.CharField(source="author.username", read_only=True, default=None)

    class Meta:
        model = Post
        fields = ["slug", "kind", "title", "summary", "locale", "author", "published_at"]


class PostDetailSerializer(PostListSerializer):
    class Meta(PostListSerializer.Meta):
        fields = [*PostListSerializer.Meta.fields, "body"]
