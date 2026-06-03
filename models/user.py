from flask_login import UserMixin
from extensions import db, login_manager

class User(db.Model, UserMixin):
    id           = db.Column(db.Integer, primary_key=True)
    username     = db.Column(db.String(100), unique=True, nullable=False)
    password     = db.Column(db.String(200), nullable=False)
    role         = db.Column(db.String(20), default="user")
    credit_score = db.Column(db.Integer, default=700)

    # Cascade: deleting a user removes all their loans
    loans = db.relationship(
        "Loan",
        backref="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
