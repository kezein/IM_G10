"""
buyers.py
CRUD for the `buyer` table. Primary key: BuyerID (a string like 'B-2023-001').

Endpoints:
  GET    /api/buyers        -> all buyers
  GET    /api/buyers/<id>   -> one buyer
  POST   /api/buyers        -> create
  PUT    /api/buyers/<id>   -> update
  DELETE /api/buyers/<id>   -> delete
"""
from flask import Blueprint, request, jsonify
from mysql.connector import Error as MySQLError, IntegrityError
from db import query_all, query_one, execute

buyers_bp = Blueprint("buyers", __name__)

# The exact columns of the buyer table, in order. Used to build SQL safely.
COLUMNS = [
    "BuyerID", "BuyerName", "Birthdate", "Birthplace", "GovID", "TIN",
    "Gender", "Civil_Status", "Address", "Citizenship", "Gross_MonthlyIncome",
    "Tel_Num", "Mobile_Num", "Personal_Email", "Work_Email",
    "Account_Type", "Bank_Name",
]
# Columns that must be provided when creating a buyer (match NOT NULL in schema).
REQUIRED = [
    "BuyerID", "BuyerName", "Birthdate", "Birthplace", "GovID", "TIN",
    "Gender", "Civil_Status", "Address", "Citizenship", "Gross_MonthlyIncome",
    "Mobile_Num", "Personal_Email", "Account_Type", "Bank_Name",
]


@buyers_bp.route("/api/buyers", methods=["GET"])
def list_buyers():
    try:
        return jsonify(ok=True, data=query_all("SELECT * FROM buyer"))
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@buyers_bp.route("/api/buyers/<buyer_id>", methods=["GET"])
def get_buyer(buyer_id):
    try:
        row = query_one("SELECT * FROM buyer WHERE BuyerID = %s", (buyer_id,))
        if row is None:
            return jsonify(ok=False, error="Buyer not found"), 404
        return jsonify(ok=True, data=row)
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@buyers_bp.route("/api/buyers", methods=["POST"])
def create_buyer():
    body = request.get_json(silent=True) or {}
    missing = [c for c in REQUIRED if not body.get(c)]
    if missing:
        return jsonify(ok=False, error=f"Missing required fields: {', '.join(missing)}"), 400

    # Build "INSERT INTO buyer (col, col, ...) VALUES (%s, %s, ...)" safely.
    placeholders = ", ".join(["%s"] * len(COLUMNS))
    col_list = ", ".join(COLUMNS)
    values = [body.get(c) for c in COLUMNS]
    try:
        execute(f"INSERT INTO buyer ({col_list}) VALUES ({placeholders})", values)
        return jsonify(ok=True, data=query_one("SELECT * FROM buyer WHERE BuyerID = %s", (body["BuyerID"],)))
    except IntegrityError:
        return jsonify(ok=False, error=f"Buyer '{body['BuyerID']}' already exists"), 409
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@buyers_bp.route("/api/buyers/<buyer_id>", methods=["PUT"])
def update_buyer(buyer_id):
    body = request.get_json(silent=True) or {}
    # Only update columns that were actually sent (never overwrite the PK).
    fields = [c for c in COLUMNS if c != "BuyerID" and c in body]
    if not fields:
        return jsonify(ok=False, error="No fields to update"), 400

    set_clause = ", ".join(f"{c} = %s" for c in fields)
    values = [body[c] for c in fields] + [buyer_id]
    try:
        affected = execute(f"UPDATE buyer SET {set_clause} WHERE BuyerID = %s", values)
        if affected == 0:
            return jsonify(ok=False, error="Buyer not found"), 404
        return jsonify(ok=True, data=query_one("SELECT * FROM buyer WHERE BuyerID = %s", (buyer_id,)))
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@buyers_bp.route("/api/buyers/<buyer_id>", methods=["DELETE"])
def delete_buyer(buyer_id):
    try:
        affected = execute("DELETE FROM buyer WHERE BuyerID = %s", (buyer_id,))
        if affected == 0:
            return jsonify(ok=False, error="Buyer not found"), 404
        return jsonify(ok=True, data={"deleted": buyer_id})
    except IntegrityError:
        return jsonify(ok=False, error="Cannot delete: other records reference this buyer"), 409
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503
