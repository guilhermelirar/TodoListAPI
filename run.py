from flask import jsonify
from app import create_app

if __name__ == '__main__':
    app = create_app()

    @app.route('/hello', methods=['GET'])
    def hello():
        return jsonify({
            "message" : "Hello World!"
        }), 200

    app.run(debug=True)
