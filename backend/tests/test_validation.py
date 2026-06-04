"""Plain-Python tests for routes/validation.py (run: python backend/tests/test_validation.py)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from routes.validation import is_valid_email, is_numeric, is_alpha_spaces, first_invalid

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
# first_invalid returns the field name or None
bad = first_invalid({"Personal_Email": "nope", "Mobile_Num": "0917"},
                    email_fields=["Personal_Email"], numeric_fields=["Mobile_Num"])
check("first_invalid finds email", bad == "Personal_Email")
good = first_invalid({"Personal_Email": "a@b.com", "Mobile_Num": "0917"},
                     email_fields=["Personal_Email"], numeric_fields=["Mobile_Num"])
check("first_invalid passes", good is None)
print("ALL VALIDATION TESTS PASSED")
