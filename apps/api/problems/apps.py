from django.apps import AppConfig


class ProblemsConfig(AppConfig):
    name = "problems"

    def ready(self) -> None:
        # Recount solvers' Skills when a problem crosses the hidden-test line.
        from problems import signals  # noqa: F401
