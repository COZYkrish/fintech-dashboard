from flask import Flask, redirect, url_for
from flask_login import current_user
from config import Config
from extensions import db, login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))


    login_manager.login_view = "auth.login"

    from routes.auth import auth_bp
    from routes.user import user_bp
    from routes.admin import admin_bp
    from routes.analytics import analytics_bp

    # -------------------------
    # Register blueprints
    # -------------------------
    # app.register_blueprint(auth_bp)
    # app.register_blueprint(user_bp)
    # app.register_blueprint(admin_bp)
    # app.register_blueprint(analytics_bp)

    # @app.route("/")
    # def home():
    #     if current_user.is_authenticated:
    #         if current_user.role == "admin":
    #             return redirect(url_for("admin.dashboard"))
    #         return redirect(url_for("user.dashboard"))
    #     return redirect(url_for("auth.login"))

    return app


# -------------------------
# Run app
# -------------------------
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
