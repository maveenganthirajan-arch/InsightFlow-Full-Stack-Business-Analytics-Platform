import os
from flask import Flask, render_template
from config import config
from app.extensions import db, login_manager

def create_app(config_name='default'):
    """Application factory for InsightFlow."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Ensure required directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.root_path, '..', 'instance'), exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register Blueprints
    from app.auth import auth_bp
    from app.datasets import datasets_bp
    from app.analytics import analytics_bp
    from app.reports import reports_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(datasets_bp, url_prefix='/datasets')
    app.register_blueprint(analytics_bp)
    app.register_blueprint(reports_bp, url_prefix='/reports')

    # Global Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return render_template('413.html'), 413

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    return app
