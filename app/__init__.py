import os
from flask import Flask, render_template
from config import config_by_name
from app.extensions import db, login_manager, migrate, csrf
from app.catalog import food_image
from app.utils import time_left


def create_app(config_name="default"):
    app = Flask(__name__, instance_relative_config=True)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Load configuration
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Register Jinja globals and filters
    app.jinja_env.globals.update(food_image=food_image)
    app.jinja_env.filters["time_left"] = time_left

    # Register blueprints
    from app.main.routes import main_bp
    from app.auth.routes import auth_bp
    from app.donor.routes import donor_bp
    from app.receiver.routes import receiver_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(donor_bp, url_prefix="/donor")
    app.register_blueprint(receiver_bp, url_prefix="/receiver")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # Error handlers
    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    return app
