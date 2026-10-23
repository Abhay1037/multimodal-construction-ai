"""Secure secret loading helpers (Streamlit secrets -> environment variables)."""

import os


def get_secret(key: str, fallback: str = "") -> str:
    """Return the configured value for `key` from Streamlit secrets or env vars."""
    value = ""
    try:
        from streamlit import secrets

        value = secrets.get(key, "") or ""
    except Exception:
        value = ""
    if not value:
        value = os.getenv(key, "") or ""
    return value
