from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from .extensions import limiter
from flasgger import Swagger
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class = 'app.config.Config') -> Flask:
    app = Flask(__name__)

    app.config.from_object(config_class)
    
    db.init_app(app)
    limiter.init_app(app)

    @app.route('/', methods=['GET'])
    @limiter.limit("1 per minute")
    def hello():
        return jsonify({
            "message": "Hello World!"
        }), 200

    @app.errorhandler(429)
    def too_many(e):
        return jsonify({
            "message": "Too many requests"
        }), 429
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({"message": "Internal Server Error"}), 500
    
    migrate.init_app(app, db)

    # Blueprints registration
    from app.routes import auth_bp, todo_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(todo_bp)

    # API documentation with Swagger
    Swagger(app, template={
        "info": {
            "title": "Todo List API",
            "version": "1.0.0"
        }
    })
        
    return app
