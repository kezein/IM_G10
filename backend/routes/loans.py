"""
loans.py
CRUD for the `loan` table. Primary key: LoanID.
"""
import re
import datetime
from flask import Blueprint, request, jsonify
from mysql.connector import Error as MySQLError, IntegrityError
from db import query_all, query_one, execute

loans_bp = Blueprint("loans", __name__)

COLUMNS = [
    "LoanID", "BuyerID", "UnitID", "Finance_Type", "DP_Term", "Loan_Term",
    "Purchase_Purpose", "Source_Funds", "LoanAmount", "Downpayment",
    "ReservationFee", "Sell_Price", "OrPr_Num", "OrPr_Date",
    "Booking_Officer", "ProcessingFee",
]
# Columns the buyer must supply. LoanID is auto-generated; the staff-assigned
# columns (OrPr_*, Booking_Officer, ProcessingFee) get neutral defaults until
# staff fill them in, and are displayed as "—" in the UI (no schema change).
STAFF_DEFAULTS = {"OrPr_Num": "", "Booking_Officer": "", "ProcessingFee": 0}
REQUIRED = [c for c in COLUMNS if c not in
            ("LoanID", "OrPr_Num", "OrPr_Date", "Booking_Officer", "ProcessingFee")]


def next_loan_id(existing_ids, year):
    """Return the next loan id 'L-YYYY-NNN' for `year`, based on existing ids."""
    pattern = re.compile(rf"^L-{year}-(\d+)$")
    max_n = 0
    for lid in existing_ids:
        m = pattern.match(lid or "")
        if m:
            max_n = max(max_n, int(m.group(1)))
    return f"L-{year}-{max_n + 1:03d}"


@loans_bp.route("/api/loans", methods=["GET"])
def list_loans():
    try:
        return jsonify(ok=True, data=query_all("SELECT * FROM loan"))
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@loans_bp.route("/api/loans/<loan_id>", methods=["GET"])
def get_loan(loan_id):
    try:
        row = query_one("SELECT * FROM loan WHERE LoanID = %s", (loan_id,))
        if row is None:
            return jsonify(ok=False, error="Loan not found"), 404
        return jsonify(ok=True, data=row)
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@loans_bp.route("/api/loans", methods=["POST"])
def create_loan():
    body = request.get_json(silent=True) or {}
    missing = [c for c in REQUIRED if body.get(c) in (None, "")]
    if missing:
        return jsonify(ok=False, error=f"Missing required fields: {', '.join(missing)}"), 400

    # Auto-generate LoanID server-side (users never type it).
    year = datetime.datetime.now().year
    existing = [r["LoanID"] for r in query_all("SELECT LoanID FROM loan")]
    loan_id = next_loan_id(existing, year)

    # Build the full value set: client values + neutral staff defaults + today's
    # OrPr_Date placeholder (NOT NULL date column; rendered as "—" in the UI).
    today = datetime.date.today().isoformat()
    values = []
    for c in COLUMNS:
        if c == "LoanID":
            values.append(loan_id)
        elif c == "OrPr_Date":
            values.append(body.get(c) or today)
        elif c in STAFF_DEFAULTS:
            values.append(body.get(c) if body.get(c) not in (None, "") else STAFF_DEFAULTS[c])
        else:
            values.append(body.get(c))

    placeholders = ", ".join(["%s"] * len(COLUMNS))
    col_list = ", ".join(COLUMNS)
    try:
        execute(f"INSERT INTO loan ({col_list}) VALUES ({placeholders})", values)
        return jsonify(ok=True, data=query_one("SELECT * FROM loan WHERE LoanID = %s", (loan_id,)))
    except IntegrityError:
        return jsonify(ok=False, error=f"Loan '{loan_id}' already exists"), 409
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@loans_bp.route("/api/loans/<loan_id>", methods=["PUT"])
def update_loan(loan_id):
    body = request.get_json(silent=True) or {}
    fields = [c for c in COLUMNS if c != "LoanID" and c in body]
    if not fields:
        return jsonify(ok=False, error="No fields to update"), 400
    set_clause = ", ".join(f"{c} = %s" for c in fields)
    values = [body[c] for c in fields] + [loan_id]
    try:
        affected = execute(f"UPDATE loan SET {set_clause} WHERE LoanID = %s", values)
        if affected == 0:
            return jsonify(ok=False, error="Loan not found"), 404
        return jsonify(ok=True, data=query_one("SELECT * FROM loan WHERE LoanID = %s", (loan_id,)))
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@loans_bp.route("/api/loans/<loan_id>", methods=["DELETE"])
def delete_loan(loan_id):
    try:
        affected = execute("DELETE FROM loan WHERE LoanID = %s", (loan_id,))
        if affected == 0:
            return jsonify(ok=False, error="Loan not found"), 404
        return jsonify(ok=True, data={"deleted": loan_id})
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503
