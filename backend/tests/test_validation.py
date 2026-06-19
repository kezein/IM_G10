"""Plain-Python tests for routes/validation.py (run: python backend/tests/test_validation.py)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from routes.validation import is_valid_email, is_numeric, is_alpha_spaces, is_valid_tin, first_invalid

def check(name, cond):
    print(("PASS" if cond else "FAIL"), name)
    assert cond, name

# email
check("email ok", is_valid_email("a@b.com"))
check("email no-at", not is_valid_email("ab.com"))
check("email no-dot", not is_valid_email("a@bcom"))
check("email blank", not is_valid_email(""))
check("email none", not is_valid_email(None))
# numeric (digits only, optional decimal)
check("num int", is_numeric("12345"))
check("num decimal", is_numeric("123.45"))
check("num alpha", not is_numeric("12a45"))
check("num blank", not is_numeric(""))
# alpha + spaces
check("alpha ok", is_alpha_spaces("Bank Of Test"))
check("alpha digit", not is_alpha_spaces("Bank 1"))
# TIN: 12 digits total (9-digit TIN + 3-digit BIR branch), formatted XXX-XXX-XXX-XXX
check("tin dashed ok", is_valid_tin("123-456-789-000"))
check("tin raw 12 ok", is_valid_tin("123456789000"))
check("tin too short", not is_valid_tin("123-456-789"))
check("tin too long", not is_valid_tin("123-456-789-0001"))
check("tin alpha", not is_valid_tin("123-456-789-00a"))
check("tin blank", not is_valid_tin(""))
# first_invalid returns the field name or None
bad = first_invalid({"Personal_Email": "nope", "Mobile_Num": "0917"},
                    email_fields=["Personal_Email"], numeric_fields=["Mobile_Num"])
check("first_invalid finds email", bad == "Personal_Email")
good = first_invalid({"Personal_Email": "a@b.com", "Mobile_Num": "0917"},
                     email_fields=["Personal_Email"], numeric_fields=["Mobile_Num"])
check("first_invalid passes", good is None)
badtin = first_invalid({"TIN": "123"}, tin_fields=["TIN"])
check("first_invalid finds tin", badtin == "TIN")
oktin = first_invalid({"TIN": "123-456-789-000"}, tin_fields=["TIN"])
check("first_invalid tin passes", oktin is None)
print("ALL VALIDATION TESTS PASSED")
