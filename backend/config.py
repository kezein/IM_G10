"""
config.py
Loads all settings from the .env file so no secret (DB password, admin
password, session key) is ever hard-coded or committed to git.

Each teammate copies .env.example -> .env and fills in their own values.
"""
import os
from dotenv import load_dotenv

# Read the .env file in this folder into environment variables.
load_dotenv()


class Config:
    # --- MySQL connection settings ---
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "profriends_inc")

    # --- Portal admin login (buyers log in differently, see auth.py) ---
    ADMIN_USER = os.getenv("ADMIN_USER", "admin")
    ADMIN_PASS = os.getenv("ADMIN_PASS", "admin123")

    # --- Flask session signing key ---
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-key")
