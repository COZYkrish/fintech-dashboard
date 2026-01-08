from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from models.loan import Loan
from extensions import db
from datetime import datetime

user_bp = Blueprint("user", __name__, url_prefix="/user")


# ===============================
# USER DASHBOARD
# ===============================
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


# Optional: redirect /user → /user/dashboard
@user_bp.route("/")
@login_required
def dashboard_redirect():
    return redirect(url_for("user.dashboard"))


# ===============================
# APPLY FOR LOAN (FIXED LOGIC)
# ===============================
@user_bp.route("/apply", methods=["POST"])
@login_required
def apply_loan():
    try:
        amount = float(request.form.get("amount"))
        tenure = int(request.form.get("tenure"))
    except (TypeError, ValueError):
        flash("Invalid input", "error")
        return redirect(url_for("user.dashboard"))

    # -------- VALIDATION --------
    if amount <= 0 or tenure <= 0:
        flash("Amount and tenure must be positive", "error")
        return redirect(url_for("user.dashboard"))

    if amount > 1_00_00_000:  # 1 Crore limit
        flash("Loan amount exceeds allowed limit", "error")
        return redirect(url_for("user.dashboard"))

    if tenure > 60:  # 5 years max
        flash("Tenure cannot exceed 60 months", "error")
        return redirect(url_for("user.dashboard"))

    # -------- SAVE LOAN --------
    loan = Loan(
        user_id=current_user.id,
        borrower=current_user.username,
        amount=amount,
        tenure=tenure,
        status="Pending",
        created_at=datetime.utcnow()
    )

    db.session.add(loan)
    db.session.commit()

    flash("Loan application submitted successfully", "success")
    return redirect(url_for("user.dashboard"))


# ===============================
# DELETE LAST LOAN (NEW)
# ===============================
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
        flash("No loan history to delete", "warning")
        return redirect(url_for("user.dashboard"))

    # Optional safety: block deletion of approved loans
    if last_loan.status == "Approved":
        flash("Approved loans cannot be deleted", "error")
        return redirect(url_for("user.dashboard"))

    db.session.delete(last_loan)
    db.session.commit()

    flash("Last loan entry deleted", "success")
    return redirect(url_for("user.dashboard"))


# ===============================
# USER LOANS API (CLEAN DATA)
# ===============================
@user_bp.route("/loans")
@login_required
def user_loans_api():
    loans = (
        Loan.query
        .filter_by(user_id=current_user.id)
        .order_by(Loan.created_at.desc())
        .all()
    )

    return jsonify([
        {
            "id": loan.id,
            "amount": float(loan.amount),
            "tenure": loan.tenure,
            "status": loan.status,
            "created_at": loan.created_at.isoformat()
        }
        for loan in loans
    ])
