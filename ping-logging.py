import flask
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/ping', methods=['GET'])
def ping():
    app.logger.info('Ping Pong')
    return jsonify({"message": "pong"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

