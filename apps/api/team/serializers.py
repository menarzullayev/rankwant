from __future__ import annotations

from rest_framework import serializers

from team.models import Department, Member, Role

DEPARTMENT_FIELDS = ["id", "name_uz", "name_ru", "name_en", "order"]
ROLE_FIELDS = [
    "id",
    "department",
    "title_uz",
    "title_ru",
    "title_en",
    "about_uz",
    "about_ru",
    "about_en",
    "reports_to_uz",
    "reports_to_ru",
    "reports_to_en",
    "status_uz",
    "status_ru",
    "status_en",
    "badge",
    "hue",
    "tone",
    "order",
]
MEMBER_FIELDS = [
    "id",
    "section",
    "name",
    "title_uz",
    "title_ru",
    "title_en",
    "context_uz",
    "context_ru",
    "context_en",
    "photo_url",
    "telegram_url",
    "github_url",
    "linkedin_url",
    "instagram_url",
    "website_url",
    "holds_all_roles",
    "order",
]


class TeamPageDepartmentSerializer(serializers.ModelSerializer[Department]):
    class Meta:
        model = Department
        fields = DEPARTMENT_FIELDS


class TeamPageRoleSerializer(serializers.ModelSerializer[Role]):
    class Meta:
        model = Role
        fields = ROLE_FIELDS


class TeamPageMemberSerializer(serializers.ModelSerializer[Member]):
    class Meta:
        model = Member
        fields = MEMBER_FIELDS


class TeamPageSerializer(serializers.Serializer[dict[str, object]]):
    """The whole page in one response: it is small and always read together."""

    departments = TeamPageDepartmentSerializer(many=True)
    roles = TeamPageRoleSerializer(many=True)
    members = TeamPageMemberSerializer(many=True)


def clean_photo(value: str) -> str:
    """A photo is a site path or an https URL — nothing a browser would run."""
    value = value.strip()
    if not value:
        return value
    site_path = value.startswith("/") and not value.startswith("//")
    if not (site_path or value.startswith("https://")):
        raise serializers.ValidationError("Use a site path (/team/photo.jpg) or an https:// URL")
    return value


class StaffTeamDepartmentSerializer(serializers.ModelSerializer[Department]):
    role_count = serializers.IntegerField(source="roles.count", read_only=True)

    class Meta:
        model = Department
        fields = [*DEPARTMENT_FIELDS, "role_count"]


class StaffTeamRoleSerializer(serializers.ModelSerializer[Role]):
    department_name = serializers.CharField(source="department.name_uz", read_only=True)

    class Meta:
        model = Role
        fields = [*ROLE_FIELDS, "department_name", "is_published", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class StaffTeamMemberSerializer(serializers.ModelSerializer[Member]):
    class Meta:
        model = Member
        fields = [*MEMBER_FIELDS, "is_published", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]

    def validate_photo_url(self, value: str) -> str:
        return clean_photo(value)

    def validate(self, attrs: dict[str, object]) -> dict[str, object]:
        # The database refuses a second holder too; this says why in words.
        if attrs.get("holds_all_roles"):
            others = Member.objects.filter(holds_all_roles=True)
            if self.instance is not None:
                others = others.exclude(pk=self.instance.pk)
            if others.exists():
                raise serializers.ValidationError(
                    {"holds_all_roles": "Another member already holds every role"}
                )
        return attrs
