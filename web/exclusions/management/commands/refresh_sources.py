from django.core.management.base import BaseCommand
from django.db.models import Count, Max
from django.utils import timezone

from exclusions.models import DataSource, ExclusionRecord
from exclusions.queries import STATE_NAMES

AUSTIN_SOURCE_STATES = {"CA", "NY", "NC", "ND", "OH", "NJ", "PA"}
LE_LUO_SOURCE_STATES = {"GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME"}
AMEEBEEZ_SOURCE_STATES = {"AL", "AK", "AZ", "AR", "CO", "CT", "DE", "DC", "FL"}
FREDERIC_SOURCE_STATES = {"SC", "TN", "TX", "VT", "WA", "WV", "WY"}


def _contributor_for(code: str) -> str:
    if code in AUSTIN_SOURCE_STATES:
        return "AustinGH32"
    if code in LE_LUO_SOURCE_STATES:
        return "le-luo327"
    if code in AMEEBEEZ_SOURCE_STATES:
        return "AmeeBeez"
    if code in FREDERIC_SOURCE_STATES:
        return "FredericYan02"
    if code == "OIG":
        return "le-luo327"
    return ""


def _list_source_for(code: str) -> str:
    return "federal" if code == "OIG" else "state"


class Command(BaseCommand):
    help = "Refresh DataSource metadata from exclusion_main aggregates."

    def handle(self, *args, **options):
        aggregates = (
            ExclusionRecord.objects.values("source_state")
            .annotate(record_count=Count("id"), last_loaded_at=Max("loaded_at"))
            .order_by("source_state")
        )
        now = timezone.now()
        updated = 0
        for row in aggregates:
            code = row["source_state"]
            defaults = {
                "name": STATE_NAMES.get(code, code),
                "contributor": _contributor_for(code),
                "list_source": _list_source_for(code),
                "record_count": row["record_count"],
                "last_merged_at": row["last_loaded_at"] or now,
            }
            _, created = DataSource.objects.update_or_create(code=code, defaults=defaults)
            action = "Created" if created else "Updated"
            self.stdout.write(
                f"{action} {code}: {defaults['name']} ({defaults['record_count']} records)"
            )
            updated += 1
        active_codes = {row["source_state"] for row in aggregates}
        removed, _ = DataSource.objects.exclude(code__in=active_codes).delete()
        if removed:
            self.stdout.write(self.style.WARNING(f"Removed {removed} stale data source(s)."))
        self.stdout.write(self.style.SUCCESS(f"Refreshed {updated} data source(s)."))
