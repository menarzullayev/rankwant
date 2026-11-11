from __future__ import annotations

from typing import Any

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from community.models import Comment, Report
from community.services import BODY_MAX, visible
from core.models import User
from profiles.titles import TitleField


class CommentAuthorSerializer(serializers.ModelSerializer[User]):
    title = TitleField()

    class Meta:
        model = User
        fields = ["username", "display_name", "title"]


class CommentSerializer(serializers.ModelSerializer[Comment]):
    """One comment as one reader may see it (`services.visible`)."""

    author = serializers.SerializerMethodField()
    body = serializers.SerializerMethodField()
    hidden_code = serializers.SerializerMethodField()
    my_vote = serializers.SerializerMethodField()
    mine = serializers.SerializerMethodField()
    author_solved = serializers.SerializerMethodField()
    author_owner = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "parent",
            "depth",
            "author",
            "body",
            "hidden_code",
            "score",
            "my_vote",
            "mine",
            "author_solved",
            "author_owner",
            "is_deleted",
            "is_hidden",
            "created_at",
            "edited_at",
        ]
        read_only_fields = fields

    def _seen(self, row: Comment) -> dict[str, Any]:
        cache: dict[int, dict[str, Any]] = self.__dict__.setdefault("_seen_rows", {})
        if row.pk not in cache:
            cache[row.pk] = visible(
                row,
                code_open=self.context.get("code_open", True),
                moderator=self.context.get("moderator", False),
                viewer_id=self.context.get("viewer_id"),
            )
        return cache[row.pk]

    @extend_schema_field(CommentAuthorSerializer(allow_null=True))
    def get_author(self, row: Comment) -> dict[str, Any] | None:
        author = self._seen(row)["author"]
        return CommentAuthorSerializer(author).data if author is not None else None

    def get_body(self, row: Comment) -> str:
        return str(self._seen(row)["body"])

    def get_hidden_code(self, row: Comment) -> int:
        """How many code blocks were taken out for this reader (②)."""
        return int(self._seen(row)["hidden_code"])

    def get_my_vote(self, row: Comment) -> int:
        return int(self.context.get("votes", {}).get(row.pk, 0))

    def get_mine(self, row: Comment) -> bool:
        viewer = self.context.get("viewer_id")
        return viewer is not None and row.author_id == viewer

    def get_author_solved(self, row: Comment) -> bool:
        return row.author_id in self.context.get("solvers", set())

    def get_author_owner(self, row: Comment) -> bool:
        place = self.context.get("place")
        return place is not None and row.author_id in place.owners


class ThreadPageSerializer(serializers.Serializer[Any]):
    #: Visible comments in the whole discussion.
    count = serializers.IntegerField()
    #: Pass as `before` for the next page of threads; null at the end.
    next = serializers.IntegerField(allow_null=True)
    #: Whether this reader sees code blocks (they solved the problem).
    code_open = serializers.BooleanField()
    comments = CommentSerializer(many=True)


class PostCommentSerializer(serializers.Serializer[Any]):
    body = serializers.CharField(max_length=BODY_MAX, trim_whitespace=True)
    #: The comment answered; empty for a new thread.
    reply_to = serializers.IntegerField(required=False, allow_null=True, min_value=1)


class EditCommentSerializer(serializers.Serializer[Any]):
    body = serializers.CharField(max_length=BODY_MAX, trim_whitespace=True)


class CommunityVoteSerializer(serializers.Serializer[Any]):
    value = serializers.ChoiceField(choices=[-1, 0, 1])


class CommunityVoteResultSerializer(serializers.Serializer[Any]):
    score = serializers.IntegerField()
    my_vote = serializers.IntegerField()


class CommunityReportSerializer(serializers.Serializer[Any]):
    reason = serializers.ChoiceField(choices=Report.Reason.choices)
    note = serializers.CharField(max_length=300, required=False, allow_blank=True, default="")


class StaffCommentSerializer(serializers.ModelSerializer[Comment]):
    """A comment in the moderation list: the whole text, whoever wrote it."""

    author = serializers.CharField(source="author.username", default=None, read_only=True)
    reasons = serializers.SerializerMethodField()
    link = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "target_type",
            "target_id",
            "link",
            "author",
            "body",
            "score",
            "report_count",
            "reasons",
            "is_hidden",
            "is_deleted",
            "created_at",
        ]
        read_only_fields = fields

    def get_reasons(self, row: Comment) -> list[str]:
        """Reasons of the reports still open."""
        reasons: dict[int, list[str]] = self.context.get("reasons", {})
        return reasons.get(row.pk, [])

    def get_link(self, row: Comment) -> str:
        """Where the comment lives on the site."""
        links: dict[int, str] = self.context.get("links", {})
        return links.get(row.pk, "")
