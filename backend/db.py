"""
db.py
One place for talking to MySQL. Other files import these helpers instead of
opening their own connections. Every helper opens a connection, runs the SQL,
and always closes the connection (even if an error happens).

All SQL passed in uses %s placeholders so values are sent separately from the
query text -> this prevents SQL injection.
"""
import mysql.connector
from mysql.connector import Error
from config import Config


def get_connection():
    """Open and return a new MySQL connection using the .env settings."""
    return mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
    )


def query_all(sql, params=None):
    """Run a SELECT and return ALL rows as a list of dicts."""
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)   # dictionary=True -> rows come back as dicts
        cur.execute(sql, params or ())
        return cur.fetchall()
    finally:
        conn.close()


def query_one(sql, params=None):
    """Run a SELECT and return the FIRST row as a dict, or None if no rows."""
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        return cur.fetchone()
    finally:
        conn.close()


def execute(sql, params=None):
    """
    Run an INSERT / UPDATE / DELETE. Commits the change and returns how many
    rows were affected. Raises mysql.connector.Error on DB problems so the
    route can turn it into a clean JSON error.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()
