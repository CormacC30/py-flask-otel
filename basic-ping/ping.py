import flask
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "pong"}), 200

# Do NOT use app.run(debug=True) as it causes Werkzeug reloader to fork
# after auto-instrumentation, preventing trace generation.
# Instead, use 'flask run' command in Dockerfile or deployment
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090)
