"""Project paths and OIG LEIE schema constants."""

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CLEANED_DIR = DATA_DIR / "cleaned"
DOCS_DIR = ROOT_DIR / "docs"
SQL_DIR = ROOT_DIR / "sql"

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
]

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
