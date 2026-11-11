"""Discussion API (decision 2026-11-11).

- `discussions/problem/<ref>/` — GET a page of threads (anyone), POST a
  comment (signed in). `ref` is the problem's slug or number. A problem not
  in the archive (a draft, or one still inside a running contest) has no
  discussion: 404.
- `comments/<id>/` — PATCH edit, DELETE remove (the author); `vote/`,
  `report/`.
- `staff/community/comments/` — moderation: the list, `hide`, `unhide`.
"""

from __future__ import annotations

from typing import Any, ClassVar

from django.db.models import QuerySet
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from community import blog, karma, services
from community.models import Comment, Entry, Kind, Report, Target, Vote
from community.serializers import (
    CommentSerializer,
    CommunityReportSerializer,
    CommunityVoteResultSerializer,
    CommunityVoteSerializer,
    EditCommentSerializer,
    EntryDetailSerializer,
    EntrySerializer,
    EntryWriteSerializer,
    KarmaRowSerializer,
    PostCommentSerializer,
    StaffCommentSerializer,
    StaffEntrySerializer,
    TagCountSerializer,
    ThreadPageSerializer,
)
from community.services import CommunityError, Place
from core.models import User
from core.pagination import StandardPagination
from core.staff import StaffViewSet

#: Errors that mean "no such thing" or "not yours", not a bad request.
_STATUS = {
    "comment_not_found": status.HTTP_404_NOT_FOUND,
    "comment_not_yours": status.HTTP_403_FORBIDDEN,
    "entry_not_found": status.HTTP_404_NOT_FOUND,
    "entry_not_yours": status.HTTP_403_FORBIDDEN,
}


def _failed(exc: CommunityError) -> Response:
    return Response(
        {"error": {"code": exc.code, "message": str(exc), "details": {}}},
        status=_STATUS.get(exc.code, status.HTTP_400_BAD_REQUEST),
    )


def _closed() -> Response:
    return Response(
        {"error": {"code": "discussion_closed", "message": "No discussion here", "details": {}}},
        status=status.HTTP_404_NOT_FOUND,
    )


def _user(request: Request) -> User:
    assert isinstance(request.user, User)
    return request.user


def _page(place: Place, request: Request, before: int | None) -> dict[str, Any]:
    page = services.thread_page(place, request.user, before=before)
    context = {key: page[key] for key in ("votes", "solvers", "moderator", "viewer_id", "place")}
    context["code_open"] = page["code_open"]
    return {
        "count": page["count"],
        "next": page["next"],
        "code_open": page["code_open"],
        "comments": CommentSerializer(page["rows"], many=True, context=context).data,
    }


def _one(place: Place, comment: Comment, request: Request) -> dict[str, Any]:
    """A comment just written or edited, as its author sees it."""
    context = {
        "votes": {},
        "solvers": set(),
        "moderator": services.is_moderator(request.user),
        "viewer_id": request.user.pk,
        "place": place,
        "code_open": True,
    }
    return dict(CommentSerializer(comment, context=context).data)


class DiscussionView(APIView):
    """One discussion: a problem's (`kind=problem`) or a blog entry's."""

    #: Set per route in `urls.py`.
    kind = Target.PROBLEM

    def get_permissions(self) -> list[Any]:
        return [IsAuthenticated()] if self.request.method == "POST" else [AllowAny()]

    def _place(self, ref: str) -> Place | None:
        if self.kind == Target.ENTRY:
            return blog.entry_place(ref)
        return services.problem_place(ref)

    @extend_schema(
        summary="Muhokama: mavzular sahifasi",
        parameters=[OpenApiParameter("before", int, required=False)],
        responses=ThreadPageSerializer,
    )
    def get(self, request: Request, ref: str) -> Response:
        place = self._place(ref)
        if place is None:
            return _closed()
        raw = request.query_params.get("before", "")
        before = int(raw) if raw.isdigit() else None
        return Response(_page(place, request, before))

    @extend_schema(
        summary="Muhokamaga izoh yozish",
        request=PostCommentSerializer,
        responses={201: CommentSerializer},
    )
    def post(self, request: Request, ref: str) -> Response:
        place = self._place(ref)
        if place is None:
            return _closed()
        body = PostCommentSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        try:
            comment = services.post(
                _user(request),
                place,
                body.validated_data["body"],
                body.validated_data.get("reply_to"),
            )
        except CommunityError as exc:
            return _failed(exc)
        return Response(_one(place, comment, request), status=status.HTTP_201_CREATED)


class CommentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Comment.objects.none()
    lookup_value_regex = r"\d+"

    @extend_schema(
        summary="O'z izohini tahrirlash", request=EditCommentSerializer, responses=CommentSerializer
    )
    def partial_update(self, request: Request, pk: str) -> Response:
        body = EditCommentSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        try:
            comment = services.edit(_user(request), int(pk), body.validated_data["body"])
        except CommunityError as exc:
            return _failed(exc)
        place = services.place_of(comment)
        if place is None:
            return _closed()
        return Response(_one(place, comment, request))

    @extend_schema(summary="O'z izohini o'chirish", request=None, responses={204: None})
    def destroy(self, request: Request, pk: str) -> Response:
        try:
            services.remove(_user(request), int(pk))
        except CommunityError as exc:
            return _failed(exc)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Izohga ovoz: 1, -1 yoki 0 (qaytarib olish)",
        request=CommunityVoteSerializer,
        responses=CommunityVoteResultSerializer,
    )
    @action(detail=True, methods=["post"])
    def vote(self, request: Request, pk: str) -> Response:
        body = CommunityVoteSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        try:
            score, mine = services.vote(
                _user(request), Kind.COMMENT, int(pk), int(body.validated_data["value"])
            )
        except CommunityError as exc:
            return _failed(exc)
        return Response({"score": score, "my_vote": mine})

    @extend_schema(
        summary="Izoh ustidan shikoyat", request=CommunityReportSerializer, responses={201: None}
    )
    @action(detail=True, methods=["post"])
    def report(self, request: Request, pk: str) -> Response:
        body = CommunityReportSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        try:
            services.report(
                _user(request),
                Kind.COMMENT,
                int(pk),
                body.validated_data["reason"],
                body.validated_data.get("note", ""),
            )
        except CommunityError as exc:
            return _failed(exc)
        return Response(status=status.HTTP_201_CREATED)


class StaffCommentViewSet(StaffViewSet):
    """Moderation after the fact: hidden by reports or by staff, never deleted."""

    queryset = Comment.objects.select_related("author")
    serializer_class = StaffCommentSerializer
    http_method_names = ["get", "post", "head", "options"]
    search_fields: ClassVar[list[str]] = ["body", "author__username"]
    ordering_fields: ClassVar[list[str]] = ["pk", "created_at", "report_count"]

    def get_queryset(self) -> QuerySet[Comment]:
        rows = super().get_queryset()
        params = self.request.query_params
        if params.get("reported") == "1":
            rows = rows.filter(report_count__gt=0)
        if params.get("is_hidden") in ("true", "false"):
            rows = rows.filter(is_hidden=params["is_hidden"] == "true")
        return rows

    def get_serializer_context(self) -> dict[str, Any]:
        context = dict(super().get_serializer_context())
        page = getattr(self, "_page_rows", None)
        if page:
            ids = [row.pk for row in page]
            reasons: dict[int, list[str]] = {}
            for object_id, reason in Report.objects.filter(
                kind=Kind.COMMENT, object_id__in=ids, status=Report.Status.OPEN
            ).values_list("object_id", "reason"):
                reasons.setdefault(object_id, []).append(reason)
            from problems.lookup import slugs_by_id

            slugs = slugs_by_id(
                {row.target_id for row in page if row.target_type == Target.PROBLEM}
            )
            context["reasons"] = reasons
            context["links"] = {
                row.pk: f"/problems/{slugs[row.target_id]}?tab=discussion#c{row.pk}"
                for row in page
                if row.target_type == Target.PROBLEM and row.target_id in slugs
            }
        return context

    def paginate_queryset(self, queryset: Any) -> Any:
        page = super().paginate_queryset(queryset)
        self._page_rows = page
        return page

    def _moderate(self, request: Request, hide: bool) -> Response:
        comment = services.moderate(_user(request), Kind.COMMENT, int(self.kwargs["pk"]), hide=hide)
        self._page_rows = [comment]
        return Response(self.get_serializer(comment).data)

    @extend_schema(summary="Izohni yashirish (shikoyatlar qabul)", request=None)
    @action(detail=True, methods=["post"])
    def hide(self, request: Request, pk: str | None = None) -> Response:
        return self._moderate(request, True)

    @extend_schema(summary="Izohni qaytarish (shikoyatlar rad)", request=None)
    @action(detail=True, methods=["post"])
    def unhide(self, request: Request, pk: str | None = None) -> Response:
        return self._moderate(request, False)


