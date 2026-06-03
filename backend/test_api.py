"""
test_api.py
A plain-Python smoke test (no testing framework). Start the server first
(`python app.py`), then in another terminal run `python test_api.py`.
It checks each endpoint and prints PASS / FAIL. It creates a temporary buyer
'B-TEST-001', edits it, then deletes it, so the database is left unchanged.
"""
import json
import urllib.request
import urllib.error

BASE = "http://localhost:5000"
passed = 0
failed = 0


def call(method, path, body=None):
    """Send an HTTP request and return (status_code, parsed_json)."""
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


def check(label, condition):
    global passed, failed
    if condition:
        passed += 1
        print(f"PASS - {label}")
    else:
        failed += 1
        print(f"FAIL - {label}")


# --- Health ---
status, body = call("GET", "/api/health")
check("health returns ok", status == 200 and body.get("ok") is True)

# --- Login (admin) ---
status, body = call("POST", "/api/login",
                    {"role": "admin", "username": "admin", "password": "admin123"})
check("admin login ok", status == 200 and body.get("ok") is True)

# --- Read buyers ---
status, body = call("GET", "/api/buyers")
check("list buyers ok", status == 200 and body.get("ok") and len(body["data"]) >= 5)

# --- Create temp buyer ---
new_buyer = {
    "BuyerID": "B-TEST-001", "BuyerName": "Test Person", "Birthdate": "1990-01-01",
    "Birthplace": "Test City", "GovID": "Passport", "TIN": "000-000-000-000",
    "Gender": "M", "Civil_Status": "S", "Address": "123 Test St",
    "Citizenship": "Filipino", "Gross_MonthlyIncome": 50000,
    "Mobile_Num": "09170000000", "Personal_Email": "test@test.com",
    "Account_Type": "Savings", "Bank_Name": "BDO",
}
status, body = call("POST", "/api/buyers", new_buyer)
check("create buyer ok", status == 200 and body.get("ok") is True)

# --- Update temp buyer ---
status, body = call("PUT", "/api/buyers/B-TEST-001", {"Bank_Name": "BPI"})
check("update buyer ok", status == 200 and body["data"]["Bank_Name"] == "BPI")

# --- Delete temp buyer (cleanup) ---
status, body = call("DELETE", "/api/buyers/B-TEST-001")
check("delete buyer ok", status == 200 and body.get("ok") is True)

# --- Report ---
status, body = call("GET", "/api/reports/q1")
check("report q1 ok", status == 200 and body.get("ok") is True)

print(f"\n{passed} passed, {failed} failed")
