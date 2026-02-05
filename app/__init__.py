from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from .extensions import limiter
from flasgger import Swagger
from flask_migrate import Migrate
from .errors import ServiceError
from .errorhandlers import set_error_handlers
import os

db = SQLAlchemy()
migrate = Migrate()

def register_extensions(app: Flask):
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    Swagger(app, template={...})

def register_services(app: Flask):
    from app.services import token_service
    token_service.init(
        app.config["ACCESS_TOKEN_SECRET"], 
        app.config["REFRESH_TOKEN_SECRET"]
    )

def register_blueprints(app):
    from app.routes import auth_bp, todo_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(todo_bp)

def create_app(config_class = 'app.config.Config') -> Flask:
    app = Flask(__name__)

    app.config.from_object(config_class)

    register_extensions(app)
    register_services(app)
    register_blueprints(app)
    set_error_handlers(app)

    return app
