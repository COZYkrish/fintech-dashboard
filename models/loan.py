from extensions import db
from datetime import datetime


class Loan(db.Model):
    id                = db.Column(db.Integer, primary_key=True)
    # FK enforces referential integrity; cascade handled via User.loans relationship
    user_id           = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    borrower          = db.Column(db.String(100))
    amount            = db.Column(db.Float)
    tenure            = db.Column(db.Integer)           # months
    status            = db.Column(db.String(20), default="Pending")
    created_at        = db.Column(db.DateTime, default=datetime.utcnow)

    # ── Financial mechanics ──────────────────────────────────────────────────
    interest_rate     = db.Column(db.Float, default=8.5)   # annual %
    emi               = db.Column(db.Float, default=0.0)   # monthly EMI
    total_interest    = db.Column(db.Float, default=0.0)   # total interest payable
    remaining_balance = db.Column(db.Float, default=0.0)   # outstanding repayable amount

    # ── Application enrichment ───────────────────────────────────────────────
    purpose           = db.Column(db.String(50), default="Personal")
    income            = db.Column(db.Float, default=0.0)   # declared monthly income
    collateral        = db.Column(db.String(200), default="")

    # ── Admin feedback ───────────────────────────────────────────────────────
    remarks           = db.Column(db.String(300), default="")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
