"""Jamoa amallari — yaratish, kod bilan qo'shilish, chiqish."""

from __future__ import annotations

from django.db import IntegrityError, transaction

from core.models import User
from profiles.models import Team, TeamMember

#: Bitta odam yaratadigan jamoalar soni — kod tarqatib spam qilishning oldini oladi.
MAX_OWNED = 5


class TeamError(Exception):
    """Foydalanuvchiga ko'rsatiladigan sabab bilan."""


class TeamForbidden(TeamError):
    """Amal faqat jamoa egasiga ruxsat etilgan."""


def code_from(value: str) -> str:
    """Kod yoki to'liq havola — ikkalasi ham qabul qilinadi."""
    value = value.strip()
    if "join=" in value:
        value = value.split("join=", 1)[1]
    return value.split("&", 1)[0].rstrip("/").rsplit("/", 1)[-1]


@transaction.atomic
def create(user: User, name: str) -> Team:
    name = name.strip()
    if len(name) < 2:
        raise TeamError("Jamoa nomi kamida 2 belgi bo'lsin")
    owned = TeamMember.objects.filter(user=user, role=TeamMember.Role.OWNER).count()
    if owned >= MAX_OWNED:
        raise TeamError(f"Ko'pi bilan {MAX_OWNED} ta jamoa yaratish mumkin")
    team = Team.objects.create(name=name, created_by=user, join_code=Team.new_code())
    TeamMember.objects.create(team=team, user=user, role=TeamMember.Role.OWNER)
    return team


@transaction.atomic
def join(user: User, code: str) -> Team:
    # Qulf: to'lib qolgan jamoaga parallel so'rovlar bilan ortiqcha a'zo qo'shilmasin.
    team = Team.objects.select_for_update().filter(join_code=code_from(code)).first()
    if team is None:
        raise TeamError("Kod noto'g'ri yoki eskirgan")
    if TeamMember.objects.filter(team=team, user=user).exists():
        raise TeamError("Siz allaqachon shu jamoadasiz")
    if team.members.count() >= Team.MAX_MEMBERS:
        raise TeamError(f"Jamoa to'lgan ({Team.MAX_MEMBERS} kishi)")
    try:
        with transaction.atomic():
            TeamMember.objects.create(team=team, user=user)
    except IntegrityError as exc:
        raise TeamError("Siz allaqachon shu jamoadasiz") from exc
    return team


def _require_owner(team: Team, user: User) -> None:
    if not TeamMember.objects.filter(team=team, user=user, role=TeamMember.Role.OWNER).exists():
        raise TeamForbidden("Bu amal faqat jamoa egasiga ruxsat etilgan")


def refresh_code(team: Team, user: User) -> Team:
    """Eski havola kuchini yo'qotadi — tarqalib ketgan kodni yopish uchun."""
    _require_owner(team, user)
    team.join_code = Team.new_code()
    team.save(update_fields=["join_code"])
    return team


def delete(team: Team, user: User) -> None:
    _require_owner(team, user)
    team.delete()


@transaction.atomic
def leave(team: Team, user: User) -> None:
    """Ega ketsa egalik eng eski a'zoga o'tadi; yolg'iz ega ketsa jamoa o'chadi."""
    locked = Team.objects.select_for_update().get(pk=team.pk)
    member = TeamMember.objects.filter(team=locked, user=user).first()
    if member is None:
        raise TeamError("Siz bu jamoada emassiz")
    member.delete()
    if member.role != TeamMember.Role.OWNER:
        return
    heir = locked.members.order_by("joined_at", "id").first()
    if heir is None:
        locked.delete()
        return
    heir.role = TeamMember.Role.OWNER
    heir.save(update_fields=["role"])


def remove(team: Team, owner: User, username: str) -> None:
    _require_owner(team, owner)
    member = TeamMember.objects.filter(team=team, user__username=username).first()
    if member is None:
        raise TeamError("A'zo topilmadi")
    if member.user_id == owner.pk:
        raise TeamError("O'zingiz uchun «Jamoadan chiqish» tugmasini ishlating")
    member.delete()


def leave_all(user: User) -> None:
    """Hisob o'chirilganda — egalik qolganlarga o'tadi."""
    for membership in list(TeamMember.objects.filter(user=user).select_related("team")):
        leave(membership.team, user)
