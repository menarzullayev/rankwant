"""The `ai` worker's tasks (ADR-0065 § 2.6).

`tutor.answer` runs on the `ai` queue only, in the `ai-worker` container —
the one place that holds the subscription token. The beat tasks run on the
ordinary worker.
"""

from __future__ import annotations

import logging
from datetime import timedelta
from decimal import Decimal
from typing import Any

from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from ai import gateway
from ai.providers import anthropic_api
from ai.types import AIError, Config
from realtime.bus import publish, user_channel
from tutor import budget, context, gate, limits, services
from tutor.models import Conversation, DailyUse, Message, Report

log = logging.getLogger(__name__)

#: Decision ⑦: a conversation lives 90 days after its last message.
RETENTION = timedelta(days=90)


def provider() -> str:
    """The provider for the next reply (decisions ⑤ and ⑨).

    The Claude API answers while it has a key and the month's budget is not
    spent; otherwise the reply goes to the fallback — `claude -p` — and when
    there is none, the tutor stops (the reply fails and is not counted).
    """
    chosen = settings.AI_PROVIDER
    if chosen == anthropic_api.NAME and (not settings.ANTHROPIC_API_KEY or budget.over_limit()):
        return settings.AI_FALLBACK_PROVIDER
    return chosen


def config() -> Config:
    return Config(
        provider=provider(),
        light_model=settings.AI_MODEL_LIGHT,
        heavy_model=settings.AI_MODEL_HEAVY,
        timeout_s=settings.AI_TIMEOUT_S,
        cli_path=settings.AI_CLI_PATH,
        oauth_token=settings.CLAUDE_CODE_OAUTH_TOKEN,
        api_key=settings.ANTHROPIC_API_KEY,
    )


def _announce(message: Message) -> None:
    slug = message.conversation.problem.slug
    payload = {"problem": slug, "message": message.pk, "status": message.status}
    transaction.on_commit(lambda: publish(user_channel(message.user_id), "tutor", payload))


def _fail(message: Message, code: str) -> None:
    done = Message.objects.filter(pk=message.pk, status=Message.Status.PENDING).update(
        status=Message.Status.FAILED, error=code[:32], answered_at=timezone.now()
    )
    if done:
        limits.give_back(message.user_id, message.created_at)
        message.status = Message.Status.FAILED
        _announce(message)


@shared_task(name="tutor.answer")
def answer(message_id: int) -> None:
    reply = (
        Message.objects.select_related("conversation__problem", "reply_to__attempt__language")
        .filter(pk=message_id, status=Message.Status.PENDING)
        .first()
    )
    if reply is None:
        return
    # The contest may have started while the question waited.
    reason = gate.closed_reason(reply.conversation.problem)
    if reason is not None:
        _fail(reply, reason)
        return
    try:
        result = gateway.ask(context.request(reply), config())
    except AIError as exc:
        log.warning("tutor reply %s failed: %s", message_id, exc)
        _fail(reply, exc.code)
        return
    except Exception:
        log.exception("tutor reply %s failed", message_id)
        _fail(reply, "failed")
        return
    usage = result.usage
    with transaction.atomic():
        stored = Message.objects.filter(pk=reply.pk, status=Message.Status.PENDING).update(
            status=Message.Status.DONE,
            text=result.text,
            model=result.model[:64],
            provider=result.provider[:16],
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            cache_read_tokens=usage.cache_read_tokens,
            cache_write_tokens=usage.cache_write_tokens,
            cost_usd=Decimal(str(round(usage.cost_usd, 6))),
            latency_ms=usage.latency_ms,
            code_removed=result.code_removed,
            answered_at=timezone.now(),
        )
        if not stored:
            # `expire_pending` gave up on it first; the student already saw a failure.
            return
        budget.record(result.model, Decimal(str(round(usage.cost_usd, 6))))
        conversation = Conversation.objects.select_for_update().get(pk=reply.conversation_id)
        if reply.kind == Message.Kind.HINT and reply.hint_level:
            conversation.hint_level = max(conversation.hint_level, reply.hint_level)
        conversation.save(update_fields=["hint_level", "updated_at"])
        reply.status = Message.Status.DONE
        _announce(reply)


@shared_task(name="tutor.expire_pending")
def expire_pending() -> int:
    stale: Any = Message.objects.select_related("conversation__problem").filter(
        status=Message.Status.PENDING, created_at__lt=services.expired_before()
    )
    count = 0
    with transaction.atomic():
        for message in stale:
            _fail(message, "timeout")
            count += 1
    return count


@shared_task(name="tutor.purge_old")
def purge_old() -> int:
    cutoff = timezone.now() - RETENTION
    deleted, _ = Conversation.objects.filter(updated_at__lt=cutoff).delete()
    DailyUse.objects.filter(day__lt=limits.local_day(cutoff)).delete()
    # A handled report goes 90 days after it was handled; an open one stays.
    Report.objects.exclude(status=Report.Status.OPEN).filter(resolved_at__lt=cutoff).delete()
    return deleted
