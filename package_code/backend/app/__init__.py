from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

from .config import Config


db = SQLAlchemy()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    from .routes.auth import bp as auth_bp
    from .routes.courses import bp as courses_bp
    from .routes.kps import bp as kps_bp
    from .routes.prereqs import bp as prereqs_bp
    from .routes.resources import bp as resources_bp
    from .routes.assessments import bp as assessments_bp
    from .routes.learning_events import bp as learning_events_bp
    from .routes.mastery import bp as mastery_bp
    from .routes.paths import bp as paths_bp
    from .routes.strategy import bp as strategy_bp
    from .routes.export import bp as export_bp
    from .routes.users import bp as users_bp
    from .routes.stats import bp as stats_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(courses_bp, url_prefix="/api")
    app.register_blueprint(kps_bp, url_prefix="/api")
    app.register_blueprint(prereqs_bp, url_prefix="/api")
    app.register_blueprint(resources_bp, url_prefix="/api")
    app.register_blueprint(assessments_bp, url_prefix="/api")
    app.register_blueprint(learning_events_bp, url_prefix="/api")
    app.register_blueprint(mastery_bp, url_prefix="/api")
    app.register_blueprint(paths_bp, url_prefix="/api")
    app.register_blueprint(strategy_bp, url_prefix="/api")
    app.register_blueprint(export_bp, url_prefix="/api")
    app.register_blueprint(users_bp, url_prefix="/api")
    app.register_blueprint(stats_bp, url_prefix="/api")

    @app.route("/api/health")
    def health():
        return {"code": 0, "message": "ok", "data": "ok"}

    return app