def _address(request: Request) -> str:
    return str(request.META.get("REMOTE_ADDR", ""))


class EntryViewSet(viewsets.GenericViewSet):  # type: ignore[type-arg]
    """Member blogs (decision 2026-11-11 ④): read by anyone, written by members."""

    serializer_class = EntrySerializer
    pagination_class = StandardPagination
    queryset = Entry.objects.none()
    lookup_value_regex = r"\d+"

    def get_permissions(self) -> list[Any]:
        if self.action in ("list", "retrieve", "tags"):
            return [AllowAny()]
        return [IsAuthenticated()]

    def _context(self, request: Request, rows: list[Entry]) -> dict[str, Any]:
        votes: dict[int, int] = {}
        if request.user.is_authenticated and rows:
            votes = dict(
                Vote.objects.filter(
                    user=request.user, kind=Kind.ENTRY, object_id__in=[r.pk for r in rows]
                ).values_list("object_id", "value")
            )
        viewer = request.user.pk if request.user.is_authenticated else None
        return {"votes": votes, "viewer_id": viewer, "request": request}

    @extend_schema(
        summary="Bloglar lentasi",
        parameters=[
            OpenApiParameter("tab", str, enum=list(blog.TABS), required=False),
            OpenApiParameter("tag", str, required=False),
            OpenApiParameter("author", str, required=False),
        ],
    )
    def list(self, request: Request) -> Response:
        params = request.query_params
        tab = params.get("tab", "new")
        rows = blog.feed(
            request.user,
            tab if tab in blog.TABS else "new",
            tag=params.get("tag", ""),
            author=params.get("author", ""),
        )
        page = self.paginate_queryset(rows) or []
        data = EntrySerializer(page, many=True, context=self._context(request, page)).data
        return self.get_paginated_response(data)

    @extend_schema(summary="Blog posti", responses=EntryDetailSerializer)
    def retrieve(self, request: Request, pk: str) -> Response:
        entry = (
            blog.with_comment_count(blog.readable(request.user))
            .select_related("author")
            .filter(pk=int(pk))
            .first()
        )
        if entry is None:
            return Response(
                {"error": {"code": "entry_not_found", "message": "Not found", "details": {}}},
                status=status.HTTP_404_NOT_FOUND,
            )
        blog.count_view(entry, request.user, _address(request))
        return Response(EntryDetailSerializer(entry, context=self._context(request, [entry])).data)

    @extend_schema(
        summary="Blog posti yozish",
        request=EntryWriteSerializer,
        responses={201: EntryDetailSerializer},
    )
    def create(self, request: Request) -> Response:
        body = EntryWriteSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        try:
            entry = blog.create(
                _user(request),
                body.validated_data["title"],
                body.validated_data["body"],
                body.validated_data["tags"],
            )
        except CommunityError as exc:
            return _failed(exc)
        return Response(
            EntryDetailSerializer(entry, context=self._context(request, [])).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Own entry: edit",
        request=EntryWriteSerializer,
        responses=EntryDetailSerializer,
    )
    def partial_update(self, request: Request, pk: str) -> Response:
        body = EntryWriteSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        try:
            entry = blog.edit(
                _user(request),
                int(pk),
                body.validated_data["title"],
                body.validated_data["body"],
                body.validated_data["tags"],
            )
        except CommunityError as exc:
            return _failed(exc)
        return Response(EntryDetailSerializer(entry, context=self._context(request, [entry])).data)

    @extend_schema(summary="Own entry: delete", request=None, responses={204: None})
    def destroy(self, request: Request, pk: str) -> Response:
        try:
            blog.remove(_user(request), int(pk))
        except CommunityError as exc:
            return _failed(exc)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Postga ovoz: 1, -1 yoki 0",
        request=CommunityVoteSerializer,
        responses=CommunityVoteResultSerializer,
    )
    @action(detail=True, methods=["post"])
    def vote(self, request: Request, pk: str) -> Response:
        body = CommunityVoteSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        try:
            score, mine = services.vote(
                _user(request), Kind.ENTRY, int(pk), int(body.validated_data["value"])
            )
        except CommunityError as exc:
            return _failed(exc)
        return Response({"score": score, "my_vote": mine})

    @extend_schema(
        summary="Post ustidan shikoyat", request=CommunityReportSerializer, responses={201: None}
    )
    @action(detail=True, methods=["post"])
    def report(self, request: Request, pk: str) -> Response:
        body = CommunityReportSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        try:
            services.report(
                _user(request),
                Kind.ENTRY,
                int(pk),
                body.validated_data["reason"],
                body.validated_data.get("note", ""),
            )
        except CommunityError as exc:
            return _failed(exc)
        return Response(status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Popular tags of the last 90 days", responses=TagCountSerializer(many=True)
    )
    @action(detail=False, methods=["get"])
    def tags(self, request: Request) -> Response:
        return Response([{"tag": tag, "count": n} for tag, n in blog.popular_tags()])


