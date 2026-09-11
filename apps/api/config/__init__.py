# Celery ilovasi Django bilan birga yuklanadi: busiz API jarayonidagi
# `shared_task` lar standart `amqp://localhost` ilovasiga bog'lanadi.
from .celery import app as celery_app

__all__ = ("celery_app",)
