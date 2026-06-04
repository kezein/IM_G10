"""
household.py
CRUD for the `household` table. Primary key: HouseholdID.
"""
from flask import Blueprint, request, jsonify
from mysql.connector import Error as MySQLError, IntegrityError
from db import query_all, query_one, execute

household_bp = Blueprint("household", __name__)

COLUMNS = [
    "HouseholdID", "BuyerID", "Household_Details", "Num_children",
    "Num_parents", "Num_others", "Address", "Home_Ownership", "Length_ofStay",
]
REQUIRED = [
    "HouseholdID", "BuyerID", "Num_children", "Num_parents", "Num_others",
    "Address", "Home_Ownership",
]


@household_bp.route("/api/household", methods=["GET"])
def list_household():
    try:
        return jsonify(ok=True, data=query_all("SELECT * FROM household"))
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@household_bp.route("/api/household/<hh_id>", methods=["GET"])
def get_household(hh_id):
    try:
        row = query_one("SELECT * FROM household WHERE HouseholdID = %s", (hh_id,))
        if row is None:
            return jsonify(ok=False, error="Household not found"), 404
        return jsonify(ok=True, data=row)
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@household_bp.route("/api/household", methods=["POST"])
def create_household():
    body = request.get_json(silent=True) or {}
    # Note: 0 is a valid count, so check for None/"" not falsiness.
    missing = [c for c in REQUIRED if body.get(c) in (None, "")]
    if missing:
        return jsonify(ok=False, error=f"Missing required fields: {', '.join(missing)}"), 400
    placeholders = ", ".join(["%s"] * len(COLUMNS))
    col_list = ", ".join(COLUMNS)
    values = [body.get(c) for c in COLUMNS]
    try:
        execute(f"INSERT INTO household ({col_list}) VALUES ({placeholders})", values)
        return jsonify(ok=True, data=query_one("SELECT * FROM household WHERE HouseholdID = %s", (body["HouseholdID"],)))
    except IntegrityError:
        return jsonify(ok=False, error=f"Household '{body['HouseholdID']}' already exists"), 409
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@household_bp.route("/api/household/<hh_id>", methods=["PUT"])
def update_household(hh_id):
    body = request.get_json(silent=True) or {}
    fields = [c for c in COLUMNS if c != "HouseholdID" and c in body]
    if not fields:
        return jsonify(ok=False, error="No fields to update"), 400
    set_clause = ", ".join(f"{c} = %s" for c in fields)
    values = [body[c] for c in fields] + [hh_id]
    try:
        affected = execute(f"UPDATE household SET {set_clause} WHERE HouseholdID = %s", values)
        if affected == 0:
            return jsonify(ok=False, error="Household not found"), 404
        return jsonify(ok=True, data=query_one("SELECT * FROM household WHERE HouseholdID = %s", (hh_id,)))
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@household_bp.route("/api/household/<hh_id>", methods=["DELETE"])
def delete_household(hh_id):
    try:
        affected = execute("DELETE FROM household WHERE HouseholdID = %s", (hh_id,))
        if affected == 0:
            return jsonify(ok=False, error="Household not found"), 404
        return jsonify(ok=True, data={"deleted": hh_id})
    except IntegrityError:
        return jsonify(ok=False, error="Cannot delete: other records still reference this record"), 409
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503
