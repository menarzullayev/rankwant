.PHONY: install lint fmt type test check schema migrate seed run all

VENV := .venv
PY   := $(VENV)/bin/python

# `config.settings` endi `DJANGO_SECRET_KEY` bo'lmasa `ImproperlyConfigured`
# ko'taradi (D5, fail-fast): ma'lum sukut bilan prod ko'tarilmasin. Bu qiymat
# FAQAT mahalliy `make` uchun — production uni `.env.public` dan, CI esa
# workflow `env:` orqali oladi. `?=` — muhitda berilgan qiymatni ustidan
# YOZMAYDI (CI/`tools/ci-local.sh` o'z qiymatini beradi).
export DJANGO_SECRET_KEY ?= local-only-not-for-production

install:
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -q -r requirements-dev.txt

lint:
	$(VENV)/bin/ruff check .
	$(VENV)/bin/ruff format --check .

fmt:
	$(VENV)/bin/ruff check . --fix
	$(VENV)/bin/ruff format .

type:
	$(VENV)/bin/mypy .

test:
	$(PY) -m pytest

check:
	$(PY) manage.py check
	$(PY) manage.py makemigrations --check --dry-run

## OpenAPI sxemasini yangilaydi — CI diff bilan tekshiradi
schema:
	$(PY) manage.py spectacular --file openapi/schema.yml

migrate:
	$(PY) manage.py migrate

seed:
	$(PY) manage.py seed_demo

run:
	$(PY) manage.py runserver

## CI bajaradigan hamma narsa
all: lint type check test schema
