# Profriends Inc — QA Findings & Fix List

**Owner:** Kezia (Backend Integration)
**Project:** IM_G10 — Information Management Final Project
**Purpose:** Working list of issues found during integration QA, ordered by priority. Used as context for Claude Code while fixing.

---

## How to use this with Claude Code

1. Open the whole `IM_G10` folder in VS Code.
2. Open the Claude Code panel and attach this file plus `README.md` and the design spec PDF for context.
3. Work through the sections **top to bottom** (data integrity first, cosmetic last).
4. Keep Claude in **Plan mode** and review each diff before accepting.
5. Tick the boxes as each item is verified fixed.

---

## 1. Data Integrity & Backend (highest priority — real bugs)

- 
[ ] **Spouse not saving.** Adding a spouse through the form does not insert into the `spouse` table. Likely the spouse insert isn't wired in the backend. *(Files: `routes/spouse.py`, `templates/index.html`)*
- [ ] **No address input on buyer registration.** The `buyer` table already has an `Address` column (`varchar(100)`), but the add-buyer form doesn't collect it, so it defaults to "N/A". Add the field to the form and wire it to the insert. *(Files: `templates/index.html`, `routes/buyers.py`)*
- [ ] **Loan placeholder values.** When a buyer applies for a loan, `OrPr_Num` saves as "Applied", `Booking_Officer` as "Pending Assignment", and there's no processing fee. These columns are `NOT NULL`, so the backend inserts placeholders. Decide on a clean approach: make those columns nullable (so they're genuinely empty until staff assign them), or add a proper loan-status field, or display the placeholders neatly (e.g. "—"). *(Files: `routes/loans.py`, schema)*
- [ ] **Inconsistent LoanID format.** Loan IDs should be auto-generated server-side in the consistent `L-YYYY-NNN` format the sample data uses. Users should never type the ID. *(File: `routes/loans.py`)*
- [ ] **Only one loan can be created.** The schema supports many loans per buyer (LoanID is PK, BuyerID is FK), so if the UI blocks a second loan, that's a frontend restriction to remove. *(File: `templates/index.html`)*
- [ ] **Beneficiary "relationship too long" error.** Entering "Daughter" throws a column-length error, but `Relationship` is `varchar(20)` and "Daughter" is only 8 characters — so something is off (live schema may differ, or the error is from another field). Reproduce, capture the exact error text, and fix. *(Files: schema, `routes/beneficiaries.py`)*
- [ ] **Delete behavior with new foreign keys.** After applying the FK patch (`database/profriends_inc(updated).sql`), deleting a buyer who still has a spouse/loan/employment/etc. is now BLOCKED by MySQL (FKs default to RESTRICT, no cascade). The delete feature must catch this error and show a friendly message instead of crashing. Decide whether delete should be blocked (force deleting children first) or cascade. *(Files: `routes/buyers.py`, `templates/index.html`)*

## 2. Input Validation

- [ ] **Email fields accept non-emails.** Add proper email-format validation on personal/work email inputs.
- [ ] **Number fields accept non-numbers.** Validate fields that should be numeric (income, fees, phone, etc.).
- [ ] **Bank Name accepts numbers.** Should accept letters/spaces only.
- [ ] **Apply validation consistently.** The account-creation form already shows "must follow…" notices — reuse that same pattern across all the other forms so validation is consistent. *(Files: `templates/index.html`, route files for server-side checks)*

## 3. Reports

- [ ] **Reports show bare numbers.** Clicking a report shows only a plain number with no detail. Add a drill-down view showing the underlying rows/details behind each report. *(Files: `templates/index.html`, `routes/reports.py`)*

## 4. UI / UX (all in `templates/index.html`)

- [ ] **Edit/Delete buttons too close.** Add spacing/gap between them.
- [ ] **Approve/Reject/Edit buttons too close.** Add spacing between all of them.
- [ ] **Delete uses the native browser dialog.** Replace the "localhost:5000 says…" `confirm()` box with a styled confirmation modal that matches the rest of the UI.
- [ ] **Show/hide password jitter.** The show/hide text jumps up and down rapidly on hover. Fix the CSS layout so it stays stable.
- [ ] **Beneficiaries display.** Beneficiaries render as raw "local user" text instead of proper cards/rows. Give them proper UI consistent with the rest of the portal.
- [ ] **Post-signup login instructions too short.** After creating an account, the explanation of how to log in is too brief to remember. Expand it (clearly state: username = BuyerID, password = last name) and make it persist/stay visible.

## 5. Design & Scope Clarifications (not bugs — confirm and document with Izy/Paul)

- [ ] **Civil status codes.** UI shows single letters. Per the data dictionary: S=Single, M=Married, D=Divorced, **P=Separated**, W=Widowed. Show full words in the dropdown instead of codes. NOTE: the manual form and the data dictionary disagree (form lists Single/Married/Separated/Widower with no Divorced; dictionary lists 5 with Divorced) — reconcile.
- [ ] **Admin "Add Property" has no table.** Properties are frontend-only sample data by design (per README); there is no property table in the schema. Either hide/remove the admin "Add Property" button or label it clearly as out-of-scope so it doesn't look broken.
- [ ] **Design-vs-build mismatches** (reconcile the documentation with the actual database):
  - `buyer.Address` exists in the SQL but is not in the design data dictionary or ERD.
  - `beneficiary` uses a **composite primary key** (`BeneficiaryID` + `BenF_Name`) in the build, but the design says PK is `BeneficiaryID` alone. This was needed so one BeneficiaryID can list multiple people — update the doc.
  - The ERD shows a `SpouseID` primary key for Spouse, but neither the dictionary nor the SQL has it (`BuyerID` is the PK). Fix the ERD.
  - `Birthplace` is `varchar(100)` in the build vs `varchar(50)` in the dictionary.

---

## Known limitations (by design — do NOT file as bugs)

- Loan status (Pending/Active/Approved) is not persisted (no column).
- Properties and Payments are frontend-only sample data, not in the database.
- "Create Account" password is ignored — buyers log in with BuyerID + last name.
