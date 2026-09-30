"""AI Gateway — monolithic module boundary (decision D6, Phase 0 skeleton).

This package is the single home for the AI layer. It is a **plain Python
package** on purpose: no Django app, no ``models.py``, no ``migrations/``,
no entry in ``INSTALLED_APPS``.

Boundary contract — enforced by ``tools/check_ai_boundary.py``:

* it must not import any Django model (``from <app>.models import ...``,
  ``from .models import ...``, ``import <app>.models``);
* it must not import ``django.db`` or ``django.contrib.*``;
* it must not touch ``DATABASE_URL``;
* it must not read test data (``testdata``, ``fixtures/``, ``*.json``).

Why the boundary exists: the AI layer is meant to be extractable later
(Phase 3). If it binds to the DB schema now, extraction becomes
impossible. The static gate forbids that today, while the package is
still empty, so the first line of AI code already obeys the contract.

Scope note: the AI Gateway *runtime* (LLM client, providers, prompts,
endpoints — items 0033-0035) is **Phase 3** and is intentionally absent
here. Phase 0 ships only this skeleton and its gate.
"""

from __future__ import annotations

__all__: list[str] = []
