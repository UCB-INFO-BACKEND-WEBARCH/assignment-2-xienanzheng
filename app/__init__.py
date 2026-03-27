from flask import Flask

from .config import Config
from .extensions import db, migrate
from .routes.tasks import tasks_bp
from .routes.categories import categories_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(tasks_bp)
    app.register_blueprint(categories_bp)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
