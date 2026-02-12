from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flasgger import Swagger

from .extensions import limiter
from .errorhandlers import set_error_handlers

db = SQLAlchemy()
migrate = Migrate()

def register_extensions(app: Flask):
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    Swagger(app, template={...})


def init_services(app: Flask):
    from app.services.auth_service import AccountService
    from app.services.task_service import TaskService
    from app.services.token_service import TokenService

    token_service = TokenService(
        db.session,
        app.config["ACCESS_TOKEN_SECRET"],
        app.config["REFRESH_TOKEN_SECRET"],
    )

    account_service = AccountService(db_session=db.session)
    task_service = TaskService(session=db.session)

    app.token_service = token_service
    app.account_service = account_service
    app.task_service = task_service

def register_blueprints(app: Flask):
    from app.routes.auth_routes import auth_bp
    from app.routes.task_routes import todo_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(todo_bp)


def create_app(config_class='app.config.Config') -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    register_extensions(app)
    register_blueprints(app)
    init_services(app)
    set_error_handlers(app)

    return app