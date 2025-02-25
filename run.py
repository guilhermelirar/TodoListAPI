from flask import jsonify
from app import create_app

if __name__ == '__main__':
    app = create_app()

    @app.route('/hello', methods=['GET'])
    def hello():
        return jsonify({
            "message" : "Hello World!"
        }), 200

    app.run(host='0.0.0.0', debug=True)
