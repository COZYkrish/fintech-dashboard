from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models.loan import Loan
from extensions import db
from sqlalchemy import func

analytics_bp = Blueprint(
    "analytics",
    __name__,
    url_prefix="/admin/analytics"
)

# -------------------------------
# Analytics Dashboard Page
# -------------------------------
@analytics_bp.route("/")
@login_required
def dashboard():
    if current_user.role != "admin":
        return "Unauthorized", 403

    total_loans = Loan.query.count()
    approved = Loan.query.filter_by(status="Approved").count()
    pending = Loan.query.filter_by(status="Pending").count()
    rejected = Loan.query.filter_by(status="Rejected").count()

    total_amount = db.session.query(
        func.coalesce(func.sum(Loan.amount), 0)
    ).scalar()

    return render_template(
        "admin/analytics.html",
        total_loans=total_loans,
        approved=approved,
        pending=pending,
        rejected=rejected,
        total_amount=total_amount
    )


# -------------------------------
# Chart Data API
# -------------------------------
@analytics_bp.route("/chart-data")
@login_required
def chart_data():
    if current_user.role != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    # Loan status counts
    status_data = {
        "Approved": Loan.query.filter_by(status="Approved").count(),
        "Pending": Loan.query.filter_by(status="Pending").count(),
        "Rejected": Loan.query.filter_by(status="Rejected").count(),
    }

    # SQLite-safe monthly grouping
    monthly_data = (
        db.session.query(
            func.strftime("%Y-%m", Loan.created_at),
            func.count(Loan.id)
        )
        .group_by(func.strftime("%Y-%m", Loan.created_at))
        .order_by(func.strftime("%Y-%m", Loan.created_at))
        .all()
    )

    return jsonify({
        "status": status_data,
        "monthly": {
            "labels": [row[0] for row in monthly_data],
            "values": [row[1] for row in monthly_data]
        }
    })

