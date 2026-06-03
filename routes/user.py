from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from models.loan import Loan
from extensions import db
from datetime import datetime

user_bp = Blueprint("user", __name__, url_prefix="/user")


# ────────────────────────────────────────────────────────────────
# HELPERS
# ────────────────────────────────────────────────────────────────

def _get_interest_rate(tenure_months: int) -> float:
    """Dynamic annual interest rate based on tenure."""
    if tenure_months <= 12:
        return 7.5
    elif tenure_months <= 36:
        return 8.5
    else:
        return 9.5


def _calc_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """Standard amortisation EMI formula."""
    r = annual_rate / 12 / 100          # monthly rate
    n = tenure_months
    if r == 0:
        return principal / n
    emi = principal * r * (1 + r) ** n / ((1 + r) ** n - 1)
    return round(emi, 2)


# ────────────────────────────────────────────────────────────────
# USER DASHBOARD
# ────────────────────────────────────────────────────────────────
@user_bp.route("/dashboard")
@login_required
def dashboard():
    loans = (
        Loan.query
        .filter_by(user_id=current_user.id)
        .order_by(Loan.created_at.desc())
        .all()
    )
    return render_template("user/dashboard.html", loans=loans)


@user_bp.route("/")
@login_required
def dashboard_redirect():
    return redirect(url_for("user.dashboard"))


# ────────────────────────────────────────────────────────────────
# APPLY FOR LOAN
# ────────────────────────────────────────────────────────────────
@user_bp.route("/apply", methods=["POST"])
@login_required
def apply_loan():
    try:
        amount  = float(request.form.get("amount") or "0")
        tenure  = int(request.form.get("tenure") or "0")
        income  = float(request.form.get("income") or "0")
    except (TypeError, ValueError):
        flash("Invalid input. Please check your entries.", "error")
        return redirect(url_for("user.dashboard"))

    purpose    = request.form.get("purpose", "Personal")
    collateral = request.form.get("collateral", "").strip()

    # ── Validation ─────────────────────────────────────────────
    if amount <= 0 or tenure <= 0:
        flash("Amount and tenure must be positive.", "error")
        return redirect(url_for("user.dashboard"))

    if amount > 1_00_00_000:
        flash("Loan amount exceeds the allowed limit of ₹1 Crore.", "error")
        return redirect(url_for("user.dashboard"))

    if tenure > 60:
        flash("Tenure cannot exceed 60 months (5 years).", "error")
        return redirect(url_for("user.dashboard"))

    # ── Financial mechanics ─────────────────────────────────────
    interest_rate  = _get_interest_rate(tenure)
    emi            = _calc_emi(amount, interest_rate, tenure)
    total_repay    = round(emi * tenure, 2)
    total_interest = round(total_repay - amount, 2)

    # ── Save ────────────────────────────────────────────────────
    loan = Loan(
        user_id           = current_user.id,
        borrower          = current_user.username,
        amount            = amount,
        tenure            = tenure,
        status            = "Pending",
        created_at        = datetime.utcnow(),
        interest_rate     = interest_rate,
        emi               = emi,
        total_interest    = total_interest,
        remaining_balance = total_repay,
        purpose           = purpose,
        income            = income,
        collateral        = collateral,
    )

    db.session.add(loan)
    db.session.commit()

    flash(
        f"Loan application submitted! EMI: ₹{emi:,.2f}/month at {interest_rate}% p.a.",
        "success",
    )
    return redirect(url_for("user.dashboard"))


# ────────────────────────────────────────────────────────────────
# MAKE EMI REPAYMENT
# ────────────────────────────────────────────────────────────────
@user_bp.route("/repay/<int:loan_id>", methods=["POST"])
@login_required
def repay_loan(loan_id):
    loan = Loan.query.filter_by(id=loan_id, user_id=current_user.id).first_or_404()

    if loan.status != "Approved":
        return jsonify({"error": "Only approved loans can be repaid."}), 400

    if loan.remaining_balance <= 0:
        return jsonify({"error": "This loan is already fully paid off."}), 400

    # Deduct one EMI instalment
    loan.remaining_balance = max(0.0, round(loan.remaining_balance - loan.emi, 2))

    if loan.remaining_balance <= 0:
        loan.status = "Paid Off"
        user = current_user._get_current_object()
        if user and hasattr(user, "credit_score"):
            user.credit_score = min(850, getattr(user, "credit_score", 700) + 25)

    db.session.commit()

    total_repay = round(loan.emi * loan.tenure, 2)
    pct_paid    = round((total_repay - loan.remaining_balance) / total_repay * 100, 1) if total_repay else 100

    return jsonify({
        "success":           True,
        "remaining_balance": loan.remaining_balance,
        "pct_paid":          pct_paid,
        "status":            loan.status,
        "credit_score":      current_user.credit_score,
    })


# ────────────────────────────────────────────────────────────────
# DELETE LAST LOAN
# ────────────────────────────────────────────────────────────────
@user_bp.route("/delete-last-loan", methods=["POST"])
@login_required
def delete_last_loan():
    last_loan = (
        Loan.query
        .filter_by(user_id=current_user.id)
        .order_by(Loan.created_at.desc())
        .first()
    )

    if not last_loan:
        flash("No loan history to delete.", "warning")
        return redirect(url_for("user.dashboard"))

    if last_loan.status in ("Approved", "Paid Off"):
        flash("Active or paid-off loans cannot be deleted.", "error")
        return redirect(url_for("user.dashboard"))

    db.session.delete(last_loan)
    db.session.commit()
    flash("Last loan application deleted.", "success")
    return redirect(url_for("user.dashboard"))


# ────────────────────────────────────────────────────────────────
# LOANS API (polling / refresh)
# ────────────────────────────────────────────────────────────────
@user_bp.route("/loans")
@login_required
def user_loans_api():
    loans = (
        Loan.query
        .filter_by(user_id=current_user.id)
        .order_by(Loan.created_at.desc())
        .all()
    )

    result = []
    for loan in loans:
        total_repay = round(loan.emi * loan.tenure, 2) if loan.emi else 0
        pct_paid    = (
            round((total_repay - loan.remaining_balance) / total_repay * 100, 1)
            if total_repay and total_repay > 0 else 0
        )
        result.append({
            "id":                loan.id,
            "amount":            float(loan.amount),
            "tenure":            loan.tenure,
            "status":            loan.status,
            "created_at":        loan.created_at.isoformat(),
            "interest_rate":     loan.interest_rate,
            "emi":               float(loan.emi or 0),
            "total_interest":    float(loan.total_interest or 0),
            "remaining_balance": float(loan.remaining_balance or 0),
            "pct_paid":          pct_paid,
            "purpose":           loan.purpose,
            "remarks":           loan.remarks or "",
        })

    return jsonify(result)
