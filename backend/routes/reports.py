"""
reports.py
Read-only reporting endpoint. Runs the 10 queries written by Izy (see
database/profriends_inc_queries.sql) and returns the rows as JSON for the
Inventory / Reports page.

GET /api/reports          -> list of available reports (number + description)
GET /api/reports/q<n>     -> rows for report n (1..10)
"""
from flask import Blueprint, jsonify
from mysql.connector import Error as MySQLError
from db import query_all

reports_bp = Blueprint("reports", __name__)

# Each entry: number -> (human description, SQL). SQL copied from Izy's file.
REPORTS = {
    1: ("Filipino buyers: id, name, citizenship",
        "SELECT BuyerID, BuyerName, Citizenship FROM buyer WHERE Citizenship = 'Filipino'"),
    2: ("Buyers born in Manila: name, gender, civil status",
        "SELECT BuyerName, Gender, Civil_Status FROM buyer WHERE Birthplace LIKE '%Manila%'"),
    3: ("Beneficiaries born 2016-2020",
        "SELECT * FROM beneficiary WHERE YEAR(BenF_Bdate) BETWEEN 2016 AND 2020"),
    4: ("Married buyers, income 50k-90k",
        "SELECT BuyerName, Gender, Civil_Status, Gross_MonthlyIncome FROM buyer "
        "WHERE (Gross_MonthlyIncome BETWEEN 50000 AND 90000) AND Civil_Status = 'M'"),
    5: ("Finance types with avg loan > 1,000,000",
        "SELECT Finance_Type, AVG(LoanAmount) AS avg_loan_amount FROM loan "
        "GROUP BY Finance_Type HAVING AVG(LoanAmount) > 1000000"),
    6: ("Total gross income per bank (high to low)",
        "SELECT Bank_Name, SUM(Gross_MonthlyIncome) AS total_income FROM buyer "
        "GROUP BY Bank_Name ORDER BY total_income DESC"),
    7: ("Length of stay by home ownership (avg > 3 yrs)",
        "SELECT MAX(Length_ofStay) AS stay_length, AVG(Length_ofStay) AS avg_stay, "
        "Home_Ownership FROM household WHERE Length_ofStay >= 2 "
        "GROUP BY Home_Ownership HAVING AVG(Length_ofStay) > 3"),
    8: ("Buyer count per employment type (single/married, tenure >= 4)",
        "SELECT Emp_Type, COUNT(*) AS total_buyers FROM employment e "
        "JOIN buyer b ON e.BuyerID = b.BuyerID "
        "WHERE b.Civil_Status IN ('M','S') AND e.Tenure >= 4 GROUP BY Emp_Type"),
    9: ("Loans term > 5 yrs with yearly payment > 200k",
        "SELECT b.BuyerName, l.Finance_Type, l.LoanAmount, l.Loan_Term, "
        "(l.LoanAmount / l.Loan_Term) AS yearly_payment "
        "FROM buyer b JOIN loan l ON b.BuyerID = l.BuyerID "
        "WHERE l.Loan_Term > 5 AND (l.LoanAmount / l.Loan_Term) > 200000"),
    10: ("Buyers with > 1 beneficiary (youngest bdate)",
         "SELECT b.BuyerName, COUNT(be.BeneficiaryID) AS total_beneficiaries, "
         "MAX(be.BenF_Bdate) AS youngest_beneficiary_bdate "
         "FROM buyer b JOIN beneficiary be ON b.BuyerID = be.BuyerID "
         "GROUP BY b.BuyerName HAVING COUNT(be.BeneficiaryID) > 1 "
         "ORDER BY total_beneficiaries DESC"),
}


@reports_bp.route("/api/reports", methods=["GET"])
def list_reports():
    """Return the menu of available reports."""
    menu = [{"number": n, "description": desc} for n, (desc, _sql) in sorted(REPORTS.items())]
    return jsonify(ok=True, data=menu)


@reports_bp.route("/api/reports/q<int:number>", methods=["GET"])
def run_report(number):
    if number not in REPORTS:
        return jsonify(ok=False, error=f"No report #{number} (valid: 1-10)"), 404
    description, sql = REPORTS[number]
    try:
        rows = query_all(sql)
        return jsonify(ok=True, data={"description": description, "rows": rows})
    except MySQLError as e:
        return jsonify(ok=False, error=f"Database error: {e}"), 503
