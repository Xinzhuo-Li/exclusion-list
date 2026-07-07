"""Project paths and OIG LEIE schema constants."""

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CLEANED_DIR = DATA_DIR / "cleaned"
DOCS_DIR = ROOT_DIR / "docs"
GUIDES_DIR = DOCS_DIR / "guides"
ARTIFACTS_DIR = DOCS_DIR / "artifacts"
ARTIFACTS_DEDUP_DIR = ARTIFACTS_DIR / "dedup"
SCANS_DIR = DOCS_DIR / "scans"
PROJECT_DOCS_DIR = DOCS_DIR / "project"
SQL_DIR = ROOT_DIR / "sql"


def artifact_run_dir() -> Path:
    """Daily run directory for pipeline JSON artifacts."""
    from datetime import date

    run_dir = ARTIFACTS_DIR / "runs" / date.today().strftime("%Y%m%d")
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir

OIG_COLUMNS = [
    "lastname",
    "firstname",
    "midname",
    "busname",
    "general",
    "specialty",
    "upin",
    "npi",
    "dob",
    "address",
    "city",
    "state",
    "zip_code",
    "excltype",
    "excldate",
    "reindate",
    "waiverdate",
    "waiverstate",
    "list_source",
]

LIST_SOURCE_STATE = "state"
LIST_SOURCE_FEDERAL = "federal"

# Production-active Medicaid state lists (pipeline + DB merge).
ORIGINAL_SOURCE_STATES = ["MD", "MA", "MI", "MS", "MT", "NE"]

# Austin colleague states — integrated after field-semantics sync (2026-07).
AUSTIN_SOURCE_STATES = ["CA", "NY", "NC", "ND", "OH", "NJ", "PA"]

# Le Luo colleague states — GA through ME (2026-07).
LE_LUO_SOURCE_STATES = ["GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME"]

# AmeeBeez colleague states — AL through FL excluding CA (2026-07).
AMEEBEEZ_SOURCE_STATES = ["AL", "AK", "AZ", "AR", "CO", "CT", "DE", "DC", "FL"]

# FredericYan colleague states (2026-07).
FREDERIC_SOURCE_STATES = ["SC", "TN", "TX", "VT", "WA", "WV", "WY"]

ALL_SOURCE_STATES = (
    ORIGINAL_SOURCE_STATES
    + AUSTIN_SOURCE_STATES
    + LE_LUO_SOURCE_STATES
    + AMEEBEEZ_SOURCE_STATES
    + FREDERIC_SOURCE_STATES
)
ACTIVE_SOURCE_STATES = ALL_SOURCE_STATES
CLEANED_STATE_CODES = [code.lower() for code in ACTIVE_SOURCE_STATES]

FEDERAL_CLEANED_FILE = "federal_oig.csv"

OIG_FIELD_LENGTHS = {
    "lastname": 20,
    "firstname": 15,
    "midname": 15,
    "busname": 30,
    "general": 20,
    "specialty": 20,
    "upin": 6,
    "npi": 10,
    "dob": 8,
    "address": 30,
    "city": 20,
    "state": 2,
    "zip_code": 5,
    "excltype": 9,
    "excldate": 8,
    "reindate": 8,
    "waiverdate": 8,
    "waiverstate": 2,
}

INDEFINITE_DATE_SERIAL = 401768
