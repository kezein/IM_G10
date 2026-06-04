"""
validation.py
Pure, reusable input checks shared by the route files. No Flask, no DB, so it can
be unit-tested on its own. Used as a LIGHT server-side guard; the frontend does the
primary, user-facing validation.
"""
import re

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_NUMERIC_RE = re.compile(r"^\d+(\.\d+)?$")
_ALPHA_SPACES_RE = re.compile(r"^[A-Za-z ]+$")


def is_valid_email(value):
    return bool(_EMAIL_RE.match((value or "").strip()))


def is_numeric(value):
    return bool(_NUMERIC_RE.match((value or "").strip()))


def is_alpha_spaces(value):
    return bool(_ALPHA_SPACES_RE.match((value or "").strip()))


def first_invalid(body, email_fields=(), numeric_fields=(), alpha_fields=()):
    """
    Return the name of the first field that is present but malformed, or None if all
    present fields are valid. Empty/missing values are skipped here (required-ness is
    enforced separately by each route's REQUIRED list).
    """
    for f in email_fields:
        v = body.get(f)
        if v not in (None, "") and not is_valid_email(v):
            return f
    for f in numeric_fields:
        v = body.get(f)
        if v not in (None, "") and not is_numeric(str(v)):
            return f
    for f in alpha_fields:
        v = body.get(f)
        if v not in (None, "") and not is_alpha_spaces(v):
            return f
    return None
