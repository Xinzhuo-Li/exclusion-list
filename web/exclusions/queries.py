"""Shared search and aggregation logic for web UI and REST API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.db.models import Count, Max, QuerySet

from .models import DataSource, ExclusionRecord

STATE_NAMES = {
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MS": "Mississippi",
    "MT": "Montana",
    "NE": "Nebraska",
    "CA": "California",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "NJ": "New Jersey",
    "PA": "Pennsylvania",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "DC": "District of Columbia",
    "FL": "Florida",
    "SC": "South Carolina",
    "TN": "Tennessee",
    "TX": "Texas",
    "VT": "Vermont",
    "WA": "Washington",
    "WV": "West Virginia",
    "WY": "Wyoming",
    "OIG": "Federal LEIE",
}


@dataclass
class SearchParams:
    firstname: str = ""
    midname: str = ""
    lastname: str = ""
    busname: str = ""
    npi: str = ""


def parse_search_params(data: dict[str, Any]) -> SearchParams:
    return SearchParams(
        firstname=(data.get("firstname") or "").strip(),
        midname=(data.get("midname") or "").strip(),
        lastname=(data.get("lastname") or "").strip(),
        busname=(data.get("busname") or "").strip(),
        npi=(data.get("npi") or "").strip(),
    )


def search_exclusions(params: SearchParams) -> QuerySet[ExclusionRecord]:
    qs = ExclusionRecord.objects.all()

    if params.firstname:
        qs = qs.filter(firstname__icontains=params.firstname)
    if params.midname:
        qs = qs.filter(midname__icontains=params.midname)
    if params.lastname:
        qs = qs.filter(lastname__icontains=params.lastname)
    if params.busname:
        qs = qs.filter(busname__icontains=params.busname)
    if params.npi:
        qs = qs.filter(npi=params.npi)

    return qs.order_by("-excldate", "id")


def get_source_state_choices() -> list[tuple[str, str]]:
    rows = (
        ExclusionRecord.objects.values("source_state")
        .annotate(count=Count("id"))
        .order_by("source_state")
    )
    choices = []
    for row in rows:
        code = row["source_state"]
        label = STATE_NAMES.get(code, code)
        choices.append((code, f"{label} ({code}) — {row['count']:,}"))
    return choices


def get_sources() -> list[dict[str, Any]]:
    """Return available data sources with counts; merge metadata when present."""
    aggregates = (
        ExclusionRecord.objects.values("source_state")
        .annotate(record_count=Count("id"), last_loaded_at=Max("loaded_at"))
        .order_by("source_state")
    )
    metadata = {ds.code: ds for ds in DataSource.objects.all()}
    sources = []
    for row in aggregates:
        code = row["source_state"]
        meta = metadata.get(code)
        sources.append(
            {
                "code": code,
                "name": meta.name if meta else STATE_NAMES.get(code, code),
                "contributor": meta.contributor if meta else "",
                "record_count": row["record_count"],
                "last_merged_at": (
                    meta.last_merged_at.isoformat()
                    if meta and meta.last_merged_at
                    else (
                        row["last_loaded_at"].isoformat()
                        if row["last_loaded_at"]
                        else None
                    )
                ),
            }
        )
    return sources


def _source_sort_key(code: str) -> tuple[int, str]:
    """Federal LEIE (OIG) first; remaining sources alphabetical."""
    return (0, "") if code == "OIG" else (1, code)


def get_stats() -> dict[str, Any]:
    total = ExclusionRecord.objects.count()
    by_source = list(
        ExclusionRecord.objects.values("source_state")
        .annotate(count=Count("id"))
    )
    by_source.sort(key=lambda row: _source_sort_key(row["source_state"]))
    return {
        "total_records": total,
        "source_count": len(by_source),
        "by_source_state": [
            {
                "source_state": row["source_state"],
                "name": STATE_NAMES.get(row["source_state"], row["source_state"]),
                "count": row["count"],
            }
            for row in by_source
        ],
    }
