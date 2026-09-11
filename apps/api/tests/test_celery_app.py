"""API jarayonidagi vazifalar loyihaning Celery ilovasiga bog'lanishi kerak."""

from django.conf import settings

from core.tasks import send_email_verify


def test_shared_tasks_publish_to_the_project_broker() -> None:
    # `config` paketi ilovani yuklamasa, `.delay()` Celery'ning standart
    # `amqp://localhost` ilovasiga ketadi va `queue()` xatoni jim yutadi:
    # foydalanuvchi «xat yuborildi» ni ko'radi, xat esa umuman ketmaydi.
    assert send_email_verify.app.main == "rankwant"
    assert send_email_verify.app.conf.broker_url == settings.CELERY_BROKER_URL
