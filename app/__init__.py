from pathlib import Path
from flask import Flask, render_template
from config import Config
from app.extensions import db, csrf


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)

    # Ensure upload folder exists outside public static
    upload_path = Path(app.config["UPLOAD_FOLDER"])
    upload_path.mkdir(parents=True, exist_ok=True)

    # Register Blueprints
    from app.routes.main import main_bp
    from app.routes.analysis import analysis_bp
    from app.routes.reports import reports_bp
    from app.routes.history import history_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(analysis_bp, url_prefix="/analysis")
    app.register_blueprint(reports_bp, url_prefix="/reports")
    app.register_blueprint(history_bp, url_prefix="/history")

    # Security Headers
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    # Error Handlers
    register_error_handlers(app)

    # Create tables if not existing
    with app.app_context():
        db.create_all()

    return app


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template("errors/400.html"), 400

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return render_template("errors/413.html"), 413

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("errors/500.html"), 500
