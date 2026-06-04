# Profriends Inc — QA Findings Fix Campaign Design

**Date:** 2026-06-04
**Author:** Kezia (QA / Backend Integration)
**Subject:** Information Management — Final Project
**Source:** `docs/superpowers/QA_findings.md`
**Branch:** `qa-fixes` (off `main`)

---

## 1. Purpose

Work through the QA findings list as a single coordinated campaign rather than ad-hoc
one-off edits. This spec records the decisions made during brainstorming so the
implementation plan (and any parallel agents) execute against a fixed, agreed target.

## 2. Ground rules / constraints (decided)

- **No schema changes.** Izy's `database/profriends_inc.sql` and the FK patch
  `database/profriends_inc(updated).sql` stay as-is. Findings that *could* be solved with a
  schema change (1.3 loan placeholders, 1.7 delete-with-FK) are solved in the
  backend + frontend only. This keeps the multi-person repo safe and requires no re-import.
- **Scope this round:** Sections 1, 2, 3, 4 and the *code* parts of Section 5 (5.1, 5.2).
  The pure-documentation mismatches (5.3) get a written reconciliation note for Izy/Paul —
  no code, no doc edits to teammates' deliverables.
- **Validation depth:** client-side validation is the primary fix (reuse the existing
  "must follow…" pattern), backed by **light server-side guards** (email format, numeric)
  as defense-in-depth.
- **Reports drill-down UX:** inline expanding detail table under the report number
  (not a modal).
- **Verification is manual.** This environment has no live MySQL connection, so agents
  cannot self-verify against the DB. Each fix is verified by the user running the app
  (admin + buyer flows) and confirming behavior — consistent with the project's existing
  testing approach. Diffs are reviewed per lane before merge.

## 3. Execution strategy — three lanes (Approach B)

The entire frontend is a single ~1900-line file (`backend/templates/index.html`) that nearly
every finding touches. Concurrent edits to it would clobber each other. Backend route files
are cleanly separated. So work splits by **file ownership**:

- **Lane 1 — Backend (parallel, isolated):** `routes/loans.py` and the delete routes in
  `routes/spouse.py`, `employment.py`, `household.py`, plus a small shared
  server-side validation helper. Touches only `backend/routes/*.py` and `backend/db.py`-adjacent
  helpers. No overlap with the frontend file.
  - **`beneficiaries.py` is owned by Lane 3, not Lane 1.** Because finding 1.6 (investigate)
    and finding 1.7 (beneficiary-delete error handling) both edit `beneficiaries.py`, a single
    owner makes both changes there to avoid two lanes clobbering one file.
- **Lane 2 — Frontend (sequential, single owner):** everything in `index.html`.
- **Lane 3 — Investigation + docs (parallel):** reproduce finding 1.6 before fixing, then make
  both the 1.6 fix and the 1.7 beneficiary-delete error handling in `beneficiaries.py` (sole
  owner of that file); write the 5.3 reconciliation note.

Lanes 1 and 3-investigation run concurrently with Lane 2. Each lane's diff is reviewed before
merge into `qa-fixes`.

> **Note on parallelism:** the genuinely-parallel backend workload is modest (mostly `loans.py`
> plus delete-route error handling). Most effort is the sequential frontend lane. This is
> expected and acceptable — the value of the split is protecting the single frontend file from
> concurrent-edit clobbering, not maximizing agent count.

## 4. Per-finding design

### Section 1 — Data integrity

- **1.1 Spouse not saving — DONE.** Backend `routes/spouse.py` now coerces blank/whitespace
  strings to SQL `NULL` (`_nullify` helper) in create + update, so the optional `Sps_Bdate`
  DATE column no longer receives `''` (which MySQL strict mode rejected). Frontend now checks
  the spouse-insert response instead of swallowing the error.
- **1.2 Address on buyer registration — DONE.** `Address` field added to the register form,
  the admin "Add Buyer" modal, and the "Edit Buyer" modal; wired into each buyer object and
  the client-side required checks. (Backend already had `Address` in `COLUMNS`/`REQUIRED`.)
- **1.3 Loan placeholder values — backend + frontend.**
  - Backend (`loans.py`): stop *requiring* the staff-assigned columns
    (`OrPr_Num`, `OrPr_Date`, `Booking_Officer`, `ProcessingFee`). On a buyer-submitted
    application, insert neutral defaults so the NOT-NULL insert still succeeds:
    `OrPr_Num=''`, `Booking_Officer=''`, `ProcessingFee=0`, `OrPr_Date`=application date.
  - Frontend: render these neutral/empty values as **"—"** wherever loan details display.
  - No schema change; loan-status persistence remains a documented known-limitation.
