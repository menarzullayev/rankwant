.PHONY: install lint fmt type test check schema migrate seed run all

VENV := .venv
PY   := $(VENV)/bin/python

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
