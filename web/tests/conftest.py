import pytest


def _postgres_available() -> bool:
    try:
        from django.db import connection

        connection.ensure_connection()
        return True
    except Exception:
        return False


def pytest_collection_modifyitems(config, items):
    if _postgres_available():
        return
    reason = "PostgreSQL unavailable — skipping database integration tests"
    skip = pytest.mark.skip(reason=reason)
    for item in items:
        if "django_db" in item.keywords:
            item.add_marker(skip)


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    if not _postgres_available():
        pytest.skip("PostgreSQL unavailable")
    with django_db_blocker.unblock():
        from exclusions.models import ExclusionRecord

        try:
            ExclusionRecord.objects.exists()
        except Exception as exc:
            pytest.skip(f"exclusion_main unavailable: {exc}")
