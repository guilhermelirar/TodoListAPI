from flask import Flask

def create_app(config_class = 'app.config.Config') -> Flask:
    app = Flask(__name__)
    
    app.config.from_object(config_class)
    
    return app
