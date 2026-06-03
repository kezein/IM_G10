"""
spouse.py
CRUD for the `spouse` table. Primary key: BuyerID (1 spouse per buyer).
Most columns are optional (a single buyer has no spouse).
"""
from flask import Blueprint, request, jsonify
from mysql.connector import Error as MySQLError, IntegrityError
from db import query_all, query_one, execute

spouse_bp = Blueprint("spouse", __name__)

COLUMNS = [
    "BuyerID", "Sps_Name", "Sps_Bdate", "Sps_Bplace", "Sps_Citizenship",
    "Sps_GovID", "Sps_TIN", "Sps_TelNum", "Sps_EmailAdd", "Sps_MobNum",
    "Sps_GrossMonthlyIncome",
]
REQUIRED = ["BuyerID"]   # only the key is mandatory; spouse details are optional


@spouse_bp.route("/api/spouse", methods=["GET"])
def list_spouse():
    try:
        return jsonify(ok=True, data=query_all("SELECT * FROM spouse"))
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@spouse_bp.route("/api/spouse/<buyer_id>", methods=["GET"])
def get_spouse(buyer_id):
    try:
        row = query_one("SELECT * FROM spouse WHERE BuyerID = %s", (buyer_id,))
        if row is None:
            return jsonify(ok=False, error="Spouse not found"), 404
        return jsonify(ok=True, data=row)
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@spouse_bp.route("/api/spouse", methods=["POST"])
def create_spouse():
    body = request.get_json(silent=True) or {}
    missing = [c for c in REQUIRED if not body.get(c)]
    if missing:
        return jsonify(ok=False, error=f"Missing required fields: {', '.join(missing)}"), 400

    placeholders = ", ".join(["%s"] * len(COLUMNS))
    col_list = ", ".join(COLUMNS)
    values = [body.get(c) for c in COLUMNS]
    try:
        execute(f"INSERT INTO spouse ({col_list}) VALUES ({placeholders})", values)
        return jsonify(ok=True, data=query_one("SELECT * FROM spouse WHERE BuyerID = %s", (body["BuyerID"],)))
    except IntegrityError:
        return jsonify(ok=False, error=f"Spouse for buyer '{body['BuyerID']}' already exists"), 409
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@spouse_bp.route("/api/spouse/<buyer_id>", methods=["PUT"])
def update_spouse(buyer_id):
    body = request.get_json(silent=True) or {}
    fields = [c for c in COLUMNS if c != "BuyerID" and c in body]
    if not fields:
        return jsonify(ok=False, error="No fields to update"), 400
    set_clause = ", ".join(f"{c} = %s" for c in fields)
    values = [body[c] for c in fields] + [buyer_id]
    try:
        affected = execute(f"UPDATE spouse SET {set_clause} WHERE BuyerID = %s", values)
        if affected == 0:
            return jsonify(ok=False, error="Spouse not found"), 404
        return jsonify(ok=True, data=query_one("SELECT * FROM spouse WHERE BuyerID = %s", (buyer_id,)))
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@spouse_bp.route("/api/spouse/<buyer_id>", methods=["DELETE"])
def delete_spouse(buyer_id):
    try:
        affected = execute("DELETE FROM spouse WHERE BuyerID = %s", (buyer_id,))
        if affected == 0:
            return jsonify(ok=False, error="Spouse not found"), 404
        return jsonify(ok=True, data={"deleted": buyer_id})
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503