class StaffEntryViewSet(StaffViewSet):
    """Blog moderation: hidden by reports or by staff, never deleted."""

    queryset = Entry.objects.select_related("author")
    serializer_class = StaffEntrySerializer
    http_method_names = ["get", "post", "head", "options"]
    search_fields: ClassVar[list[str]] = ["title", "body", "author__username"]
    ordering_fields: ClassVar[list[str]] = ["pk", "created_at", "report_count"]

    def get_queryset(self) -> QuerySet[Entry]:
        rows = super().get_queryset()
        if self.request.query_params.get("reported") == "1":
            rows = rows.filter(report_count__gt=0)
        return rows

    def get_serializer_context(self) -> dict[str, Any]:
        context = dict(super().get_serializer_context())
        page = getattr(self, "_page_rows", None)
        if page:
            reasons: dict[int, list[str]] = {}
            for object_id, reason in Report.objects.filter(
                kind=Kind.ENTRY, object_id__in=[row.pk for row in page], status=Report.Status.OPEN
            ).values_list("object_id", "reason"):
                reasons.setdefault(object_id, []).append(reason)
            context["reasons"] = reasons
        return context

    def paginate_queryset(self, queryset: Any) -> Any:
        page = super().paginate_queryset(queryset)
        self._page_rows = page
        return page

    def _moderate(self, request: Request, hide: bool) -> Response:
        entry = services.moderate(_user(request), Kind.ENTRY, int(self.kwargs["pk"]), hide=hide)
        self._page_rows = [entry]
        return Response(self.get_serializer(entry).data)

    @extend_schema(summary="Hide an entry (reports accepted)", request=None)
    @action(detail=True, methods=["post"])
    def hide(self, request: Request, pk: str | None = None) -> Response:
        return self._moderate(request, True)

    @extend_schema(summary="Bring an entry back (reports rejected)", request=None)
    @action(detail=True, methods=["post"])
    def unhide(self, request: Request, pk: str | None = None) -> Response:
        return self._moderate(request, False)


class KarmaTopView(APIView):
    """People by karma: `period=all` (the users table) or `30d` (active authors)."""

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Karma bo'yicha foydalanuvchilar",
        parameters=[
            OpenApiParameter("period", str, enum=list(karma.PERIODS), required=False),
            OpenApiParameter("limit", int, required=False),
        ],
        responses=KarmaRowSerializer(many=True),
    )
    def get(self, request: Request) -> Response:
        period = request.query_params.get("period", "all")
        raw = request.query_params.get("limit", "50")
        limit = min(int(raw), 100) if raw.isdigit() and int(raw) > 0 else 50
        rows = karma.top(period if period in karma.PERIODS else "all", limit)
        return Response(KarmaRowSerializer(rows, many=True).data)
