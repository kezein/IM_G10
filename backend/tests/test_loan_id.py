"""Plain-Python tests for next_loan_id (run: python backend/tests/test_loan_id.py)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from routes.loans import next_loan_id

def check(name, cond):
    print(("PASS" if cond else "FAIL"), name); assert cond, name

check("empty -> 001", next_loan_id([], 2026) == "L-2026-001")
check("increments", next_loan_id(["L-2026-001", "L-2026-002"], 2026) == "L-2026-003")
check("ignores other years", next_loan_id(["L-2025-009"], 2026) == "L-2026-001")
check("ignores junk", next_loan_id(["", None, "garbage"], 2026) == "L-2026-001")
check("pads to 3", next_loan_id(["L-2026-010"], 2026) == "L-2026-011")
print("ALL LOAN ID TESTS PASSED")
