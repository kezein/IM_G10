"""
auth.py
Login for two kinds of users:
  - Admin: matches the ADMIN_USER / ADMIN_PASS from .env.
  - Buyer: matches a BuyerID + the buyer's last name found in the buyer table.
On success we store who they are in the Flask session (a signed cookie).

No new database table is needed. Buyer "password" = last word of BuyerName
(simple/demo-grade, agreed in the design spec).
"""
from flask import Blueprint, request, jsonify, session
from config import Config
from db import query_one

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/login", methods=["POST"])
def login():
    body = request.get_json(silent=True) or {}
    role = body.get("role")          # "admin" or "buyer"
    username = body.get("username")  # admin user, or BuyerID for buyers
    password = body.get("password")  # admin pass, or last name for buyers

    if not role or not username or not password:
        return jsonify(ok=False, error="role, username and password are required"), 400

    if role == "admin":
        if username == Config.ADMIN_USER and password == Config.ADMIN_PASS:
            session["role"] = "admin"
            session["user_id"] = "admin"
            return jsonify(ok=True, data={"role": "admin", "name": "Administrator"})
        return jsonify(ok=False, error="Invalid admin credentials"), 401

    if role == "buyer":
        # Look the buyer up by ID, then check the last name matches.
        buyer = query_one(
            "SELECT BuyerID, BuyerName FROM buyer WHERE BuyerID = %s",
            (username,),
        )
        if buyer is None:
            return jsonify(ok=False, error="Buyer ID not found"), 401
        last_name = buyer["BuyerName"].strip().split()[-1].lower()
        if password.strip().lower() == last_name:
            session["role"] = "buyer"
            session["user_id"] = buyer["BuyerID"]
            return jsonify(ok=True, data={"role": "buyer", "name": buyer["BuyerName"]})
        return jsonify(ok=False, error="Invalid buyer credentials"), 401

    return jsonify(ok=False, error="Unknown role"), 400


@auth_bp.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify(ok=True, data={"loggedOut": True})


@auth_bp.route("/api/me", methods=["GET"])
def me():
    """Tell the frontend who (if anyone) is logged in."""
    if "role" not in session:
        return jsonify(ok=False, error="Not logged in"), 401
    return jsonify(ok=True, data={"role": session["role"], "user_id": session["user_id"]})
