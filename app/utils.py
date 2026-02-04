import re
from datetime import datetime, timezone


PHONE_RE = re.compile(r"^\+?\d{9,15}$")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def valid_min_len(s: str, n: int) -> bool:
    s = (s or "").strip()
    return len(s) >= n


def normalize_phone(s: str) -> str:
    s = (s or "").strip().replace(" ", "").replace("-", "")
    return s


def valid_phone(s: str) -> bool:
    s = normalize_phone(s)
    return bool(PHONE_RE.match(s))
