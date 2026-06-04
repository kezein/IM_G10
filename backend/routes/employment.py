"""
employment.py
CRUD for the `employment` table. Primary key: EmploymentID.
"""
from flask import Blueprint, request, jsonify
from mysql.connector import Error as MySQLError, IntegrityError
from db import query_all, query_one, execute
from routes.validation import first_invalid

employment_bp = Blueprint("employment", __name__)

COLUMNS = [
    "EmploymentID", "BuyerID", "Emp_Type", "Emp_Name", "Emp_Address",
    "Emp_TelNum", "Emp_EmailAdd", "Occupation", "Position", "Tenure",
    "Occupation_rank",
]
REQUIRED = [
    "EmploymentID", "BuyerID", "Emp_Type", "Emp_Name", "Emp_Address",
    "Occupation", "Position", "Tenure",
]


@employment_bp.route("/api/employment", methods=["GET"])
def list_employment():
    try:
        return jsonify(ok=True, data=query_all("SELECT * FROM employment"))
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@employment_bp.route("/api/employment/<emp_id>", methods=["GET"])
def get_employment(emp_id):
    try:
        row = query_one("SELECT * FROM employment WHERE EmploymentID = %s", (emp_id,))
        if row is None:
            return jsonify(ok=False, error="Employment record not found"), 404
        return jsonify(ok=True, data=row)
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@employment_bp.route("/api/employment", methods=["POST"])
def create_employment():
    body = request.get_json(silent=True) or {}
    missing = [c for c in REQUIRED if body.get(c) in (None, "")]
    if missing:
        return jsonify(ok=False, error=f"Missing required fields: {', '.join(missing)}"), 400
    bad = first_invalid(body, email_fields=["Emp_EmailAdd"],
                        numeric_fields=["Tenure"])
    if bad:
        return jsonify(ok=False, error=f"Invalid value for field: {bad}"), 400
    placeholders = ", ".join(["%s"] * len(COLUMNS))
    col_list = ", ".join(COLUMNS)
    values = [body.get(c) for c in COLUMNS]
    try:
        execute(f"INSERT INTO employment ({col_list}) VALUES ({placeholders})", values)
        return jsonify(ok=True, data=query_one("SELECT * FROM employment WHERE EmploymentID = %s", (body["EmploymentID"],)))
    except IntegrityError:
        return jsonify(ok=False, error=f"Employment '{body['EmploymentID']}' already exists"), 409
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@employment_bp.route("/api/employment/<emp_id>", methods=["PUT"])
def update_employment(emp_id):
    body = request.get_json(silent=True) or {}
    fields = [c for c in COLUMNS if c != "EmploymentID" and c in body]
    if not fields:
        return jsonify(ok=False, error="No fields to update"), 400
    set_clause = ", ".join(f"{c} = %s" for c in fields)
    values = [body[c] for c in fields] + [emp_id]
    try:
        affected = execute(f"UPDATE employment SET {set_clause} WHERE EmploymentID = %s", values)
        if affected == 0:
            return jsonify(ok=False, error="Employment record not found"), 404
        return jsonify(ok=True, data=query_one("SELECT * FROM employment WHERE EmploymentID = %s", (emp_id,)))
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@employment_bp.route("/api/employment/<emp_id>", methods=["DELETE"])
def delete_employment(emp_id):
    try:
        affected = execute("DELETE FROM employment WHERE EmploymentID = %s", (emp_id,))
        if affected == 0:
            return jsonify(ok=False, error="Employment record not found"), 404
        return jsonify(ok=True, data={"deleted": emp_id})
    except IntegrityError:
        return jsonify(ok=False, error="Cannot delete: other records still reference this record"), 409
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503