- **1.4 Inconsistent LoanID format — backend + frontend.**
  - Backend (`loans.py`): if the request omits `LoanID`, auto-generate `L-YYYY-NNN`
    server-side. Strategy: `YYYY` = current year; `NNN` = (max existing numeric suffix) + 1,
    zero-padded to 3. Remove `LoanID` from the client-supplied `REQUIRED` set.
  - Frontend: remove the LoanID input; never let the user type it.
- **1.5 Only one loan can be created — frontend.** Remove the UI guard that blocks a second
  loan. Schema already allows many loans per buyer (LoanID PK, BuyerID FK).
- **1.6 Beneficiary "relationship too long" — investigate first, then fix.**
  Schema is `Relationship varchar(20)`; "Daughter" is 8 chars, so the reported error does not
  match this schema. Use systematic-debugging: reproduce, capture the *exact* error text and
  the request body, identify the real cause (candidates: a mis-mapped field writing into a
  shorter column; an auto-generated `BeneficiaryID` exceeding `varchar(15)`; a live schema that
  differs from the dump). Fix the actual cause. Likely spans `beneficiaries.py` and the
  beneficiary form in `index.html`; assign once the cause is known.
- **1.7 Delete behavior with new FKs — backend + frontend.**
  - `buyers.py` already catches `IntegrityError` → friendly message; keep.
  - Add explicit `IntegrityError` handling (409 + plain-English message) to the delete routes
    that currently only catch generic `MySQLError`: `spouse.py`, `employment.py`,
    `household.py`, and `loans.py` as applicable (Lane 1); `beneficiaries.py` is handled with
    1.6 in Lane 3.
  - Behavior: **block** the delete (no cascade); message tells the user to remove the
    referencing child records first.
  - Frontend: pairs with the styled confirm modal (4.3).

### Section 2 — Input validation (client + light server-side)

- Client-side: reuse the existing "must follow…" notice pattern across all forms.
  - **2.1 Email** fields (personal/work, employer, spouse) — validate email format.
  - **2.2 Numeric** fields (income, fees, phone, TIN, tenure) — digits only / numeric.
  - **2.3 Bank Name** — letters and spaces only (no digits).
  - **2.4 Consistency** — apply the same notice/validation styling everywhere.
- Server-side (light, shared): a small helper used by the relevant routes to reject malformed
  email and non-numeric numeric fields with a 400 naming the bad field. Defense-in-depth only;
  the client remains the primary UX.

### Section 3 — Reports (frontend-only)

Backend `/api/reports/q<n>` already returns `{ description, rows: [...] }`. The UI currently
shows only a count. Render the returned `rows` as an **inline expanding detail table** beneath
each report, with a row-count summary. No backend change.

### Section 4 — UI / UX (frontend, `index.html`)

- **4.1** Add spacing/gap between Edit/Delete buttons.
- **4.2** Add spacing between Approve/Reject/Edit buttons.
- **4.3** Replace native `confirm()` with a styled confirmation modal matching the UI
  (used by all destructive actions, ties into 1.7).
- **4.4** Fix show/hide password jitter — stabilize the toggle's layout so it doesn't jump on
  hover (reserve space / absolute-position the toggle).
- **4.5** Render beneficiaries as proper cards/rows instead of raw "local user" text.
- **4.6** Expand the post-signup login instructions and make them persist: clearly state
  username = BuyerID, password = last name.

### Section 5 — Design & scope clarifications

- **5.1 Civil status codes — frontend.** Show full words in dropdowns
  (S=Single, M=Married, D=Divorced, P=Separated, W=Widowed). Reconcile the form-vs-dictionary
  disagreement by following the data dictionary's 5 values (including Divorced). The stored
  value stays the single-letter code the DB uses; only the label changes.
- **5.2 Add Property — frontend.** Properties are frontend-only by design (no table). Label the
  admin "Add Property" control clearly as out-of-scope / sample-data (or hide it) so it doesn't
  look broken.
- **5.3 Design-vs-build mismatches — documentation note only.** Produce a short written note for
  Izy/Paul listing: `buyer.Address` missing from dictionary/ERD; `beneficiary` composite PK
  (`BeneficiaryID` + `BenF_Name`) vs doc's single PK; ERD's phantom `SpouseID`; `Birthplace`
  `varchar(100)` build vs `varchar(50)` dict. No code, no edits to teammates' docs.

## 5. Known limitations (carried forward — NOT bugs)

- Loan status (Pending/Active/Approved) is not persisted (no column).
- Properties and Payments are frontend-only sample data, not in the database.
- "Create Account" password is ignored — buyers log in with BuyerID + last name.

## 6. Testing / verification

- Per fix, the user runs the app and exercises the relevant admin + buyer flow, confirming the
  behavior and DB persistence where applicable.
- `backend/test_api.py` smoke test remains the automated baseline for endpoint health.
- Each lane's diff is reviewed before merging into `qa-fixes`.
