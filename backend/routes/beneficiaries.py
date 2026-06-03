"""
beneficiaries.py
CRUD for the `beneficiary` table.
Composite primary key: (BeneficiaryID, BenF_Name) -> one ID can list several
named beneficiaries. Single-record routes need BOTH parts, passed as query
params, e.g. /api/beneficiaries/one?id=BEN-001&name=Jemie%20Velasco
"""
from flask import Blueprint, request, jsonify
from mysql.connector import Error as MySQLError, IntegrityError
from db import query_all, query_one, execute

beneficiaries_bp = Blueprint("beneficiaries", __name__)

COLUMNS = ["BeneficiaryID", "BuyerID", "BenF_Name", "BenF_Bdate", "Relationship"]
REQUIRED = ["BeneficiaryID", "BenF_Name"]   # the two PK parts


@beneficiaries_bp.route("/api/beneficiaries", methods=["GET"])
def list_beneficiaries():
    try:
        return jsonify(ok=True, data=query_all("SELECT * FROM beneficiary"))
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@beneficiaries_bp.route("/api/beneficiaries/one", methods=["GET"])
def get_beneficiary():
    ben_id = request.args.get("id")
    name = request.args.get("name")
    if not ben_id or not name:
        return jsonify(ok=False, error="id and name query params required"), 400
    try:
        row = query_one(
            "SELECT * FROM beneficiary WHERE BeneficiaryID = %s AND BenF_Name = %s",
            (ben_id, name),
        )
        if row is None:
            return jsonify(ok=False, error="Beneficiary not found"), 404
        return jsonify(ok=True, data=row)
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@beneficiaries_bp.route("/api/beneficiaries", methods=["POST"])
def create_beneficiary():
    body = request.get_json(silent=True) or {}
    missing = [c for c in REQUIRED if not body.get(c)]
    if missing:
        return jsonify(ok=False, error=f"Missing required fields: {', '.join(missing)}"), 400
    placeholders = ", ".join(["%s"] * len(COLUMNS))
    col_list = ", ".join(COLUMNS)
    values = [body.get(c) for c in COLUMNS]
    try:
        execute(f"INSERT INTO beneficiary ({col_list}) VALUES ({placeholders})", values)
        row = query_one(
            "SELECT * FROM beneficiary WHERE BeneficiaryID = %s AND BenF_Name = %s",
            (body["BeneficiaryID"], body["BenF_Name"]),
        )
        return jsonify(ok=True, data=row)
    except IntegrityError:
        return jsonify(ok=False, error="That beneficiary (ID + name) already exists"), 409
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@beneficiaries_bp.route("/api/beneficiaries/one", methods=["PUT"])
def update_beneficiary():
    ben_id = request.args.get("id")
    name = request.args.get("name")
    if not ben_id or not name:
        return jsonify(ok=False, error="id and name query params required"), 400
    body = request.get_json(silent=True) or {}
    # Updatable columns = everything except the two PK parts.
    fields = [c for c in COLUMNS if c not in ("BeneficiaryID", "BenF_Name") and c in body]
    if not fields:
        return jsonify(ok=False, error="No fields to update"), 400
    set_clause = ", ".join(f"{c} = %s" for c in fields)
    values = [body[c] for c in fields] + [ben_id, name]
    try:
        affected = execute(
            f"UPDATE beneficiary SET {set_clause} WHERE BeneficiaryID = %s AND BenF_Name = %s",
            values,
        )
        if affected == 0:
            return jsonify(ok=False, error="Beneficiary not found"), 404
        row = query_one(
            "SELECT * FROM beneficiary WHERE BeneficiaryID = %s AND BenF_Name = %s",
            (ben_id, name),
        )
        return jsonify(ok=True, data=row)
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503


@beneficiaries_bp.route("/api/beneficiaries/one", methods=["DELETE"])
def delete_beneficiary():
    ben_id = request.args.get("id")
    name = request.args.get("name")
    if not ben_id or not name:
        return jsonify(ok=False, error="id and name query params required"), 400
    try:
        affected = execute(
            "DELETE FROM beneficiary WHERE BeneficiaryID = %s AND BenF_Name = %s",
            (ben_id, name),
        )
        if affected == 0:
            return jsonify(ok=False, error="Beneficiary not found"), 404
        return jsonify(ok=True, data={"deleted": {"id": ben_id, "name": name}})
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503
