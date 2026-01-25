from flask import jsonify
from .errors import ServiceError

def set_error_handlers(app):
    @app.errorhandler(ServiceError)
    def service_error(e):
        return jsonify({
            "message": e.message
        }), e.status_code

    @app.errorhandler(429)
    def too_many(e):
        return jsonify({
            "message": "Too many requests"
        }), 429
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({"message": "Internal Server Error"}), 500
     