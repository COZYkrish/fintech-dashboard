from flask import Blueprint, render_template, jsonify, redirect, url_for, request
from flask_login import login_required, current_user
from models.loan import Loan
from models.user import User
from extensions import db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ────────────────────────────────────────────────────────────────
# ADMIN DASHBOARD
# ────────────────────────────────────────────────────────────────
@admin_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != "admin":
        return "Unauthorized", 403

    loans = (
        Loan.query
        .order_by(Loan.created_at.desc())
        .all()
    )
    return render_template("admin/dashboard.html", loans=loans)


@admin_bp.route("/")
@login_required
def dashboard_redirect():
    return redirect(url_for("admin.dashboard"))


# ────────────────────────────────────────────────────────────────
# UPDATE LOAN STATUS  (now accepts remarks + adjusts credit score)
# ────────────────────────────────────────────────────────────────
@admin_bp.route("/update-status/<int:loan_id>/<status>", methods=["POST"])
@login_required
def update_status(loan_id, status):
    if current_user.role != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    if status not in ("Approved", "Rejected"):
        return jsonify({"error": "Invalid status"}), 400

    loan = db.get_or_404(Loan, loan_id)

    # Grab optional remarks from JSON body or form data
    data    = request.get_json(silent=True) or {}
    remarks = data.get("remarks", "").strip()

    loan.status  = status
    loan.remarks = remarks

    # Credit-score side-effect on rejection
    if status == "Rejected":
        borrower = db.session.get(User, loan.user_id)
        if borrower:
            borrower.credit_score = max(300, borrower.credit_score - 10)

    # On Approval ensure remaining_balance is populated for old loans (emi=0 guard)
    if status == "Approved" and loan.remaining_balance == 0 and loan.emi > 0:
        loan.remaining_balance = round(loan.emi * loan.tenure, 2)

    db.session.commit()

    # Return updated credit score so the UI can refresh
    borrower        = db.session.get(User, loan.user_id)
    new_score       = borrower.credit_score if borrower else None

    return jsonify({
        "success":      True,
        "loan_id":      loan.id,
        "status":       loan.status,
        "credit_score": new_score,
    })
