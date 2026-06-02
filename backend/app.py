"""
app.py
Entry point. Builds the Flask app, registers every blueprint (one per
resource), serves the frontend, and defines shared JSON error responses so
the frontend always receives the same { ok, error } shape.

Run with:  python app.py   ->  http://localhost:5000
"""
from flask import Flask, jsonify, render_template
from mysql.connector import Error as MySQLError

from config import Config


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = Config.SECRET_KEY

    # --- Register blueprints ---
    # These are uncommented one at a time as each blueprint file is added
    # in later tasks (Task 2 = auth, Tasks 3-8 = CRUD, Task 9 = reports).
    from routes.auth import auth_bp
    from routes.buyers import buyers_bp
    from routes.spouse import spouse_bp
    from routes.beneficiaries import beneficiaries_bp
    from routes.employment import employment_bp
    from routes.household import household_bp
    from routes.loans import loans_bp
    from routes.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(buyers_bp)
    app.register_blueprint(spouse_bp)
    app.register_blueprint(beneficiaries_bp)
    app.register_blueprint(employment_bp)
    app.register_blueprint(household_bp)
    app.register_blueprint(loans_bp)
    app.register_blueprint(reports_bp)

    # --- Frontend: serve the wired copy of Andre's UI ---
    @app.route("/")
    def index():
        return render_template("index.html")

    # --- Health check: confirms the server AND the database are reachable ---
    @app.route("/api/health")
    def health():
        from db import query_one
        try:
            query_one("SELECT 1 AS ok")
            return jsonify(ok=True, data={"db": "connected"})
        except MySQLError as e:
            return jsonify(ok=False, error=f"Database unavailable: {e}"), 503

    # --- Shared error handlers: every error becomes clean JSON ---
    @app.errorhandler(404)
    def not_found(_):
        return jsonify(ok=False, error="Not found"), 404

    @app.errorhandler(500)
    def server_error(_):
        return jsonify(ok=False, error="Unexpected server error"), 500

    return app


if __name__ == "__main__":
    # debug=True auto-reloads on code changes while developing.
    create_app().run(host="0.0.0.0", port=5000, debug=True)
